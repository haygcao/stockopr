# -*- coding: utf-8 -*-
import time

import psutil
import pywinauto
import win32gui

from .. import config


def is_foreground():
    w = win32gui.GetForegroundWindow()
    text = win32gui.GetWindowText(w)

    return '网上股票交易系统5.0' in text


def get_pid_by_exec(exec_path):
    exec = exec_path.split('\\')[-1].lower()
    proc_list = [proc for proc in psutil.process_iter() if exec == proc.name().lower()]
    return proc_list[0].pid if proc_list else -1


def max_window(window):
    if window.get_show_state() != 3:
        window.maximize()
    window.set_focus()


def active_window():
    global g_main_window
    try:
        if not g_main_window:
            max_window(g_main_window)
            return g_main_window
    except:
        g_main_window = None

    pid = get_pid_by_exec('C:\\同花顺下单\\xiadan.exe')

    if pid < 0:
        app = pywinauto.Application(backend="win32").start('C:\\同花顺下单\\xiadan.exe')
    else:
        app = pywinauto.Application(backend="win32").connect(process=pid)

    main_window = app.window(title='网上股票交易系统5.0')
    max_window(main_window)

    pywinauto.mouse.click(coords=config.pos_centre)
    pywinauto.keyboard.send_keys('{ESC}')
    while not is_foreground():
        pywinauto.keyboard.send_keys('{ESC}')
        time.sleep(0.1)

    g_main_window = main_window

    return main_window


def copy_to_clipboard():
    """
    # https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
    '+': {VK_SHIFT}
    '^': {VK_CONTROL}
    '%': {VK_MENU} a.k.a. Alt key
    """
    pywinauto.mouse.click(coords=config.pos_centre)
    # pywinauto.mouse.release(coords=pos_centre)
    time.sleep(0.2)

    # pywinauto.mouse.right_click(coords=pos_centre)
    # pywinauto.mouse.release(coords=pos_centre)
    # time.sleep(0.2)
    # pywinauto.keyboard.send_keys('C')

    pywinauto.keyboard.send_keys('^c')
    time.sleep(0.2)


def clean_clipboard_data(data, cols):
    """
    清洗剪贴板数据
    :param data: 数据
    :param cols: 列数
    :return: 清洗后的数据，返回列表
    """
    lst = data.strip().split()[:-1]
    matrix = []
    for i in range(0, len(lst) // cols):
        matrix.append(lst[i * cols:(i + 1) * cols])
    return matrix[1:]


def get_screen_size():
    return win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)


def get_cursor_pos():
    return win32api.GetCursorPos()
