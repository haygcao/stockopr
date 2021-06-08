# -*- coding: utf-8 -*-
import atexit
import datetime
import signal
import sys
import time

import psutil

from util import util
from util.log import logger

g_quotation_monitor_pid = -1


def handler(signum, frame):
    logger.info('Signal handler called with signal', signum)
    goodbye()
    sys.exit(0)
    # raise OSError("Couldn't open device!")


# @atexit.register
def goodbye():
    logger.info('watch dog will exit')
    if g_quotation_monitor_pid > 0:
        psutil.Process(g_quotation_monitor_pid).terminate()
        print('terminate quotation monitor')


def monitor():
    # Set the signal handler and a 5-second alarm
    signal.signal(signal.SIGTERM, handler)
    # signal.alarm(signal.SIGTERM)

    global g_quotation_monitor_pid
    while True:
        now = datetime.datetime.now()
        if now.hour >= 15:
            return

        g_quotation_monitor_pid = util.get_pid_of_python_proc('quotation_monitor')
        if g_quotation_monitor_pid < 0:
            logger.info('quotation_monitor not running, start...')
            util.run_subprocess('quotation_monitor.py')

        time.sleep(5)


if __name__ == '__main__':
    # p = psutil.Process()   # 当前进程
    # print(p.cmdline())
    monitor()
