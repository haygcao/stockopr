# -*- coding: utf-8 -*-
"""
网上股票交易系统5.0
[快速交易]
自动弹出窗口停留时间(秒)
是否弹出成交回报提示窗口
撤单前是否需要确认
委托前是否需要确认
委托成功后是否弹出提示对话框

[界面设置]
下单窗口总在最前面
查询界面自动刷新时间(秒)
显示悬浮工具栏

"""
import datetime
import os
import pathlib

import psutil
import win32api

import time
import pywinauto
import pywinauto.clipboard
import pywinauto.application

from . import helper
from .. import config


g_main_window = None


def refresh():
    pywinauto.mouse.click(coords=config.pos_refresh)
    time.sleep(0.5)


def scroll_top():
    # pywinauto.mouse.press(coords=config.pos_down_arrow)
    pywinauto.mouse.press(coords=config.pos_scroll_middle)
    # time.sleep(0.1)
    pywinauto.mouse.release(coords=config.pos_up_arrow)


def scroll_bottom():
    # pywinauto.mouse.press(coords=config.pos_down_arrow)
    pywinauto.mouse.press(coords=config.pos_scroll_middle)
    # time.sleep(0.1)
    pywinauto.mouse.release(coords=config.pos_down_arrow)


def unfold_gui():
    root_dir = os.path.join(os.path.dirname(__file__), '..')
    root_dir = os.path.abspath(root_dir)
    tmp = os.path.join(root_dir, 'unfold_gui.txt')
    path = pathlib.Path(tmp)
    today = datetime.date.today()
    if path.exists() and datetime.datetime.fromtimestamp(path.stat().st_mtime).date() == today:
        return
    with open(tmp, 'w') as f:
        f.write(str(today))

    pywinauto.mouse.click(coords=config.pos_dbp)
    pywinauto.mouse.click(coords=config.pos_rz)
    pywinauto.mouse.click(coords=config.pos_rz2)
    pywinauto.mouse.click(coords=config.pos_rq)
    pywinauto.mouse.click(coords=config.pos_rq2)

    pywinauto.keyboard.send_keys('{F4}')


def active_sub_window(op_type, direct, main_window):
    if op_type == config.OP_TYPE_DBP:
        hotkey_buy = '{F1}'
        hotkey_sell = '{F2}'
        if direct == 'B':
            main_window.type_keys(hotkey_sell)
            main_window.type_keys(hotkey_buy)
        else:
            main_window.type_keys(hotkey_buy)
            main_window.type_keys(hotkey_sell)
        return

    if op_type == config.OP_TYPE_RZ:
        pos = config.pos_rz_buy if direct == 'B' else config.pos_rz_sell
    else:
        pos = config.pos_rq_buy if direct == 'B' else config.pos_rq_sell

    pywinauto.mouse.click(coords=pos)


def get_order():
    """
    获取未成交的委托
    """
    main_window = helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()

    columns = ['委托时间', '证券代码', '证券名称', '买卖', '委托状态', '委托数量', '成交数量', '委托价格', '成交价格', '已撤数量', '合同编号', '交易市场', '股东代码']

    main_window.type_keys('{F3}')
    # time.sleep(0.2)
    # refresh()

    helper.copy_to_clipboard()

    data = pywinauto.clipboard.GetData()
    end_pos = data.find('\n')
    columns = data[:end_pos].split()

    order_list = []
    for i, row_str in enumerate(data.split('\n')):
        if i == 0:
            continue
        row = row_str.split('\t')
        order_list.append({
            'trade_time': row[columns.index('委托时间')],
            'code': row[columns.index('证券代码')],
            'direct': row[columns.index('买卖')],  # 买卖标志
            'count_to': int(row[columns.index('委托数量')]),
            'count_ed': int(row[columns.index('成交数量')]),
            'price_to': float(row[columns.index('委托价格')]),
            'price_ed': float(row[columns.index('成交价格')]),  # 成交均价
            'amount': float(row[columns.index('成交金额')]),
            'count_withdraw': int(row[columns.index('已撤数量')]),
            'status': row[columns.index('委托状态')]
        })
    return order_list


