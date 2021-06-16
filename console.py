import datetime
import multiprocessing
import os
import signal
import subprocess
import sys
import threading
import time
import warnings

import psutil
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QLabel,
                             QComboBox, QApplication, QLineEdit, QGridLayout, QPushButton, QMainWindow)
import pywinauto
import win32api

import chart
import watch_dog
from acquisition import acquire, basic, quote_db, tx
from config import config
from pointor.signal import write_supplemental_signal
from trade_manager import trade_manager
from util import util
from util.pywinauto_util import max_window


warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.initUI()
        self.show()

    def initUI(self):
        self.alertWidget = Panel()
        self.setCentralWidget(self.alertWidget)


class Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('data/icon11.png'))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.dict = {}
        self.code = '300502'
        self.period = 'day'
        self.monitor_proc = None
        self.check_thread = None
        self.rlock = threading.RLock()
        self.running = True
        self.count = '0'

        self.initUI()

    def initUI(self):
        self.lbl = QLabel('{} {}'.format(self.code, self.period), self)
        self.log = QLabel("this for log", self)

        self.combo_code = QComboBox(self)
        # comboCode.adjustSize()
        self.combo_code.resize(self.combo_code.width() + 50, self.combo_code.height())
        self.load()

        self.combo_code.activated[str].connect(self.on_activated_code)

        btn_tdx = QPushButton('通达信', self)
        btn_tdx.clicked.connect(self.open_tdx)

        btn_load = QPushButton('load', self)
        btn_load.clicked.connect(self.load)

        combo_period = QComboBox(self)
        for period in ['m1', 'm5', 'm15', 'm30', 'm60', 'day', 'week']:
            combo_period.addItem(period)

        # comboPeriod.move(50, 50)
        # self.lbl.move(50, 150)

        combo_period.activated[str].connect(self.on_activated_period)

        qle_code = QLineEdit('300502', self)

        # qle.move(60, 100)
        # self.lbl.move(60, 40)

        qle_code.textChanged[str].connect(self.on_code_changed)

        btn_show_chart = QPushButton('show', self)
        btn_show_chart.clicked.connect(self.show_chart)

        pid = util.get_pid_of_python_proc('watch_dog')
        if pid < 0:
            txt = 'watch dog stopped'
            color = 'red'
        else:
            txt = 'watch dog running'
            color = 'green'
        self.btn_monitor = QPushButton(txt, self)
        self.btn_monitor.setStyleSheet("background-color : {}".format(color))
        self.btn_monitor.clicked.connect(self.control_watch_dog)

        threading.Thread(target=self.check_watch_dog, args=()).start()

        btn_update_quote = QPushButton('update quote', self)
        btn_update_quote.clicked.connect(self.update_quote)

        btn_sync = QPushButton('sync', self)
        btn_sync.clicked.connect(self.sync)

        qle_count = QLineEdit(self.count, self)
        qle_count.textChanged[str].connect(self.on_count_changed)

        btn_buy = QPushButton('Buy', self)
        btn_buy.clicked.connect(self.buy)

        btn_sell = QPushButton('Sell', self)
        btn_sell.clicked.connect(self.sell)

        grid = QGridLayout()

        grid.setSpacing(10)
        grid.addWidget(self.lbl, 1, 0)
        grid.addWidget(self.combo_code, 2, 0)
        grid.addWidget(combo_period, 2, 1)
        grid.addWidget(btn_show_chart, 2, 2)
        grid.addWidget(btn_tdx, 2, 3)
        grid.addWidget(btn_load, 2, 4)
        grid.addWidget(self.btn_monitor, 1, 1)
        grid.addWidget(btn_update_quote, 1, 2)
        grid.addWidget(btn_sync, 1, 3)

        grid.addWidget(qle_code, 3, 0)
        grid.addWidget(qle_count, 3, 1)
        grid.addWidget(btn_buy, 3, 2)
        grid.addWidget(btn_sell, 3, 3)

        grid.addWidget(self.log, 4, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('K')
        self.show()

    def on_code_changed(self, text):
        if len(text) > 1 and text[0] not in '036' and text[-1] == ';':
            text = basic.get_stock_code(text[:-1])
        self.code = text
        self.lbl.setText('{} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def on_count_changed(self, text):
        self.count = text
        self.lbl.setText('order {} {}'.format(self.code, self.count))
        self.lbl.adjustSize()

    def on_activated_code(self, text):
        self.code = text.split()[0]
        self.lbl.setText('{} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def open_tdx(self):
        pid = util.get_pid_by_exec('C:\\new_tdx\\TdxW.exe')
        if pid < 0:
            app = pywinauto.Application(backend="win32").start('C:\\new_tdx\\TdxW.exe')
        else:
            app = pywinauto.Application(backend="win32").connect(process=pid)

        pos = win32api.GetCursorPos()
        main_window = app.window(class_name='TdxW_MainFrame_Class')
        max_window(main_window)
        win32api.SetCursorPos(pos)

        # main_window.type_keys(str(self.code))
        pywinauto.keyboard.send_keys(str(self.code))
        pywinauto.keyboard.send_keys('{ENTER}')

    def load(self):
        self.combo_code.clear()

        code_name_map = quote_db.query_trade_order_map()
        for code, order in code_name_map.items():
            name = basic.get_stock_name(code)
            self.combo_code.addItem('{} {}'.format(code, name))

        with open('data/portfolio.txt', encoding='utf8') as fp:
            for code_name in fp:
                code_name = code_name.strip()
                if not code_name:
                    continue
                # name = basic.get_stock_name(code)
                self.combo_code.addItem(code_name)

    def on_activated_period(self, text):
        self.period = text
        self.lbl.setText('{} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def show_chart(self):
        print('{} {}'.format(self.code, self.period))
        p = multiprocessing.Process(target=chart.open_graph, args=(self.code, self.period,))
        p.start()
        p.join(timeout=1)
        # open_graph(self.code, self.period)

    def control_watch_dog(self):
        with self.rlock:
            pid = util.get_pid_of_python_proc('watch_dog')
            # if self.btn_monitor.isChecked():
            if pid > 0:
                print('stop watch dog')
                self.btn_monitor.setText('watch dog stopped')
                self.btn_monitor.setStyleSheet("background-color : red")
                # self.btn_monitor.setCheckable(False)
                # self.monitor_proc.terminate()
                # self.monitor_proc.join()
                # self.monitor_proc = None
                # os.kill(pid, signal.CTRL_C_EVENT)
                psutil.Process(pid=pid).terminate()
            else:
                print('start watch dog')
                self.btn_monitor.setText('watch dog running')
                self.btn_monitor.setStyleSheet("background-color : green")
                # self.btn_monitor.setCheckable(True)
                # self.monitor_proc = multiprocessing.Process(target=watch_dog.monitor, args=())
                # self.monitor_proc.start()

                util.run_subprocess('watch_dog.py')

    def update_quote(self):
        p = multiprocessing.Process(target=acquire.save_quote, args=())
        p.start()

    def sync(self):
        p = multiprocessing.Process(target=trade_manager.sync, args=())
        p.start()
        print('sync started')

    def buy(self):
        supplemental_signal_path = config.supplemental_signal_path
        write_supplemental_signal(supplemental_signal_path, self.code, datetime.datetime.now(), 'B', self.period, '')
        quote = tx.get_realtime_data_sina(self.code)
        trade_manager.buy(self.code, price_trade=quote['close'][-1], count=int(self.count), auto=True)

    def sell(self):
        supplemental_signal_path = config.supplemental_signal_path
        write_supplemental_signal(supplemental_signal_path, self.code, datetime.datetime.now(), 'S', self.period, '')
        quote = tx.get_realtime_data_sina(self.code)
        trade_manager.sell(self.code, price_trade=quote['close'][-1], count=int(self.count), auto=True)

    def check_watch_dog(self):
        pid_prev_check = -1
        while self.running:
            pid = util.get_pid_of_python_proc('watch_dog')
            if pid == pid_prev_check:
                time.sleep(3)
                continue

            pid_prev_check = pid
            if pid < 0:
                txt = 'watch dog stopped'
                color = 'red'
            else:
                txt = 'watch dog running'
                color = 'green'

            print('check watch dog', color)
            with self.rlock:
                self.btn_monitor.setText(txt)
                self.btn_monitor.setStyleSheet("background-color : {}".format(color))

        print('check thread exit')

    def stop_check_thread(self):
        ex.running = False

    def stop_watch_dog(self):
        pid = util.get_pid_of_python_proc('watch_dog')
        if pid > 0:
            print('send signal.CTRL_C_EVENT')
            os.kill(pid, signal.CTRL_C_EVENT)
            # psutil.Process(pid).terminate()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # ex = Main()
    ex = Panel()
    rc = app.exec_()
    ex.stop_check_thread()
    ex.stop_watch_dog()

    sys.exit(rc)
