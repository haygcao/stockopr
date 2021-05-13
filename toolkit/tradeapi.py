# -*- coding: utf-8 -*-
import time

import psutil
import pywinauto


def get_pid_by_exec(exec_path):
    exec = exec_path.split('\\')[-1]
    proc_list = [proc for proc in psutil.process_iter() if exec == proc.name().lower()]

    return proc_list[0].pid if proc_list else -1


def order(direct, code, count, price=0, auto=False):
    pid = get_pid_by_exec('C:\\同花顺软件\\同花顺\\xiadan.exe')

    if pid < 0:
        app = pywinauto.Application(backend="win32").start('C:\\同花顺软件\\同花顺\\xiadan.exe')
    else:
        app = pywinauto.Application(backend="win32").connect(process=pid)

    main_window = app.window(title='网上股票交易系统5.0')
    if direct == 'B':
        main_window.type_keys('{F2}')
        main_window.type_keys('{F1}')
    else:
        main_window.type_keys('{F1}')
        main_window.type_keys('{F2}')

    main_window.type_keys(str(code))
    main_window.type_keys('{TAB}')
    if price > 0:
        main_window.type_keys(str(price))
    main_window.type_keys('{TAB}')
    main_window.type_keys(str(count))
    main_window.type_keys('{TAB}')
    main_window.type_keys('{ENTER}')
    if auto:
        time.sleep(0.5)
        pywinauto.keyboard.send_keys('{ENTER}')
        time.sleep(0.5)
        pywinauto.keyboard.send_keys('{ENTER}')


if __name__ == '__main__':
    code = '300502'
    count = '100'
    order('B', code, count, auto=True)
