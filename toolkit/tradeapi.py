# -*- coding: utf-8 -*-
import psutil
import win32api

import tkinter.messagebox
import time
import pywinauto
import pywinauto.clipboard
import pywinauto.application

from data_structure import trade_data
from util import util

pos_position = (36, 258)
pos_detail = (36, 456)
pos_asset = (45, 354)
pos_buy_and_sell = (25, 159)
pos_centre = (1024, 1024)


def copy_to_clipboard():
    """
    # https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
    '+': {VK_SHIFT}
    '^': {VK_CONTROL}
    '%': {VK_MENU} a.k.a. Alt key
    """
    pywinauto.mouse.click(coords=pos_centre)
    # pywinauto.mouse.release(coords=pos_centre)
    time.sleep(0.2)

    # pywinauto.mouse.right_click(coords=pos_centre)
    # pywinauto.mouse.release(coords=pos_centre)
    # time.sleep(0.2)
    # pywinauto.keyboard.send_keys('C')

    pywinauto.keyboard.send_keys('^c')
    time.sleep(0.2)


def max_window(window):
    """
    最大化窗口
    """
    if window.get_show_state() != 3:
        window.maximize()
    window.set_focus()


class OperationThs:
    def __init__(self):
        try:
            self.__app = pywinauto.application.Application()
            self.__app.connect(title='网上股票交易系统5.0')
            top_hwnd = pywinauto.findwindows.find_window(title='网上股票交易系统5.0')
            self.__main_window = self.__app.window(handle=top_hwnd)
            self.max_window()
            return

            # pywinauto.mouse.click(coords=pos_buy_and_sell)
            # pywinauto.mouse.release(coords=pos_buy_and_sell)
            #
            # dialog_hwnd = \
            # pywinauto.findwindows.find_windows(top_level_only=False, class_name='#32770', parent=top_hwnd)[0]
            # wanted_hwnds = pywinauto.findwindows.find_windows(top_level_only=False, parent=dialog_hwnd)
            # print('wanted_hwnds length', len(wanted_hwnds))
            # if len(wanted_hwnds) == 0:
            #     tkinter.messagebox.showerror('错误', '获取[同花顺双向委托界面]的窗口句柄错误！')
            #     exit()
            #
            # self.__dialog_window = self.__app.window(handle=dialog_hwnd)
        except Exception as e:
            pass

    def __buy(self, code, quantity, price=0, auto=False):
        """买函数
        :param code: 代码， 字符串
        :param quantity: 数量， 字符串
        """
        self.__dialog_window.Edit1.set_focus()
        time.sleep(0.2)
        self.__dialog_window.Edit1.set_edit_text(code)
        time.sleep(0.2)
        if quantity != '0':
            self.__dialog_window.Edit3.set_edit_text(quantity)
            time.sleep(0.2)
        if auto:
            self.__dialog_window.Button1.click()
        time.sleep(0.2)

    def __sell(self, code, quantity, price=0, auto=False):
        """
        卖函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        self.__dialog_window.Edit4.set_focus()
        time.sleep(0.2)
        self.__dialog_window.Edit4.set_edit_text(code)
        time.sleep(0.2)
        if quantity != '0':
            self.__dialog_window.Edit6.set_edit_text(quantity)
            time.sleep(0.2)
        if auto:
            self.__dialog_window.Button2.click()
        time.sleep(0.2)

    def __close_popup_window(self):
        """
        关闭一个弹窗。
        :return: 如果有弹出式对话框，返回True，否则返回False
        """
        popup_hwnd = self.__main_window.popup_window()
        if popup_hwnd:
            popup_window = self.__app.window(handle=popup_hwnd)
            popup_window.SetFocus()
            popup_window.Button.Click()
            return True
        return False

    def __close_popup_windows(self):
        """
        关闭多个弹出窗口
        :return:
        """
        while self.__close_popup_window():
            time.sleep(0.5)

    def click(self):
        pos_detail = (36, 456)
        pos_asset = (45, 354)
        pos_buy_and_sell = (25, 159)
        pass

    def order(self, code, direction, quantity):
        """
        下单函数
        :param code: 股票代码， 字符串
        :param direction: 买卖方向， 字符串
        :param quantity: 买卖数量， 字符串
        """
        if direction == 'B':
            self.__buy(code, quantity)
        if direction == 'S':
            self.__sell(code, quantity)
        self.__close_popup_windows()

    def max_window(self):
        """
        最大化窗口
        """
        if self.__main_window.get_show_state() != 3:
            self.__main_window.maximize()
        self.__main_window.set_focus()

    def min_window(self):
        """
        最小化窗体
        """
        if self.__main_window.get_show_state() != 2:
            self.__main_window.minimize()

    def refresh(self, t=0.5):
        """
        点击刷新按钮
        :param t:刷新后的等待时间
        """
        self.__dialog_window.Button5.click()
        time.sleep(t)

    def get_asset(self):
        """
        获取资金明细
        """
        # return float(self.__dialog_window.Static19.WindowText())
        column = ['资金帐户', '银行名称', '币种', '资金余额', '可用资金', '可取资金', '交易冻结', '委托买入冻结金额', '证券市值', '多金融产品市值', '现金资产', '总资产', '预计利息', '利息税']
        pywinauto.mouse.click(coords=pos_asset)
        # pywinauto.mouse.release(coords=pos_asset)
        time.sleep(0.2)
        copy_to_clipboard()

        asset_list = []
        data = pywinauto.clipboard.GetData()
        for row in self.__clean_clipboard_data(data, cols=14):
            asset = trade_data.Asset(float(row[column.index('总资产')]), float(row[4]))
            # asset.total_money = row[3]
            # asset.avail_money = row[4]
            asset_list.append(asset)

        return asset_list

    def get_operation_detail(self):
        """
        获取对账单
        """
        column = ['成交时间', '发生日期', '证券代码', '证券名称', '业务名称', '发生金额', '资金本次余额', '股份余额', '成交数量', '成交价格', '成交金额', '手续费', '印花税', '附加费', '委托编号', '股东代码', '币种', '过户费', '交易所清算费', '资金帐号', '备注']

        pywinauto.mouse.click(coords=pos_detail)
        # pywinauto.mouse.release(coords=pos_detail)
        time.sleep(0.2)
        copy_to_clipboard()

        data = pywinauto.clipboard.GetData()
        return self.__clean_clipboard_data(data, cols=21)

    @staticmethod
    def __clean_clipboard_data(data, cols):
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

    def __copy_to_clipboard(self):
        """
        拷贝持仓信息至剪贴板
        :return:
        """
        self.__dialog_window.CVirtualGridCtrl.right_click(coords=(30, 30))
        self.__main_window.type_keys('C')
        time.sleep(0.2)

    def __get_cleaned_data(self, cols=12):
        """
        读取ListView中的信息
        :return: 清洗后的数据
        """
        self.__copy_to_clipboard()
        data = pywinauto.clipboard.GetData()
        return self.__clean_clipboard_data(data, cols)

    def __select_window(self, choice):
        """
        选择tab窗口信息
        :param choice: 选择个标签页。持仓，撤单，委托，成交
        :return:
        """
        rect = self.__dialog_window.CCustomTabCtrl.client_rect()
        x = rect.width() // 8
        y = rect.height() // 2
        if choice == 'W':
            x = x
        elif choice == 'E':
            x *= 3
        elif choice == 'R':
            x *= 5
        elif choice == 'A':
            x *= 7
        self.__dialog_window.CCustomTabCtrl.click_input(coords=(x, y))
        time.sleep(0.5)

    def __get_info(self, choice):
        """
        获取股票信息
        """
        self.__select_window(choice=choice)
        return self.__get_cleaned_data()

    def get_position(self):
        """
        获取持仓
        :return:
        """
        columns = ['证券代码', '证券名称', '股份余额', '实际数量', '可用股份', '冻结数量', '成本价1', '当前价', '浮动盈亏', '盈亏比例(%)', '最新市值', '交易市场']
        pywinauto.mouse.click(coords=pos_position)
        # pywinauto.mouse.release(coords=pos_asset)
        time.sleep(0.2)
        copy_to_clipboard()

        position_list = []
        data = pywinauto.clipboard.GetData()
        for row in self.__clean_clipboard_data(data, cols=12):
            current_position = int(float(row[3]))
            avail_position = int(float(row[4]))

            position = trade_data.Position(row[0], current_position, avail_position)

            position_list.append(position)

        return position_list

    @staticmethod
    def get_deal(code, pre_position, cur_position):
        """
        获取成交数量
        :param code: 需检查的股票代码， 字符串
        :param pre_position: 下单前的持仓
        :param cur_position: 下单后的持仓
        :return: 0-未成交， 正整数是买入的数量， 负整数是卖出的数量
        """
        column = ['成交时间', '证券代码', '证券名称', '买卖', '成交数量', '成交价格', '成交金额', '委托编号', '成交编号']
        column = ['委托时间', '证券代码', '证券名称', '买卖', '委托状态', '委托数量', '成交数量', '委托价格', '成交价格', '已撤数量', '合同编号', '交易市场', '股东代码']
        if pre_position == cur_position:
            return 0
        pre_len = len(pre_position)
        cur_len = len(cur_position)
        index_position = 2
        if pre_len == cur_len:
            for row in range(cur_len):
                if cur_position[row][0] == code:
                    return int(float(cur_position[row][index_position]) - float(pre_position[row][index_position]))
        if cur_len > pre_len:
            return int(float(cur_position[-1][index_position]))

    def withdraw(self, code, direction):
        """
        指定撤单
        :param code: 股票代码
        :param direction: 方向 B， S
        :return:
        """
        row_pos = []
        info = self.__get_info(choice='R')
        if direction == 'B':
            direction = '买入'
        elif direction == 'S':
            direction = '卖出'
        if info:
            for index, element in enumerate(info):
                if element[0] == code:
                    if element[1] == direction:
                        row_pos.append(index)
        if row_pos:
            for row in row_pos:
                self.__dialog_window.CVirtualGridCtrl.ClickInput(coords=(7, 28 + 16 * row))
            self.__dialog_window.Button12.Click()
            self.__close_popup_windows()

    def withdraw_buy(self):
        """
        撤买
        :return:
        """
        self.__select_window(choice='R')
        self.__dialog_window.Button8.Click()
        self.__close_popup_windows()

    def withdraw_sell(self):
        """
        撤卖
        :return:
        """
        self.__select_window(choice='R')
        self.__dialog_window.Button9.Click()
        self.__close_popup_windows()

    def withdraw_all(self):
        """
        全撤
        :return:
        """
        self.__select_window(choice='R')
        self.__dialog_window.Button7.Click()
        self.__close_popup_windows()


def get_screen_size():
    return win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)


def get_cursor_pos():
    return win32api.GetCursorPos()


def order(direct, code, count, price=0, auto=False):
    pid = util.get_pid_by_exec('C:\\同花顺软件\\同花顺\\xiadan.exe')

    if pid < 0:
        app = pywinauto.Application(backend="win32").start('C:\\同花顺软件\\同花顺\\xiadan.exe')
    else:
        app = pywinauto.Application(backend="win32").connect(process=pid)

    main_window = app.window(title='网上股票交易系统5.0')
    max_window(main_window)

    # time.sleep(0.5)
    # pywinauto.mouse.click(coords=pos_asset)
    # time.sleep(0.2)

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
