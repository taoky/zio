#!/usr/bin/env python3

import os
import sys


def evals(s):
    st = 0      # 0 for normal, 1 for escape, 2 for \xXX
    ret = []
    i = 0
    while i < len(s):
        if st == 0:
            if s[i] == '\\':
                st = 1
            else:
                ret.append(s[i].encode())
        elif st == 1:
            if s[i] in ('"', "'", "\\", "t", "n", "r"):
                if s[i] == 't':
                    ret.append(b'\t')
                elif s[i] == 'n':
                    ret.append(b'\n')
                elif s[i] == 'r':
                    ret.append(b'\r')
                else:
                    ret.append(s[i].encode())
                st = 0
            elif s[i] == 'x':
                st = 2
            else:
                raise Exception('invalid repr of str %s' % s)
        else:
            num = int(s[i:i + 2], 16)
            assert 0 <= num < 256
            ret.append(bytes([num]))
            # DO NOT USE chr(num), as it may bring 0xc2 (leading character in UTF-8) to sequence.
            st = 0
            i += 1
        i += 1
    return b"".join(ret)


sys.stdout.buffer.write(evals(sys.argv[1]))
sys.stdout.flush()
