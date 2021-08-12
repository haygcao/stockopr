#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtWidgets import QLCDNumber
from PyQt5.Qt import QPoint, QPalette, QTimer, QTime, QRect
from PyQt5.QtCore import Qt


class DigitalClock(QLCDNumber):

    def __init__(self):
        super().__init__()
        self.__init_data()
        self.__init_view()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.Tool)

    def __init_data(self):
        self.__show_colon = True
        self.__drag_position = QPoint(0, 0)

        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.show_time)

        self.__timer.start(1000)

    def __init_view(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.lightGray)
        self.setPalette(palette)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.4)
        self.resize(200, 60)
        self.setNumDigits(8)
        self.show_time()

    def show_time(self):
        time = QTime.currentTime()
        time_text = time.toString(Qt.DefaultLocaleLongDate)

        # 冒号闪烁
        if self.__show_colon:
            self.__show_colon = False
        else:
            time_text = time_text.replace(':', ' ')
            self.__show_colon = True

        self.display(time_text)

    def mousePressEvent(self, mouse_event):
        btn_code = mouse_event.button()

        if btn_code == Qt.LeftButton:
            self.__drag_position = mouse_event.globalPos() - self.frameGeometry().topLeft()
            print(self.__drag_position)
            mouse_event.accept()
        elif btn_code == Qt.RightButton:
            self.close()
            sys.exit(0)

    def mouseMoveEvent(self, mouse_event):
        self.move(mouse_event.globalPos() - self.__drag_position)
        mouse_event.accept()

    def location(self):
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = self.geometry()

        x = ag.width() - widget.width() - 30
        y = 2 * ag.height() - sg.height() - widget.height() - 10
        y = 50

        self.move(x, y)


def main():
    app = QApplication(sys.argv)
    clock = DigitalClock()
    clock.location()
    clock.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
