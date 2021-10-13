# -*- coding: utf-8 -*-

"""
https://github.com/jordansissel/xdotool

xdotool search "Mozilla Firefox" windowactivate --sync key --clearmodifiers ctrl+l
xdotool search --onlyvisible --classname "gnome-terminal" windowsize %@ 500 500
"""
import subprocess


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
    cmd = ['xdotool', 'search', name]
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


def mouse_move(x, y):
    cmd = ['xdotool', 'mousemove', x, y]
    subprocess.run(cmd)


def click_left():
    cmd = ['xdotool', 'click', 1]
    subprocess.run(cmd)
