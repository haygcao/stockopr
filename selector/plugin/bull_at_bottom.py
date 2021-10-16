# -*- encoding: utf-8 -*-

"""
最近波动大, 但涨幅不大
"""

import numpy


def one_day(close, ad, back_day):
    # 最近15天, 至少3天涨幅超7%
    n = numpy.count_nonzero(ad[-15 - back_day:-back_day] > 0.07)
    if n < 3:
        return False

    # 最近15天, 至少1天跌幅超4%
    n = numpy.count_nonzero(ad[-15 - back_day:-back_day] < -0.04)
    if n < 1:
        return False

    # 最近15天, 振幅不超过 30%
    max_ = numpy.max(close[-15 - back_day:-back_day])
    min_ = numpy.min(close[-15 - back_day:-back_day])
    if max_/min_ - 1 > 0.3:
        return False

    # 最近60天, 涨幅不超过30%
    min_ = numpy.min(close[-60 - back_day:-back_day])
    if max_/min_ - 1 > 0.3:
        return False

    return True


def bull_at_bottom(quote, period, back_days=10):
    close = quote['close']
    close_shift = quote['close'].shift(periods=1)
    ad = close / close_shift - 1

    for back_day in range(0, back_days):
        if one_day(close, ad, back_day):
            return True

    return False
