#!/usr/bin/env python3

import os
import sys
import unittest
import string
import time
import random
import subprocess
import socket
from zio import *  # NOQA


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def exec_script(self, script, *args, **kwargs):
        from zio import which
        py = which('python3') or which('python')
        self.assertNotEqual(py, None)
        return self.cmdline(
            ' '.join([py, '-u', os.path.join(os.path.dirname(sys.argv[0]), script)] + list(args)),
            **kwargs
        )

    def cmdline(self, cmd, **kwargs):
        print('')
        socat_exec = ',pty,stderr,ctty'
        if 'socat_exec' in kwargs:
            socat_exec = kwargs['socat_exec']
            del kwargs['socat_exec']
        io = zio(cmd, **kwargs)
        yield io
        io.close()
        print('"%s" exited: ' % cmd, io.exit_code)

        for _ in range(16):
            port = random.randint(31337, 65530)
            p = subprocess.Popen(['socat', 'TCP-LISTEN:%d' % port, 'exec:"' + cmd + '"' + socat_exec])
            time.sleep(0.2)
            if p.returncode:
                continue
            try:
                io = zio(('127.0.0.1', port), **kwargs)
                yield io
            except socket.error:
                continue
            io.close()
            p.terminate()
            p.wait()
            break

    def test_tty(self):
        print('')
        io = zio('tty')
        out = io.read()
        self.assertEqual(out.strip(), b'not a tty', repr(out))

        io = zio('tty', stdin=TTY)
        out = io.read()
        self.assertTrue(out.strip().startswith(b'/dev/'), repr(out))

    def test_attach_socket(self):
        print('')
        for _ in range(4):
            port = random.randint(31337, 65530)
            p = subprocess.Popen(
                ['socat',
                 'TCP-LISTEN:%d,crlf' % port,
                 'SYSTEM:"echo HTTP/1.0 200; echo Content-Type: text/plain; echo; echo Hello, zio;"']
            )
            time.sleep(0.2)
            if p.returncode:
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', port))
                line = b''
                while True:
                    c = s.recv(1)
                    if not c:
                        break
                    else:
                        line += c
                    if line.find(b'\n') > -1:
                        break
                assert line.rstrip() == b"HTTP/1.0 200", repr(line)

                io = zio(s)

                line = io.readline()
                self.assertEqual(line.rstrip(), b"Content-Type: text/plain", repr(line))
                line = io.readline()
                line = io.readline()

                self.assertEqual(line.rstrip(), b"Hello, zio", repr(line))

                io.end()
                io.close()
            except socket.error:
                continue
            p.terminate()
            for _ in range(10):
                r = p.poll()
                if r is not None:
                    break
                time.sleep(0.2)
            else:
                try:
                    p.kill()
                except:  # NOQA
                    pass
            break

    def test_tty_raw_out(self):
        s = []
        ans = []
        for i in range(10):
            r = random.randint(0, 1)
            s.append('%d%s' % (i, r and '\\r\\n' or '\\n'))
            ans.append(b'%d%s' % (i, r and b'\r\n' or b'\n'))
        ans = b''.join(ans)
        cmd = "printf '" + ''.join(s) + "'"
        io = zio(cmd, stdout=TTY_RAW)
        rd = io.read()
        io.close()
        self.assertEqual(rd, ans)

        unprintable = [bytes([c]) for c in range(256) if chr(c) not in string.printable]
        for i in range(10):
            random.shuffle(unprintable)

        from zio import which
        py = which('python3') or which('python')
        self.assertNotEqual(py, None)
        target = ' '.join(
            [py,
             '-u',
             os.path.join(
                 os.path.dirname(sys.argv[0]), 'myprintf.py'
             ),
             "'\\r\\n" + repr(b''.join(unprintable))[2:-1] + "\\n'"]
        )
        print(repr(target))
        io = zio(target, stdout=TTY_RAW, print_read=COLORED(REPR))
        rd = io.read()
        self.assertEqual(rd, b"\r\n" + b''.join(unprintable) + b"\n")

    def test_pipe_out(self):
        io = zio('uname', stdout=PIPE)
        r = io.read()
        io.close()
        self.assertEqual(r.strip(), os.uname()[0].encode('utf-8'))

    # ---- below are tests for both socket and process IO

    def test_uname(self):
        for io in self.cmdline('uname'):
            rs = io.read()
            self.assertEqual(rs.strip(), os.uname()[0].encode('utf-8'), repr(rs))

    def test_cat(self):
        for io in self.cmdline('cat'):
            s = b'The Cat is #1\n'
            io.write(s)
            rs = io.readline()
            self.assertEqual(rs.strip(), s.strip(), 'TestCase Failure: got ' + repr(rs))

    def test_cat_eof(self):
        for io in self.cmdline('cat'):
            s = b'The Cat is #1'
            io.write(s)
            io.end()
            rs = io.read()
            self.assertEqual(rs.strip(), s.strip(), repr(rs))

    def test_cat_readline(self):
        for io in self.cmdline('cat'):
            s = b'The Cat is #1'
            io.write(s + b'\n' + b'blah blah')
            rs = io.readline()
            self.assertEqual(rs.strip(), s)

    def test_read_until(self):
        for io in self.cmdline('cat'):
            s = b''.join([random.choice(string.printable[:62]).encode('utf-8') for x in range(1000)])
            io.writeline(s)
            io.read(100)
            io.read_until(s[500:600])
            mid = io.read(100)
            self.assertEqual(mid, s[600:700])

    def test_get_pass(self):
        # here we have to use TTY, or password won't get write thru
        # if you use subprocess, you will encouter same effect
        for io in self.exec_script('userpass.py', stdin=TTY):
            io.read_until(b'Welcome')
            io.readline()
            io.read_until(b'Username: ')
            io.writeline(b'user')
            # note the 'stream = sys.stdout' line in userpass.py,
            # which makes this prompt readable here,
            # else Password will be echoed back from stdin(tty), not stdout,
            # so you will never read this!!
            io.read_until(b'Password: ')
            io.writeline(b'pass')
            io.readline()
            line = io.readline()
            self.assertEqual(line.strip(), b'Logged in', repr(line))
            io.end()

    def test_xxd(self):
        for io in self.cmdline('xxd',
                               print_write=COLORED(REPR),
                               print_read=COLORED(RAW, 'yellow'),
                               socat_exec=''):
            io.write(b''.join([bytes([x]) for x in range(0, 256)]) + b'\n')
            io.end()
            out = io.read()
            expected = open("test_xxd.txt", "rb").read()
            self.assertEqual(out.replace(b'\r\n', b'\n'), expected, repr((out, expected)))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)

    tests = []

    if len(sys.argv) > 1:
        tests.extend(sys.argv[1:])

    if len(tests):
        suite = unittest.TestSuite(list(map(Test, tests)))

    rs = unittest.TextTestRunner(verbosity=2).run(suite)
    if len(rs.errors) > 0 or len(rs.failures) > 0:
        sys.exit(10)
    else:
        sys.exit(0)
