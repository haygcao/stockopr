# -*- coding: utf-8 -*-
import datetime
import inspect
import json
import os
import sys

import requests

from config import config
from data_structure import trade_data
from server import config as config_svr
from util.log import logger

base_url = config.get_tradeapi_server()
headers = {"Content-Type": "application/json"}


def handle_err(data):
    if 'ret_code' in data and data['ret_code'] == -1:
        return True
    return False


def get_asset(account_id):
    """
    获取资金明细
    """
    url = 'http://{}/query_money'.format(base_url)
    data = {'account_id': account_id}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    d = json.loads(response.content)
    if handle_err(d):
        logger.error(d['err_msg'], inspect.currentframe().f_code.co_name)
        return

    if account_id == config_svr.ACCOUNT_ID_XY:
        asset = trade_data.Asset(d['total_money'], d['avail_money'], d['net_money'], d['deposit'], d['market_value'])
    else:
        asset = trade_data.Asset(d['total_money'], d['avail_money'])
    return asset


def query_position(account_id, code=None):
    """
    可以卖的股数
    还可以买的股数
    """
    url = 'http://{}/query_position'.format(base_url)
    data = {
        'code': code,
        'account_id': account_id
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    json_str = response.content
    d = json.loads(json_str)
    if handle_err(d):
        logger.error(d['err_msg'], inspect.currentframe().f_code.co_name)
        return

    position_list = []
    try:
        for row in d:
            position = trade_data.Position(row['code'], row['current_position'], row['avail_position'],
                                           row['price_cost'], row['price'], row['profit_total'])
            position_list.append(position)
    except Exception as e:
        print(e, json_str)
        return None

    return position_list


def query_operation_detail(account_id, code=None):
    """
    获取对账单
    """
    url = 'http://{}/query_operation_detail'.format(base_url)
    data = {
        'code': code,
        'account_id': account_id
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    d = json.loads(response.content)
    if handle_err(d):
        logger.error(d['err_msg'], inspect.currentframe().f_code.co_name)
        return

    detail_list = []
    price_trade = 0
    price_limited = 0
    for row in d:
        detail = trade_data.OperationDetail(row['trade_time'], row['code'], row['price'], price_trade, price_limited,
                                            row['count'])
        detail_list.append(detail)

    return detail_list


def order(account_id, op_type, direct, code, count, price_limited=0, auto=False):
    url = 'http://{}/order'.format(base_url)
    data = {
        'account_id': account_id,
        'op_type': op_type,
        'code': code,
        'direct': direct,
        'count': count,
        'auto': auto
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.ok


def query_withdraw_order(account_id):
    """
    查询未成交的委托单
    direct: 证券买入/证券卖出
    """
    url = 'http://{}/query_withdraw_order'.format(base_url)
    data = {'account_id': account_id}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    d = json.loads(response.content)
    if handle_err(d):
        logger.error(d['err_msg'], inspect.currentframe().f_code.co_name)
        return

    order_list = []
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    for row in d:
        trade_time = datetime.datetime.strptime('{} {}'.format(today_str, row['trade_time']), '%Y-%m-%d %H:%M:%S')
        direct = 'B' if '买入' in row['direct'] else 'S'
        withdraw_order = trade_data.WithdrawOrder(trade_time, row['code'], direct, row['count_to'], row['count_ed'],
                                                  row['price_to'], row['price_ed'], row['count_withdraw'])
        order_list.append(withdraw_order)

    return order_list


def withdraw(direct):
    url = 'http://{}/withdraw'.format(base_url)
    data = {'direct': direct}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.ok


def query_today_order(account_id, code=None):
    """
    获取对账单
    """
    url = 'http://{}/query_today_order'.format(base_url)
    data = {
        'code': code,
        'account_id': account_id
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    d = json.loads(response.content)
    if handle_err(d):
        logger.error(d['err_msg'], inspect.currentframe().f_code.co_name)
        return

    order_list = []
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    for row in d:
        trade_time = datetime.datetime.strptime('{} {}'.format(today_str, row['trade_time']), '%Y-%m-%d %H:%M:%S')
        direct = 'B' if '买入' in row['direct'] else 'S'
        price_ed = round(row['amount'] / row['count_ed'], 3)
        withdraw_order = trade_data.WithdrawOrder(trade_time, row['code'], direct, row['count_to'], row['count_ed'],
                                                  row['price_to'], price_ed, row['count_withdraw'])
        order_list.append(withdraw_order)

    return order_list
