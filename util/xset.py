# -*- coding: utf-8 -*-

import subprocess
from Xlib import X
from Xlib.display import Display


def turn_on_screen(ungrab):
    if ungrab:
        display = Display(':0')
        display.ungrab_pointer(X.CurrentTime)
        display.ungrab_keyboard(X.CurrentTime)

    # cmd = 'xset dpms force off'.split()
    cmd = 'xset -display :0.0 dpms force on'.split()
    subprocess.call(cmd)


def turn_off_screen(grab):
    if grab:
        display = Display(':0')
        root = display.screen().root
        root.grab_pointer(True, X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask,
                          X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime)
        root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

    # cmd = 'xset dpms force off'.split()
    cmd = 'xset -display :0.0 dpms force off'.split()
    subprocess.call(cmd)

    # p = subprocess.Popen('gnome-screensaver-command -i'.split())
    # time.sleep(1)
    # while True:
    #     print(display.next_event())
    #     p.terminate()
    #     break
