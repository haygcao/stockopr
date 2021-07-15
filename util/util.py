import json
import os
import subprocess

import psutil
import datetime
import time


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


def get_pname_by_id(pid):
    try:
        p = psutil.Process(pid)
        return p.name()
    except psutil.NoSuchProcess:
        return None


def get_pid_by_name(pname):
    """ get process by name
    return the first process if there are more than one
    """

    '''
    for pid in psutil.pids():
        p = psutil.Process(pid)
        print(pid, p.name())
        if 'cmd' == psutil.Process(pid).name():
            print(pid)
            break
    '''
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == pname.lower():
                return proc.pid  # return if found one
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    return -1


def get_pid_by_exec(exec_path):
    exec = exec_path.split('\\')[-1].lower()
    proc_list = [proc for proc in psutil.process_iter() if exec == proc.name().lower()]
    return proc_list[0].pid if proc_list else -1


def get_pid_of_python_proc(args):
    for proc in psutil.process_iter():
        if proc.name() != 'python.exe':
            continue
        cmdline = proc.cmdline()
        if args in str(cmdline):
            return proc.pid
    return -1


def get_root_dir():
    root_dir = os.path.join(os.path.dirname(__file__), '..')
    return os.path.abspath(root_dir)


def run_subprocess(script):
    # root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    root_dir = get_root_dir()
    monitor_path = os.path.join(root_dir, script)
    os.environ['PYTHONPATH'] = root_dir
    py = str(os.path.join(root_dir, 'venv', 'Scripts', 'python.exe'))
    # subprocess.run([py, monitor_path])
    subprocess.Popen([py, monitor_path])


def print_stock_info(stock_info):
    #['highest', 'lowest', 'last_min', 'cur', 'time_last_record', 'name']
    key_str = ['price', 'last_min', 'high', 'low']
    code = stock_info['code']
    cnt = time.strftime('[%H:%M:%S]', time.localtime()) + stock_info['name'] + '[%s]:' % str(code)
    for key in key_str:
        cnt += key + ':%.2f\t' % stock_info[key]
    print(cnt)


def pause_trade(day):
    today = datetime.date.today()
    if (today - day).days > 2:
        return True
    return False


# 标准日期格式 2016-01-01 str(datetime.date.today())
def get_day(day, delta):
    ymd = [int(i) for i in day.split('-')]
    day = datetime.date(ymd[0], ymd[1], ymd[2])
    day = day + datetime.timedelta(delta)

    return str(day)


def get_today():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def get_diff_days(day1, day2):
    ymd = [int(i) for i in day1.split('-')]
    date1 = datetime.date(ymd[0], ymd[1], ymd[2])
    ymd = [int(i) for i in day2.split('-')]
    date2 = datetime.date(ymd[0], ymd[1], ymd[2])

    return (date2 - date1).days


if __name__ == '__main__':
    # r = get_day('2015-12-31', 1)
    r = get_diff_days('2015-12-31', '2016-01-10')
    print(r)
