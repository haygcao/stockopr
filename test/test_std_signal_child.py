# -*- coding: utf-8 -*-
import atexit
import signal, os
import time

from util.log import logger
# from log4python.log4python import Log

@atexit.register
def goodbye():
    pass
    # logger.info('Signal handler called with signal')


# parent process os.kill(, signal.SIGINT), handler do not called
def handler(signum, frame):
    logger.info('Signal handler called with signal', signum)
    raise OSError("Couldn't open device!")

def f():
    print(__name__)
    logger.info(__name__)
    # logger_ = Log(__file__)
    logger.info(__name__)


if __name__ == '__main__':
    # On Windows, signal() can only be called with SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, or SIGTERM.
    # A ValueError will be raised in any other case.
    # Set the signal handler and a 5-second alarm
    signal.signal(signal.SIGINT, handler)
    # signal.alarm(5)
    print('this is child process')
    # logger.info('this is child process')
