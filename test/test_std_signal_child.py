# -*- coding: utf-8 -*-
import atexit
import signal, os
import time


@atexit.register
def goodbye():
    with open('aaa.txt') as f:
        f.write('Signal handler called with signal')


# parent process os.kill(, signal.SIGINT), handler do not called
def handler(signum, frame):
    with open('aaa.txt') as f:
        f.write('Signal handler called with signal')
    print('Signal handler called with signal', signum)
    raise OSError("Couldn't open device!")

# On Windows, signal() can only be called with SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, or SIGTERM.
# A ValueError will be raised in any other case.
# Set the signal handler and a 5-second alarm
signal.signal(signal.SIGINT, handler)
# signal.alarm(5)

while True:
    time.sleep(1)
