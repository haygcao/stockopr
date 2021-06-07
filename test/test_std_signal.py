import os
import signal
import subprocess

from util import util

pid = util.get_pid_of_python_proc('test_std_signal_child')
if pid < 0:
    subprocess.Popen(['python', 'test/test_std_signal_child.py'])

pid = util.get_pid_of_python_proc('test_std_signal_child')
print(pid)
if pid > 0:
    # child process's signal handler will not be revoked
    os.kill(pid, signal.SIGINT)

pid = util.get_pid_of_python_proc('test_std_signal_child')
print(pid)
