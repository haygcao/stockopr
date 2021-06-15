# -*- coding: utf-8 -*-
import datetime

import psutil
import win32api

import time
import pywinauto
import pywinauto.clipboard
import pywinauto.application

from ..config import pos_centre, pos_asset, pos_position, pos_detail

g_main_window = None


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

    g_main_window = main_window

    return main_window
    

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


def get_asset():
    """
    获取资金明细
    """
    active_window()

    columns = ['资金帐户', '银行名称', '币种', '资金余额', '可用资金', '可取资金', '交易冻结', '委托买入冻结金额', '证券市值', '多金融产品市值', '现金资产', '总资产', '预计利息', '利息税']
    columns = ['资金帐户', '银行名称', '币种', '资金余额', '可用资金', '可取资金', '交易冻结', '委托买入冻结金额', '证券市值', '多金融产品市值', '现金资产', '总资产', '预计利息', '利息税']
    pywinauto.mouse.click(coords=pos_asset)
    # pywinauto.mouse.release(coords=pos_asset)
    time.sleep(0.2)
    copy_to_clipboard()

    data = pywinauto.clipboard.GetData()
    for row in clean_clipboard_data(data, cols=len(columns)):
        return {'total_money': float(row[columns.index('总资产')]), 'avail_money': float(row[columns.index('可用资金')])}


def get_positions():
    """
    获取持仓
    :return:
    """
    active_window()
    
    columns = ['证券代码', '证券名称', '股份余额', '实际数量', '可用股份', '冻结数量', '成本价1', '当前价', '浮动盈亏', '盈亏比例(%)', '最新市值', '交易市场']
    columns = ['证券代码', '证券名称', '股份余额', '实际数量', '可用股份', '冻结数量', '成本价1', '当前价', '浮动盈亏', '盈亏比例(%)', '当日盈亏', '当日盈亏比(%)', '最新市值', '仓位占比(%)', '交易市场']
    pywinauto.mouse.click(coords=pos_position)
    # pywinauto.mouse.release(coords=pos_asset)
    time.sleep(0.2)
    copy_to_clipboard()

    position_list = []
    data = pywinauto.clipboard.GetData()
    for row in clean_clipboard_data(data, cols=len(columns)):
        current_position = int(float(row[columns.index('股份余额')]))
        avail_position = int(float(row[columns.index('可用股份')]))

        # position = n.Position(row[0], current_position, avail_position)
        position = {'code': row[0], 'current_position': current_position, 'avail_position': avail_position}

        position_list.append(position)

    return position_list


def query_position(code):
    """
    可以卖的股数
    还可以买的股数
    """
    active_window()
    
    position_list = get_positions()
    for position in position_list:
        if position['code'] != code:
            continue
        return position


def get_operation_detail(code_in=None):
    """
    获取对账单
    """
    active_window()
    
    columns = ['成交时间', '发生日期', '证券代码', '证券名称', '业务名称', '发生金额', '资金本次余额', '股份余额', '成交数量', '成交价格', '成交金额', '手续费', '印花税', '附加费', '委托编号', '股东代码', '币种', '过户费', '交易所清算费', '资金帐号', '备注', '费用备注']
    pywinauto.mouse.click(coords=pos_detail)
    # pywinauto.mouse.release(coords=pos_detail)
    time.sleep(0.2)
    copy_to_clipboard()

    data = pywinauto.clipboard.GetData()
    end_pos = data.find('\n')
    columns = data[:end_pos].split()
    # val_1st_row = data[end_pos + 1: end_pos + 1 + data[end_pos + 1:].find('\n')].split()

    detail_list = []
    for i, row_str in enumerate(data.split('\n')):
        if i == 0:
            continue
        row = row_str.split('\t')
        code = row[columns.index('证券代码')]
        if not code:
            continue

        if code_in and code_in != code:
            continue
        trade_time = row[columns.index('成交时间')]
        trade_date = row[columns.index('发生日期')]
        trade_time = datetime.datetime.strptime('{} {}'.format(trade_date, trade_time), '%Y%m%d %H:%M:%S')
        price = float(row[columns.index('成交价格')])
        count = int(float(row[columns.index('成交数量')]))

        detail = {
            'trade_time': trade_time.strftime('%Y-%m-%d %H:%M:%S'),
            'code': code,
            'price': price,
            'count': count
        }

        detail_list.append(detail)
    for row in data.split('\n'):
        val_list = row.split('\t')

    return detail_list


def order(direct, code, count, price=0, auto=False):
    main_window = active_window()

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
