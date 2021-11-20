# -*- coding: utf-8 -*-

# Copyright (c) 2021, shuhm. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""stockopr is stock trade helper in Python. Supported platforms:

 - Linux
 - Windows

Works with Python versions from 3.4 to 3.9+.
"""

import datetime
import multiprocessing
import os
import re
import signal
import subprocess
import sys
import threading
import time
import warnings

import pandas
import psutil
import pyautogui
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QPalette
from PyQt5.QtWidgets import (QWidget, QLabel,
                             QComboBox, QApplication, QLineEdit, QGridLayout, QPushButton, QMainWindow, QDesktopWidget,
                             QHBoxLayout, QVBoxLayout, QShortcut, QTextBrowser, QListWidget)
import system_hotkey
# import win32api

import chart
import trade_manager.db_handler
from acquisition import acquire, basic, quote_db, tx
from config import config
from console_trade import PlaceControlInCell
from indicator import relative_price_strength
from pointor.signal import write_supplemental_signal
from selector import selector
from selector.plugin import fund
from server import config as svr_config
from trade_manager import trade_manager
from util import util, dt, qt_util, singleten, pylinuxauto
from util.QComboCheckBox import QComboCheckBox
from util.log import logger
from util.pywinauto_util import max_window

# pywinauto
# QWindowsContext: OleInitialize() failed: "COM error 0xffffffff80010106 RPC_E_CHANGED_MODE (Unknown error 0x080010106)"
warnings.simplefilter("ignore", category=UserWarning)
sys.coinit_flags = 2
# import pywinauto

# g_periods = ['m1', 'm5', 'm15', 'm30', 'm60', 'day', 'week']
g_periods = ['m5', 'm30', 'day', 'week']
g_periods.reverse()
g_indicators = ['macd', 'force_index', 'adosc', 'skdj', 'rsi', 'rps']
g_market_indicators = ['nhnl', 'adl', 'ema_over']


def list_to_str(list_: list):
    return '|'.join([str(i) for i in list_])


def get_combo_signal_key(s):
    if 'enter' in s:
        if 'deviation' in s:
            return 'enter_deviation'
        else:
            return 'enter'
    else:
        if 'deviation' in s:
            return 'exit_deviation'
        else:
            return 'exit'


def send_key(key):
    import pyautogui as pag

    # x, y = pag.position()
    #
    # screen_width, screen_height = pyautogui.size()
    # pyautogui.moveTo(screen_width - 100, screen_height / 2)
    # pyautogui.click()

    pyautogui.typewrite(message=key, interval=0.1)
    pyautogui.press('enter')

    # pag.moveTo(x, y)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.initUI()
        self.show()

    def initUI(self):
        self.alertWidget = Widget()
        self.setCentralWidget(self.alertWidget)


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.combo_classification = QComboCheckBox()
        # self.combo_classification = QPushButton('xxx')
        # self.combo_classification = QLabel('xxx')
        grid = QGridLayout()
        grid.addWidget(self.combo_classification)
        # grid = QVBoxLayout()
        # grid.addWidget(self.combo_classification)
        # self.setGeometry(300, 300, 280, 170)
        self.setLayout(grid)
        self.show()


class Panel(QWidget):
    sig_keyhot = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('data/icon.png'))

        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # self.setFixedSize(700, 200)
        self.setFixedWidth(700)

        # self.widget_signals = {}
        self.combo_signal = {
            'enter': QComboCheckBox(),
            'enter_deviation': QComboCheckBox(),
            'exit': QComboCheckBox(),
            'exit_deviation': QComboCheckBox()
        }

        self.stock_info_map = {}
        self.account_id = svr_config.ACCOUNT_ID_XY
        self.op_type = svr_config.OP_TYPE_DBP
        self.code = 'maq'
        self.period = 'day'
        self.indicator = g_indicators[0]
        self.monitor_proc = None
        self.check_thread = None
        self.rlock = threading.RLock()
        self.running = True
        self.count_or_price = [0, 0]   # [price, count]
        self.log_lines = []

        QShortcut(QKeySequence(self.tr("F1")), self, self.buy)
        QShortcut(QKeySequence(self.tr("F2")), self, self.sell)

        self.sig_keyhot.connect(self.MKey_pressEvent)

        self.hk_tdx_l = system_hotkey.SystemHotkey()
        self.hk_tdx_r = system_hotkey.SystemHotkey()

        self.hk_tdx = system_hotkey.SystemHotkey()
        self.hk_tdx_l.register(('alt', 'j'), callback=lambda x: self.open_tdx(-1))  # self.switch_code(-1))
        self.hk_tdx_r.register(('alt', 'l'), callback=lambda x: self.open_tdx(1))  # self.switch_code(1))
        self.hk_tdx.register(('alt', 'k'), callback=lambda x: self.open_tdx(0))  # self.switch_code(0))

        # self.hk_show_l = system_hotkey.SystemHotkey()
        # self.hk_show_r = system_hotkey.SystemHotkey()
        # self.hk_show = system_hotkey.SystemHotkey()
        # self.hk_show_l.register(('shift', 'j'), callback=lambda x: self.show_chart(-1))
        # self.hk_show_r.register(('shift', 'l'), callback=lambda x: self.show_chart(1))
        # self.hk_show.register(('shift', 'k'), callback=lambda x: self.show_chart(0))

        self.qle_price = QLineEdit('price', self)
        self.qle_count = QLineEdit('count', self)

        self.lbl = QLabel('{} {} {}'.format(self.code, self.period, list_to_str(self.count_or_price)), self)
        self.lbl_stock_info = QLabel('', self)
        self.combo_code = QComboBox(self)
        self.combo_period = QComboBox(self)
        self.combo_indictor = QComboBox(self)

        self.btn_tdx_prev = QPushButton('<-', self)
        self.btn_tdx_next = QPushButton('->', self)

        self.btn_tdx = QPushButton('tdx', self)
        self.btn_show_chart = QPushButton('show', self)
        self.btn_f10 = QPushButton('f10', self)
        # self.btn_show_chart_prev = QPushButton('<-', self)
        # self.btn_show_chart_next = QPushButton('->', self)

        self.combo_classification = QComboCheckBox()
        self.combo_candidate = QComboCheckBox()
        self.combo_traced = QComboCheckBox()
        self.combo_strategy = QComboCheckBox()

        self.btn_monitor = QPushButton('watch dog', self)
        self.btn_update_quote = QPushButton('update', self)
        self.btn_sync = QPushButton('sync', self)
        self.lbl_account = QLabel('-', self)
        self.lbl_account.setAutoFillBackground(True)  # 允许自动填充背景
        palette = QPalette()  # 定义一个调色板实例
        palette.setColor(QPalette.Window, Qt.blue)  # 配置调色板
        self.lbl_account.setPalette(palette)  # 使用配置好的调色板
        self.lbl_account.setAlignment(Qt.AlignCenter)  # 设置文本居中

        self.btn_update_candidate = QPushButton('u cnd', self)
        self.btn_update_traced = QPushButton('u trc', self)
        self.btn_scan = QPushButton('scan', self)

        self.btn_load = QPushButton('load', self)
        self.qle_code = QLineEdit('300502', self)

        self.btn_buy = QPushButton('buy', self)
        self.btn_sell = QPushButton('sell', self)
        self.btn_new_order = QPushButton('i ordr', self)

        self.btn_delete = QPushButton('delete', self)

        self.order_switch = QPushButton('-', self)
        self.order_switch.setFixedHeight(5)
        self.order_table = PlaceControlInCell()

        self.log_switch = QPushButton('-', self)
        self.log_switch.setFixedHeight(5)
        self.log = QListWidget(self)  # QTextBrowser(self)  # QLabel("this for log", self)
        # self.log.resize(600, 500)
        # self.log.setHidden(True)
        self.log.setFixedHeight(250)

        self.init_ui()
        # self.order_table.setFixedHeight(self.order_table.geometry().height())
        threading.Thread(target=self.check, args=()).start()

        self.show()

    # 热键处理函数
    def MKey_pressEvent(self, i_str):
        self.refresh_log()

    # 热键信号发送函数(将外部信号，转化成qt信号)
    def send_key_event(self, i_str):
        self.sig_keyhot.emit(i_str)

    def init_period(self):
        for period in g_periods:
            self.combo_period.addItem(period)
        self.combo_period.setCurrentIndex(g_periods.index(self.period))
        self.combo_period.activated[str].connect(self.on_activated_period)

    def init_indicator(self):
        for indicator in g_indicators + g_market_indicators:
            self.combo_indictor.addItem(indicator)
        self.combo_indictor.activated[str].connect(self.on_activated_indicator)

        for indicator in ['market_index', 'position', 'allow_buy', 'traced', 'candidate', 'reserve']:
            self.combo_classification.addItem(indicator)
        self.combo_classification.select_index(1)
        self.combo_classification.select_index(2)
        self.combo_classification.select_text('traced')

        for indicator in config.candidate_strategy_list:
            self.combo_candidate.addItem(indicator)

        self.combo_candidate.select_text('finance')
        self.combo_candidate.select_text('fund')
        self.combo_candidate.select_text('second_stage')

        for indicator in config.traced_strategy_list:
            self.combo_traced.addItem(indicator)
        # self.combo_traced.select_text('value_return_ing')
        self.combo_traced.select_text('vcp')

        # self.combo_strategy = QComboBox(self)

        for indicator in config.allow_buy_strategy_list:
            self.combo_strategy.addItem(indicator)

        # self.combo_strategy.setCurrentIndex(1)
        self.combo_strategy.select_text('vcp_breakout')

    def init_ui(self):
        # comboCode.adjustSize()
        self.combo_code.resize(self.combo_code.width() + 50, self.combo_code.height())

        self.combo_code.activated[str].connect(self.on_activated_code)

        self.btn_tdx.clicked.connect(self.open_tdx)
        self.btn_tdx_prev.clicked.connect(self.switch_code)
        self.btn_tdx_next.clicked.connect(self.switch_code)

        self.btn_load.clicked.connect(self.load)
        self.btn_delete.clicked.connect(self.delete_data_in_db)

        self.qle_code.textChanged[str].connect(self.on_code_changed)

        self.btn_show_chart.clicked.connect(self.show_chart)
        self.btn_f10.clicked.connect(self.show_f10)
        # self.btn_show_chart_prev.clicked.connect(self.show_chart)
        # self.btn_show_chart_next.clicked.connect(self.show_chart)

        self.btn_monitor.clicked.connect(self.control_watch_dog)
        self.btn_update_quote.clicked.connect(self.update_quote)
        self.btn_sync.clicked.connect(self.sync)
        self.btn_update_candidate.clicked.connect(self.update_candidate)
        self.btn_update_traced.clicked.connect(self.update_traced)
        self.btn_scan.clicked.connect(self.scan)

        self.qle_price.textChanged[str].connect(self.on_count_or_price_changed)
        self.qle_count.textChanged[str].connect(self.on_count_or_price_changed)

        self.btn_buy.clicked.connect(self.buy)
        self.btn_sell.clicked.connect(self.sell)
        self.btn_new_order.clicked.connect(self.new_trade_order)

        self.init_period()
        self.init_indicator()

        self.log_switch.clicked.connect(self.hide_log)
        self.order_switch.clicked.connect(self.hide_log)

        ###
        # TODO 信号下拉复选框点击 ALL 时报错
        h_layout_signal = QHBoxLayout()

        for combo in self.combo_signal.values():
            combo.activated[str].connect(self.on_activated_signal)
            combo.setMaxVisibleItems(20)
            h_layout_signal.addWidget(combo)

        signals = config.get_all_signal(self.period)
        for s, enabled in signals.items():
            combo = self.combo_signal.get(get_combo_signal_key(s))
            combo.addItem(s)
            if enabled:
                combo.select_text(s)

        grid = QGridLayout()

        grid.setSpacing(10)

        grid.addWidget(self.combo_classification, 1, 0)
        grid.addWidget(self.combo_candidate, 1, 1)
        grid.addWidget(self.combo_traced, 1, 2)
        grid.addWidget(self.combo_strategy, 1, 3)

        h_layout_candidate = QHBoxLayout()
        h_layout_candidate.addWidget(self.btn_update_candidate)
        h_layout_candidate.addWidget(self.btn_update_traced)
        grid.addLayout(h_layout_candidate, 1, 4)

        h_layout_analyse = QHBoxLayout()
        h_layout_analyse.addWidget(self.btn_scan)
        h_layout_analyse.addWidget(self.btn_load)
        grid.addLayout(h_layout_analyse, 2, 4)

        grid.addWidget(self.qle_code, 3, 0)
        h_layout_price_count = QHBoxLayout()
        h_layout_price_count.addWidget(self.qle_price)
        h_layout_price_count.addWidget(self.qle_count)
        grid.addLayout(h_layout_price_count, 3, 1)

        h_layout_order = QHBoxLayout()
        h_layout_order.addWidget(self.btn_buy)
        h_layout_order.addWidget(self.btn_sell)
        grid.addLayout(h_layout_order, 3, 2)

        grid.addWidget(self.combo_code, 2, 0)
        grid.addWidget(self.combo_period, 2, 1)
        grid.addWidget(self.combo_indictor, 2, 2)

        h_layout_tdx = QHBoxLayout()
        h_layout_tdx.addWidget(self.btn_tdx_prev)
        h_layout_tdx.addWidget(self.btn_tdx_next)
        grid.addLayout(h_layout_tdx, 2, 3)

        h_layout_show_chart = QHBoxLayout()
        # h_layout_show_chart.addWidget(self.btn_show_chart_prev)
        h_layout_show_chart.addWidget(self.btn_tdx)
        h_layout_show_chart.addWidget(self.btn_f10)
        h_layout_show_chart.addWidget(self.btn_show_chart)
        # h_layout_show_chart.addWidget(self.btn_show_chart_next)
        grid.addLayout(h_layout_show_chart, 3, 3)

        h_layout_op = QHBoxLayout()
        h_layout_op.addWidget(self.btn_delete)
        h_layout_op.addWidget(self.btn_new_order)
        grid.addLayout(h_layout_op, 3, 4)

        h_layout_data = QHBoxLayout()
        h_layout_data.addWidget(self.btn_update_quote)
        h_layout_data.addWidget(self.btn_sync)
        grid.addWidget(self.lbl, 4, 0)
        grid.addWidget(self.lbl_account, 4, 2)
        grid.addLayout(h_layout_data, 4, 3)
        grid.addWidget(self.btn_monitor, 4, 4)

        layout = QVBoxLayout()
        layout.addStretch(2)
        layout.addLayout(grid)
        layout.addWidget(self.lbl_stock_info)
        layout.addLayout(h_layout_signal)

        v_layout_log = QVBoxLayout()
        h_layout_switch = QHBoxLayout()
        h_layout_switch.addWidget(self.order_switch)
        h_layout_switch.addWidget(self.log_switch)
        v_layout_log.addLayout(h_layout_switch)
        v_layout_log.addWidget(self.order_table)
        v_layout_log.addWidget(self.log)

        layout.addLayout(v_layout_log)

        self.load()

        self.setLayout(layout)

        # self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('K')

    def hide_log(self):
        comp = self.log if self.sender() == self.log_switch else self.order_table
        if comp.isHidden():
            hide = False
            adj = 1
        else:
            hide = True
            adj = -1
        comp.setFixedHeight(comp.geometry().height())
        comp.setHidden(hide)
        self.setFixedHeight(self.geometry().height() + adj * comp.geometry().height())

    def set_label(self):
        s = '{} {} {}'.format(self.code, self.period, list_to_str(self.count_or_price))
        self.lbl.setText(s)
        self.lbl.adjustSize()

        stock_info = self.stock_info_map[self.code]
        self.lbl_stock_info.setText('[{}-{} {}]\trs_rating: [{}]  fmvp: [{}]  percent: [{}]'.format(
            self.code, self.period, list_to_str(self.count_or_price),
            stock_info['rs_rating'], stock_info['fmvp'], stock_info['percent']))

    def checked(self, checked):
        for s, w in self.widget_signals.items():
            if self.sender() == w:
                checked = True if checked == Qt.Checked else False
                w.setChecked(checked)
                s = w.text()
                config.enable_signal(s, checked, self.period)

    def on_code_changed(self, text):
        if not text:
            return

        # if len(text) < 1 or (not text.endswith(';') and not re.match('[0-9]{6}', text) and text != maq):
        if not text.endswith(';'):
            return

        maq = 'maq'
        if not text.startswith(maq) and not re.match('[0-9]{6}', text):
            self.code = basic.get_stock_code(text[:-1])
        else:
            self.code = text[:-1]

        self.set_label()

        # 市场指数长度为 7, 行业指数长度为 6, 且以 '88' 开始
        if len(self.code) == 6 and self.code[0] in '036':
            return

        quote = tx.get_realtime_data_sina(self.code)
        if not isinstance(quote, pandas.DataFrame):
            return

        self.count_or_price[0] = quote['close'][-1]
        # self.qle_price.setText(list_to_str(self.count_or_price))
        self.qle_price.setText(str(quote['close'][-1]))

    def on_count_or_price_changed(self, text):
        if self.sender() == self.qle_price:
            self.count_or_price[0] = float(text) if text else 0
        else:
            self.count_or_price[1] = int(text) if text else 0
        self.set_label()

    def on_activated_code(self, text):
        self.code = text.split()[0]

        quote = tx.get_realtime_data_sina(self.code)
        if isinstance(quote, pandas.DataFrame):
            self.count_or_price[0] = quote['close'][-1]

        self.set_label()

        # self.qle_price.setText(list_to_str(self.count_or_price))
        self.qle_price.setText(str(quote['close'][-1]))

    def on_activated_signal(self, text):
        combo: QComboCheckBox = self.sender()

        enabled = text in [s.text() for s in combo.get_selected()]
        config.enable_signal(text, enabled, self.period)

    def get_forward(self):
        widget = self.sender()
        if widget == self.btn_tdx_prev:  # or widget == self.btn_show_chart_prev:
            return -1
        elif widget == self.btn_tdx_next:  # or widget == self.btn_show_chart_next:
            return 1
        return 0

    def set_current(self, forward=1):
        current_index = self.combo_code.currentIndex()
        max_index = self.combo_code.count() - 1

        if forward == -1:
            current_index -= 1
            current_index = max_index if current_index < 0 else current_index
        # elif
        elif forward == 1:
            current_index += 1
            current_index = 0 if current_index > max_index else current_index

        current_index = max(0, min(current_index, max_index))
        self.combo_code.setCurrentIndex(current_index)

    def switch_code(self, forward):
        forward = forward if forward else self.get_forward()
        self.set_current(forward)

        text = self.combo_code.currentText()
        self.code = text.split()[0]

        self.set_label()

    def open_tdx(self, forward=0):
        if forward != 0:
            self.switch_code(forward)

        # pid = util.get_pid_by_exec('C:\\new_tdx\\TdxW.exe')
        # if pid < 0:
        #     app = pywinauto.Application(backend="uia").start('C:\\new_tdx\\TdxW.exe')
        # else:
        #     app = pywinauto.Application(backend="uia").connect(process=pid)

        # pos = win32api.GetCursorPos()
        # main_window = app.window(class_name='TdxW_MainFrame_Class')
        # max_window(main_window)
        # win32api.SetCursorPos(pos)

        # import win32con
        # width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        # height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        m = {
            'maq': '999999',
            '0000001': '999999',
            '0000688': '000688',  # '"000688 {VK_DOWN}",
            '1399001': '399001',
            '1399006': '399006'
        }

        pylinuxauto.active_window_by_name(config.tdx_window_name)

        # main_window.type_keys(str(self.code))
        code = self.code if len(self.code) == 6 else m[self.code]
        # pylinuxauto.send_key(code)
        time.sleep(0.5)
        send_key(code)
        # pyautogui.typewrite(message=code, interval=0.1)
        # pywinauto.keyboard.send_keys(code)
        # if self.code == '0000688':
        #     time.sleep(0.5)
        # pyautogui.press('enter')
        # pywinauto.keyboard.send_keys('{ENTER}')

    def load(self):
        self.combo_code.clear()

        classification_list = [i.text() for i in self.combo_classification.get_selected()]
        index_list = ['maq', '0000001', '0000688', '1399001', '1399006']
        if 'market_index' in classification_list:
            for code in index_list:
                self.combo_code.addItem(code)

        code_list = []
        if 'position' in classification_list:
            code_list = trade_manager.query_position_ex(self.account_id)

        if 'allow_buy' in classification_list:
            strategy_list = [i.text() for i in self.combo_strategy.get_selected()]
            logger.info('load ', strategy_list)
            code_list_tmp = basic.get_allowed_to_buy_stock_code(strategy_list)
            code_list.extend([code for code in code_list_tmp if code not in code_list])

        if 'traced' in classification_list:
            traced_list = [i.text() for i in self.combo_traced.get_selected()]
            logger.info('load ', traced_list)
            code_list_tmp = basic.get_traced_stock_code(traced_list)
            code_list.extend([code for code in code_list_tmp if code not in code_list])

        if 'candidate' in classification_list:
            candidate_list = [i.text() for i in self.combo_candidate.get_selected()]
            logger.info('load ', candidate_list)
            code_list_tmp = basic.get_candidate_stock_code(candidate_list)
            code_list.extend([code for code in code_list_tmp if code not in code_list])

        for code in code_list:
            name = basic.get_stock_name(code)
            self.combo_code.addItem('{} {}'.format(code, name))

        # self.combo_code.adjustSize()
        self.combo_code.setMaxVisibleItems(50)

        for code in code_list:
            if code in self.stock_info_map:
                continue
            quote = quote_db.get_price_info_df_db(code, 300)
            rs_rating = quote['rs_rating'][-1]
            # rs_rating = int(rs_rating) if rs_rating > 0 else rs_rating
            fmvp = fund.query_fmvp(code)
            # fmvp = round(fmvp, 2) if fmvp > 0 else fmvp
            percent = round(100 * (quote.close[-1] / quote.close[-250] - 1), 3)
            self.stock_info_map.update({code: {'rs_rating': rs_rating, 'fmvp': fmvp, 'percent': percent}})

        qt_util.popup_info_message_box_mp('[{}] loaded'.format(len(code_list)))

    def delete_data_in_db(self):
        classification_list = [i.text() for i in self.combo_classification.get_selected()]
        strategy_list = [i.text() for i in self.combo_strategy.get_selected()]
        traced_list = [i.text() for i in self.combo_traced.get_selected()]

        l = strategy_list + traced_list
        n = basic.delete_portfolio(classification_list, l)
        qt_util.popup_info_message_box_mp('{}{}\n[{}] deleted'.format(classification_list, l, n))

    def on_activated_period(self, text):
        self.period = text
        self.set_label()

        [combo.select_clear() for combo in self.combo_signal.values()]
        signals = config.get_all_signal(self.period)
        for s, v in signals.items():
            # self.widget_signals.get(s).setChecked(v)
            if v:
                self.combo_signal.get(get_combo_signal_key(s)).select_text(s)

    def on_activated_indicator(self, text):
        self.indicator = text
        self.set_label()

    def show_chart(self):
        if self.code == 'maq' or len(self.code) == 7:
            indicator = self.indicator if self.indicator in g_market_indicators else g_market_indicators[0]
        else:
            indicator = self.indicator if self.indicator in g_indicators else g_indicators[0]
        logger.info('{} {} {}'.format(self.code, self.period, indicator))
        # TODO multiprocessing 不支持, threading 打开图时会重新打开之前关闭的图
        # p = multiprocessing.Process(target=chart.open_graph, args=(self.code, self.period, indicator))
        # p = threading.Thread(target=chart.open_graph, args=(self.code, self.period, indicator))
        # p.start()
        # p.join(timeout=1)
        util.run_subprocess('chart.py', [self.code, self.period, indicator])
        # open_graph(self.code, self.period)

    def show_f10(self):
        code = self.code
        url = 'http://basic.10jqka.com.cn/' + code
        cmd = ['/usr/bin/browser', '--tabs', url]
        subprocess.Popen(cmd)

    def show_indicator(self):
        logger.info('{} {}'.format(self.code, self.period))
        p = multiprocessing.Process(target=chart.show_indicator,
                                    args=(self.code, self.period, relative_price_strength.relative_price_strength))
        p.start()
        p.join(timeout=1)

    def show_market(self):
        logger.info('{} {}'.format(self.code, self.period))
        indicator = self.indicator if self.indicator in g_market_indicators else g_market_indicators[0]
        p = multiprocessing.Process(target=chart.show_market, args=(self.period, indicator))
        p.start()
        p.join(timeout=1)

    def control_watch_dog(self):
        with self.rlock:
            pid = util.get_pid_of_python_proc('watch_dog')
            # if self.btn_monitor.isChecked():
            if pid > 0:
                logger.info('stop watch dog')
                self.btn_monitor.setStyleSheet("background-color : red")
                # self.btn_monitor.setCheckable(False)
                # self.monitor_proc.terminate()
                # self.monitor_proc.join()
                # self.monitor_proc = None
                # os.kill(pid, signal.CTRL_C_EVENT)
                psutil.Process(pid=pid).terminate()
            else:
                logger.info('start watch dog')
                self.btn_monitor.setStyleSheet("background-color : green")
                # self.btn_monitor.setCheckable(True)
                # self.monitor_proc = multiprocessing.Process(target=watch_dog.monitor, args=())
                # self.monitor_proc.start()

                util.run_subprocess('watch_dog.py')

    def update_quote(self):
        p = multiprocessing.Process(target=acquire.save_quote, args=())
        p.start()
        logger.info('update quote started')

    def sync(self):
        p = multiprocessing.Process(target=trade_manager.sync, args=())
        p.start()
        logger.info('sync started')

    def update_candidate(self):
        logger.info('update candidate started')
        selected_list = [s.text() for s in self.combo_candidate.get_selected()]
        logger.info(selected_list)
        p = multiprocessing.Process(target=selector.update_candidate_pool, args=(selected_list, self.period))
        p.start()

    def update_traced(self):
        logger.info('update traced started')
        traced_list = [s.text() for s in self.combo_traced.get_selected()]
        candidate_list = [s.text() for s in self.combo_candidate.get_selected()]
        logger.info('{} {}'.format(candidate_list, traced_list))
        p = multiprocessing.Process(target=selector.select, args=(traced_list, candidate_list, self.period))
        p.start()

    def scan(self):
        logger.info('scan started')
        strategy_name_list = [s.text() for s in self.combo_strategy.get_selected()]
        traced_list = [s.text() for s in self.combo_traced.get_selected()]
        candidate_list = [s.text() for s in self.combo_candidate.get_selected()] if not traced_list else []

        logger.info('candidate: {}, traced: {}, strategy: {}'.format(candidate_list, traced_list, strategy_name_list))
        p = multiprocessing.Process(target=selector.select,
                                    args=(strategy_name_list, candidate_list, traced_list, self.period))
        p.start()

        # with multiprocessing.Manager() as manager:
        #     l = manager.list()
        #     p = multiprocessing.Process(target=selector.select, args=(strategy_name_list, l))
        #     p.start()
        #     p.join()

    def buy(self):
        supplemental_signal_path = config.supplemental_signal_path
        write_supplemental_signal(supplemental_signal_path, self.code, datetime.datetime.now(), 'B', self.period, 0)
        quote = tx.get_realtime_data_sina(self.code)
        if not isinstance(quote, pandas.DataFrame) or quote.empty:
            qt_util.popup_warning_message_box_mp('获取行情数据失败 [{}]'.format(self.code))
            return

        trade_manager.buy(self.account_id, self.op_type, self.code,
                          price_trade=quote['close'][-1],
                          price_limited=int(self.count_or_price[0]),
                          count=int(self.count_or_price[1]),
                          period=self.period,
                          auto=True)

    def sell(self):
        supplemental_signal_path = config.supplemental_signal_path
        write_supplemental_signal(supplemental_signal_path, self.code, datetime.datetime.now(), 'S', self.period, 0)
        quote = tx.get_realtime_data_sina(self.code)
        if not isinstance(quote, pandas.DataFrame) or quote.empty:
            qt_util.popup_warning_message_box_mp('获取行情数据失败 [{}]'.format(self.code))
            return

        trade_manager.sell(self.account_id, self.op_type, self.code,
                           price_trade=quote['close'][-1],
                           price_limited=int(self.count_or_price[0]),
                           count=int(self.count_or_price[1]),
                           period=self.period,
                           auto=True)

    def new_trade_order(self):
        strategys = self.combo_strategy.get_selected()
        if len(strategys) > 1:
            qt_util.popup_info_message_box_mp('more than one strategy[{}] selected'.format(strategys))
            return
        if not strategys:
            qt_util.popup_info_message_box_mp('must select one and only one strategy')
            return
        strategy = '{}_signal_enter'.format(strategys[0])
        trade_manager.create_trade_order(self.account_id, self.code, self.count_or_price[0], strategy)

    def refresh_log(self):
        lines = util.read_last_lines('log/run.log')
        # print(self.log.verticalScrollBar().value(), self.log.verticalScrollBar().cursor().pos())
        offset = (self.log.verticalOffset() == 460 and self.log.horizontalOffset() == 0)
        if self.log.count() == 0 or (offset and lines != self.log_lines):
            self.log.clear()
            self.log.addItems([line[:-1] for line in lines])
            self.log.setCurrentRow(self.log.count() - 1)

            # QTextBrowser
            # self.log.setText(''.join(lines))
            # self.log.ensureCursorVisible()  # 游标可用
            # cursor = self.log.textCursor()  # 设置游标
            # pos = len(self.log.toPlainText())  # 获取文本尾部的位置
            # cursor.setPosition(pos - 1)  # 游标位置设置为尾部
            # self.log.setTextCursor(cursor)  # 滚动到游标位置

    def check(self):
        latest_sync_date = trade_manager.db_handler.query_money(self.account_id).date
        logger.info('account: {}'.format(latest_sync_date))

        trade_date = dt.get_trade_date()
        count = quote_db.get_quote_count(trade_date)
        logger.info('quote: {}   {}'.format(trade_date, count))

        quote_updated = count > 4000
        account_updated = latest_sync_date == trade_date

        pid_prev_check = None
        update_time = datetime.datetime(2021, 6, 18, 0, 0, 0)

        while self.running:
            self.send_key_event('xxx')
            now = datetime.datetime.now()
            if now - update_time > datetime.timedelta(seconds=60):
                if not account_updated and not dt.istradetime():
                    self.btn_sync.setStyleSheet("color : red")
                    latest_sync_date = trade_manager.db_handler.query_money(self.account_id).date
                    account_updated = latest_sync_date == trade_date
                else:
                    self.btn_sync.setStyleSheet("color : black")

                if not quote_updated and not dt.istradetime():
                    self.btn_update_quote.setStyleSheet("color : red")
                    # latest_quote_date = quote_db.get_latest_trade_date()
                    # quote_updated = latest_quote_date == trade_date
                    count = quote_db.get_quote_count(trade_date)
                    quote_updated = count > 4000
                else:
                    self.btn_update_quote.setStyleSheet("color : black")

                asset = trade_manager.db_handler.query_money(self.account_id)
                self.lbl_account.setText('{}%'.format(asset.position_percent))
                if asset.position_percent > 80:
                    self.lbl_account.setStyleSheet("background-color : red")
                    # self.lbl_account.setStyleSheet("color : red")

                update_time = now

            pid = util.get_pid_of_python_proc('watch_dog')
            if pid == pid_prev_check:
                time.sleep(3)
                continue

            pid_prev_check = pid
            txt = 'watch dog'
            if pid < 0:
                color = 'red'
            else:
                color = 'green'

            logger.info('check watch dog', color)
            with self.rlock:
                self.btn_monitor.setText(txt)
                self.btn_monitor.setStyleSheet("background-color : {}".format(color))

        logger.info('check thread exit')

    def stop_check_thread(self):
        ex.running = False

    def stop_watch_dog(self):
        pid = util.get_pid_of_python_proc('watch_dog')
        if pid > 0:
            logger.info('send signal.CTRL_C_EVENT')
            os.kill(pid, signal.CTRL_C_EVENT)
            # psutil.Process(pid).terminate()

    def location_on_the_screen(self):
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = self.geometry()
        x = ag.width() - widget.width() - 30
        y = 2 * ag.height() - sg.height() - widget.height() - 50

        x = 0
        y = 100
        self.move(x, y)


if __name__ == '__main__':
    me = singleten.SingleInstance()

    app = QApplication(sys.argv)

    # ex = Main()
    # ex = Widget()
    ex = Panel()
    ex.location_on_the_screen()
    logger.info('width: {}\theight: {}'.format(ex.width(), ex.height()))

    rc = app.exec_()
    ex.stop_check_thread()
    ex.stop_watch_dog()

    sys.exit(rc)
