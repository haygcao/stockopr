# -*- coding: utf-8 -*-

"""
https://github.com/jordansissel/xdotool

xdotool search "Mozilla Firefox" windowactivate --sync key --clearmodifiers ctrl+l
xdotool search --onlyvisible --classname "gnome-terminal" windowsize %@ 500 500
"""
import subprocess
import time


def get_active_window():
    cmd = ['xdotool', 'getactivewindow']
    p = subprocess.run(cmd, capture_output=True)
    handle = p.stdout.decode(encoding='utf8').strip()
    return handle


def active_window_by_name(name):
    cmd = ['wmctrl', '-a', name]
    p = subprocess.run(cmd)


def active_window_by_handle(handle):
    cmd = ['wmctrl', '-a', handle]
    p = subprocess.run(cmd)


def get_window_name(handle):
    cmd = ['xdotool', 'getwindowname', handle]
    p = subprocess.run(cmd, capture_output=True)
    name = p.stdout.decode(encoding='utf8').strip()
    return name


def search_window_handle(name):
    cmd = ['xdotool', 'search', '--onlyvisible', name]
    p = subprocess.run(cmd, capture_output=True)
    handle = p.stdout.decode(encoding='utf8').strip()
    return handle


def close_window_clicked():
    # kill the process
    cmd = ['xdotool', 'selectwindow', 'windowclose']
    p = subprocess.run(cmd)


def send_key(key):
    cmd = ['xdotool', 'key', key]
    p = subprocess.run(cmd)


def edit(string):
    cmd = ['xdotool', 'type', string]
    subprocess.run(cmd)


def mouse_move(pos):
    x, y = pos
    cmd = ['xdotool', 'mousemove', str(x), str(y)]
    subprocess.run(cmd)


def click_left():
    cmd = ['xdotool', 'click', '1']
    subprocess.run(cmd)


def get_cursor_pos():
    cmd = ['xdotool', 'getmouselocation']
    p = subprocess.run(cmd, capture_output=True)
    ret = p.stdout.decode(encoding='utf8').strip()
    # x:547 y:508 screen:0 window:67108874
    arr = ret.split()
    x = arr[0][2:]
    y = arr[1][2:]

    return x, y


def has_popup(cls):
    """
    shuhm@shuhm-PC:~/workspace/stockopr$ xdotool search --onlyvisible "tdx"
    Defaulting to search window name, class, and classname
    106954766
    71303242
    shuhm@shuhm-PC:~/workspace/stockopr$ xdotool search --onlyvisible "tdxw"
    Defaulting to search window name, class, and classname
    106954766
    """
    ret = search_window_handle(cls)
    return '\n' in ret


def close_popup():
    # pylinuxauto.send_key('alt+Tab')
    mouse_move((800, 500))
    time.sleep(0.3)
    click_left()
    time.sleep(1)
    send_key('Escape')
