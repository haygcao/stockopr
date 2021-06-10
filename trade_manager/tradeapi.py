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


def query_position(code):
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

    try:
        d = json.loads(json_str)
        position = trade_data.Position(code, d['current_position'], d['avail_position'])
    except Exception as e:
        print(e, json_str)
        return None

    return position


def get_operation_detail():
    """
    获取对账单
    """
    url = 'http://{}/query_operation_detail'.format(base_url)
    data = {}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    return json.loads(response.content)


def order(direct, code, count, price=0, auto=False):
    url = 'http://{}/order'.format(base_url)
    data = {'code': code, 'direct': direct, 'count': count}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    return response.ok
