# -*- coding: utf-8 -*-
import os
import time

import psutil
import pywinauto
import win32gui
from PIL import ImageGrab
# https://digi.bib.uni-mannheim.de/tesseract/
from pytesseract import image_to_string

from .. import config


g_main_window = None
g_app = None


def is_foreground():
    w = win32gui.GetForegroundWindow()
    text = win32gui.GetWindowText(w)

    return config.ths_main_window_title in text


def get_pid_by_exec(exec_path):
    # os.path.join() 在 windows 下生成的路径分割符是 '\'
    exec = exec_path.split('\\')[-1].lower()
    proc_list = [proc for proc in psutil.process_iter() if exec == proc.name().lower()]
    return proc_list[0].pid if proc_list else -1


def max_window(window):
    if window.get_show_state() != 3:
        window.maximize()
    window.set_focus()


def active_window():
    global g_app
    global g_main_window

    try:
        if not g_main_window:
            max_window(g_main_window)
            return g_main_window
    except:
        g_main_window = None

    ths_exe = os.path.join(config.ths_home, 'xiadan.exe')
    pid = get_pid_by_exec(ths_exe)

    if pid < 0:
        g_app = pywinauto.Application(backend="win32").start(ths_exe)
    else:
        g_app = pywinauto.Application(backend="win32").connect(process=pid)

    main_window = g_app.window(title=config.ths_main_window_title)
    max_window(main_window)

    pywinauto.mouse.click(coords=config.pos_centre)
    pywinauto.keyboard.send_keys('{ESC}')
    while not is_foreground():
        pywinauto.keyboard.send_keys('{ESC}')
        time.sleep(0.1)

    g_main_window = main_window

    return main_window


def _copy_authentication(app, trade_win):
    popup_hwnd = trade_win.popup_window()
    if not popup_hwnd:
        return

    for i in range(10):
        popup_window = app.window(handle=popup_hwnd)
        popup_window.set_focus()
        rect = popup_window['Static2'].rectangle()
        img = ImageGrab.grab((rect.left, rect.top, rect.right, rect.bottom))

        code = image_to_string(img)
        if len(code) >= 4:
            code = code[:4]
            # not enough to use EM_REPLACESEL - 需要用 admin 运行下单程序, 但仍然无法输入验证码
            # Use the EM_REPLACESEL message to replace only a portion of the text in an edit control.
            # To replace all of the text, use the WM_SETTEXT message.
            # popup_window['Edit'].set_edit_text(code)
            # time.sleep(0.1)

            pywinauto.mouse.click(coords=config.pos_verify)
            pywinauto.keyboard.send_keys(code)

            popup_window.type_keys('{ENTER}')

        time.sleep(0.1)

        popup_hwnd = trade_win.popup_window()
        if not popup_window:
            return


def copy_to_clipboard(pos=None):
    """
    # https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
    '+': {VK_SHIFT}
    '^': {VK_CONTROL}
    '%': {VK_MENU} a.k.a. Alt key
    """
    pos = pos if pos else config.pos_centre
    pywinauto.mouse.click(coords=pos)
    # pywinauto.mouse.release(coords=pos_centre)
    # time.sleep(0.2)

    # pywinauto.mouse.right_click(coords=pos_centre)
    # pywinauto.mouse.release(coords=pos_centre)
    # time.sleep(0.2)
    # pywinauto.keyboard.send_keys('C')

    pywinauto.keyboard.send_keys('^c')

    global g_app
    global g_main_window
    _copy_authentication(g_app, g_main_window)

    # time.sleep(0.2)


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
