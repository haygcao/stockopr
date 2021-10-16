# -*- coding: utf-8 -*-

import config.config as config
from acquisition import basic
from indicator import ma


def gen_ma(quote, n=config.MA_NUM, l=config.MAS):
    r = []
    for i in range(n):
        r.append(ma.ma(quote['close'], l[i]))

    return r


def filter_quote(quote):
    if quote.empty:
        return True

    name = basic.get_stock_name(quote['code'][-1])
    if '退市' in name:  # or 'ST' in name:
        return True

    min_days = config.WEEK_MIN * 5 if config.USING_LONG_PERIOD else config.DAY_MIN
    if len(quote) < min_days:
        return True

    return False


def filer_code(code):
    if basic.sum_trade_date(code) < config.MIN:
        return True
    return False


def verify(code, dt=True):
    pass


def print_time(cost):
    if int(cost/5) == 0:
        print(cost)


def print_line(a):
    if a % 100 == 0:
        n = int(a/100)
        print('{0}'.format('-'*n))