def get_asset_old():
    """
    获取资金明细
    """
    helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()
    scroll_bottom()
    for i in range(3):
        # time.sleep(0.1)
        pywinauto.mouse.click(coords=config.pos_up_arrow)
    # time.sleep(0.3)

    columns = ['发生日期', '成交时间', '业务名称', '证券代码', '证券名称', '成交价格', '成交数量', '成交金额', '股份余额', '手续费', '印花税', '过户费', '交易所清算费',
               '发生金额', '资金本次余额', '委托编号', '股东代码', '资金帐号', '币种']

    pywinauto.mouse.click(coords=config.pos_asset_cre)
    # pywinauto.mouse.release(coords=pos_asset)
    # time.sleep(0.2)
    # refresh()

    helper.copy_to_clipboard()

    scroll_top()

    data = pywinauto.clipboard.GetData()
    end_pos = data.find('\n')
    columns = data[:end_pos].split()
    # val_1st_row = data[end_pos + 1: end_pos + 1 + data[end_pos + 1:].find('\n')].split()

    for i, row_str in enumerate(data.split('\n')):
        if i == 0:
            continue
        row = row_str.split('\t')
        item_total_money = '信用资产账户总资产'
        item_avail_money = '可用金额'
        item_market_value = '参考市值'
        return {
            'total_money': float(row[columns.index(item_total_money)]),
            'avail_money': float(row[columns.index(item_avail_money)]),
            # TODO
            'net_money': 0,
            'deposit': 0,
            'market_value': float(row[columns.index(item_market_value)])
        }


def get_asset():
    """
    获取资金明细
    """
    helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()

    pywinauto.keyboard.send_keys('{F4}')

    r = {}
    pos_list = [config.pos_asset_asset_cre, config.pos_asset_money_cre]
    for index, pos in enumerate(pos_list):
        helper.copy_to_clipboard(pos)

        data = pywinauto.clipboard.GetData()
        end_pos = data.find('\n')
        columns = data[:end_pos].split()
        # val_1st_row = data[end_pos + 1: end_pos + 1 + data[end_pos + 1:].find('\n')].split()

        arr = data.split('\n')[1:]

        d = {
            '总资产': -1,
            '净资产': -2,
            '标的券市值': 0,
            '参考市值': 1,
            '两融总负债': 6,
            '两融总盈亏': 7,

            '可用保证金': 3,
            '可用金额': 4,
        }

        if index == 0:
            r.update({
                'total_money': float(arr[d['总资产']].split('\t')[1]),
                'net_money': float(arr[d['净资产']].split('\t')[1]),
                'market_value': float(arr[d['参考市值']].split('\t')[1]),
                'market_value_r': float(arr[d['标的券市值']].split('\t')[1]),
                'debt': float(arr[d['两融总负债']].split('\t')[1]),
                'debt_profit': float(arr[d['两融总盈亏']].split('\t')[1]),
            })
        else:
            r.update({
                'avail_money': float(arr[d['可用金额']].split('\t')[1]),
                'deposit': float(arr[d['可用保证金']].split('\t')[1]),
            })
    return r


def get_positions():
    """
    获取持仓
    :return:
    """
    helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()

    columns = ['证券代码', '证券名称', '可用股份', '股份余额', '当前价', '浮动盈亏', '盈亏比例(%)', '最新市值', '交易市场', '股东代码', '参考持股', '成本价', '当前成本', '冻结数量', '卖出成交数量', '在途股份(买入成交)', '资金帐户']
    # pywinauto.mouse.click(coords=pos_position)
    # pywinauto.mouse.release(coords=pos_asset)
    pywinauto.keyboard.send_keys('{F4}')
    # time.sleep(0.2)
    # refresh()

    helper.copy_to_clipboard()

    position_list = []
    data = pywinauto.clipboard.GetData()
    end_pos = data.find('\n')
    columns = data[:end_pos].split()
    # val_1st_row = data[end_pos + 1: end_pos + 1 + data[end_pos + 1:].find('\n')].split()

    detail_list = []
    for i, row_str in enumerate(data.split('\n')):
        if i == 0:
            continue
        row = row_str.split('\t')
        current_position = int(float(row[columns.index('股份余额')]))
        avail_position = int(float(row[columns.index('可用股份')]))
        price = float(row[columns.index('当前价')])
        price_cost = float(row[columns.index('成本价')])
        profit_total = float(row[columns.index('浮动盈亏')])

        # position = n.Position(row[0], current_position, avail_position)
        position = {
            'code': row[0],
            'current_position': current_position,
            'avail_position': avail_position,
            'price': price,
            'price_cost': price_cost,
            'profit_total': profit_total
        }

        position_list.append(position)

    return position_list


def query_position(code):
    """
    可以卖的股数
    还可以买的股数
    """
    helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()

    position_list = get_positions()
    if not code:
        return position_list

    for position in position_list:
        if position['code'] != code:
            continue
        return [position]


