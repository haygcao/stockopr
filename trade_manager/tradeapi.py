# -*- coding: utf-8 -*-
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
            position = trade_data.Position(row['code'], row['current_position'], row['avail_position'])
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
    for row in json.loads(response.content):
        detail = trade_data.OperationDetail(row['trade_time'], row['code'], row['price'], row['count'])
        detail_list.append(detail)

    return detail_list


def order(direct, code, count, price=0, auto=False):
    url = 'http://{}/order'.format(base_url)
    data = {'code': code, 'direct': direct, 'count': count, 'auto': auto}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.ok
