# -*- coding: utf-8 -*-
import datetime
import multiprocessing
import os.path
import subprocess
import sys
import time

from util import util


def monitor():
    root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    monitor_path = os.path.join(root_dir, 'quotation_monitor.py')
    while True:
        now = datetime.datetime.now()
        if now.hour >= 15:
            return

        pid = util.get_pid_of_python_proc('quotation_monitor')
        if pid < 0:
            # from monitor import monitor_today
            # p = multiprocessing.Process(target=monitor_today.monitor_today)
            # p.start()
            os.environ['PYTHONPATH'] = root_dir
            py = str(os.path.join(root_dir, 'venv', 'Scripts', 'python.exe'))
            subprocess.run([py, monitor_path])

        time.sleep(5)


if __name__ == '__main__':
    # p = psutil.Process()   # 当前进程
    # print(p.cmdline())
    monitor()
