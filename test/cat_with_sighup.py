#!/usr/bin/env python3

import os
import sys
import signal
import datetime
import time


def handler(a, b):
    now = datetime.datetime.now().strftime('[%Y-%m-%d_%H:%M:%S]')
    f = open('/tmp/zio-test-sighup.txt', 'a')
    f.write('%s %r %r\n' % (now, a, b))
    f.close()
    sys.exit(0)


signal.signal(signal.SIGHUP, handler)

print('pid =', os.getpid())

while True:
    sys.stdout.write(sys.stdin.readline())
