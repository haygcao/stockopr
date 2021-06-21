# -*- coding: utf-8 -*-
import datetime
import json
import requests

from config import config
from data_structure import trade_data

base_url = config.get_tradeapi_server()
headers = {"Content-Type": "application/json"}


def get_asset():
    """
    获取资金明细
    """
    url = 'http://{}/query_money'.format(base_url)
    data = {}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    d = json.loads(response.content)
    asset = trade_data.Asset(d['total_money'], d['avail_money'])

    return asset


def query_position(code=None):
    """
    可以卖的股数
    还可以买的股数
    """
    url = 'http://{}/query_position'.format(base_url)
    data = {'code': code}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    json_str = response.content
    if not json_str:
        return None

    position_list = []
    try:
        d = json.loads(json_str)
        for row in d:
            position = trade_data.Position(row['code'], row['current_position'], row['avail_position'],
                                           row['price_cost'], row['price'], row['profit_total'])
            position_list.append(position)
    except Exception as e:
        print(e, json_str)
        return None

    return position_list


def query_operation_detail(code=None):
    """
    获取对账单
    """
    url = 'http://{}/query_operation_detail'.format(base_url)
    data = {'code': code}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    detail_list = []
    price_trade = 0
    price_limited = 0
    for row in json.loads(response.content):
        detail = trade_data.OperationDetail(row['trade_time'], row['code'], row['price'], price_trade, price_limited,
                                            row['count'])
        detail_list.append(detail)

    return detail_list


def order(direct, code, count, price_limited=0, auto=False):
    url = 'http://{}/order'.format(base_url)
    data = {'code': code, 'direct': direct, 'count': count, 'auto': auto}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.ok


def query_withdraw_order():
    """
    查询未成交的委托单
    direct: 证券买入/证券卖出
    """
    url = 'http://{}/query_withdraw_order'.format(base_url)
    data = {}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    order_list = []
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    for row in json.loads(response.content):
        trade_time = datetime.datetime.strptime('{} {}'.format(today_str, row['trade_time']), '%Y-%m-%d %H:%M:%S')
        direct = 'B' if '买入' in row['direct'] else 'S'
        withdraw_order = trade_data.WithdrawOrder(trade_time, row['code'], direct, row['count'],
                                                  row['count_ed'], row['price'], row['price_ed'], row['count_withdraw'])
        order_list.append(withdraw_order)

    return order_list


def withdraw(direct):
    url = 'http://{}/withdraw'.format(base_url)
    data = {'direct': direct}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.ok