def get_operation_detail(code_in=None):
    """
    获取对账单
    """
    helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()

    scroll_bottom()
    # time.sleep(0.3)

    columns = ['发生日期', '成交时间', '业务名称', '证券代码', '证券名称', '成交价格', '成交数量', '成交金额', '股份余额', '手续费', '印花税', '过户费', '交易所清算费', '发生金额', '资金本次余额', '委托编号', '股东代码', '资金帐号', '币种']
    pywinauto.mouse.click(coords=config.pos_detail_cre)
    # pywinauto.mouse.release(coords=pos_detail)
    # time.sleep(0.2)
    # refresh()
    # 选择开始日期
    pywinauto.mouse.click(coords=config.pos_dzd_date_down_arrow)
    pywinauto.mouse.click(coords=config.pos_dzd_date_left_up_grid)
    pywinauto.mouse.click(coords=config.pos_dzd_date_confirm)

    helper.copy_to_clipboard()

    scroll_top()

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


def get_today_order(code_in=None):
    """
    获取对账单
    """
    helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()

    pywinauto.mouse.click(coords=config.pos_order_cre)
    # refresh()

    helper.copy_to_clipboard()

    scroll_top()

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
        trade_time = row[columns.index('委托时间')]
        trade_date = datetime.date.today().strftime('%Y%m%d')  # row[columns.index('委托日期')]
        direct = row[columns.index('买卖')]
        trade_time = datetime.datetime.strptime('{} {}'.format(trade_date, trade_time), '%Y%m%d %H:%M:%S')
        price_to = float(row[columns.index('委托价格')])
        price_ed = float(row[columns.index('成交价格')])  # 成交均价
        count_to = int(float(row[columns.index('委托数量')]))
        count_ed = int(float(row[columns.index('成交数量')]))
        amount = float(row[columns.index('成交金额')])
        count_cancel = int(float(row[columns.index('已撤数量')]))
        trade_status = row[columns.index('委托状态')]

        detail = {
            'trade_time': trade_time.strftime('%Y-%m-%d %H:%M:%S'),
            'code': code,
            'direct': direct,
            'price_to': price_to,
            'price_ed': price_ed,
            'amount': amount,
            'count_to': count_to,
            'count_ed': count_ed,
            'count_withdraw': count_cancel,
            'status': trade_status
        }

        detail_list.append(detail)
    for row in data.split('\n'):
        val_list = row.split('\t')

    return detail_list


def order(op_type, direct, code, count, price=0, auto=False):
    main_window = helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)
    unfold_gui()

    # pywinauto.mouse.click(coords=pos_asset)
    # time.sleep(0.2)

    active_sub_window(op_type, direct, main_window)

    pywinauto.mouse.double_click(coords=config.pos_edit_code)
    main_window.type_keys(str(code))
    # main_window.type_keys('{TAB}')
    if price > 0:
        # time.sleep(0.2)
        pywinauto.mouse.double_click(coords=config.pos_edit_price)
        main_window.type_keys(str(price))
    # main_window.type_keys('{TAB}')
    pos = config.pos_edit_count
    if op_type == config.OP_TYPE_RZ and direct == 'S':
        pos = config.pos_edit_count_rz_sell
    elif op_type == config.OP_TYPE_RQ and direct == 'B':
        pos = config.pos_edit_count_rq_buy
    # time.sleep(0.2)
    pywinauto.mouse.double_click(coords=pos)
    main_window.type_keys(str(count))

    if auto:
        main_window.type_keys('{TAB}')
        main_window.type_keys('{ENTER}')
        # time.sleep(0.5)
        # pywinauto.keyboard.send_keys('{ENTER}')
        # time.sleep(0.5)
        # pywinauto.keyboard.send_keys('{ENTER}')


def withdraw(direct):
    pos = ()
    command = ''
    if direct == 'full':
        command = 'z'
        pos = config.pos_withdraw_all
    elif direct == 'buy':
        command = 'x'
        pos = config.pos_withdraw_buy
    elif direct == 'sell':
        command = 'c'
        pos = config.pos_withdraw_sell
    elif direct == 'last':
        command = 'g'
        pos = config.pos_withdraw_last
    else:
        print(direct, ' is unknown')
        return

    print('direct is - {}, command is - {}'.format(direct, command))

    main_window = helper.active_window()
    pywinauto.mouse.click(coords=config.pos_xy)

    main_window.type_keys('{F3}')

    time.sleep(0.2)
    pywinauto.mouse.click(coords=pos)

    # main_window.type_keys(command)
    # pywinauto.keyboard.send_keys(command)

    time.sleep(0.5)
    pywinauto.keyboard.send_keys('{ENTER}')
