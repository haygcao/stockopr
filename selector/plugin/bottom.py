# -*- encoding: utf-8 -*-

import numpy


def compute_bottom(quote, n1, n2, percent_down):
    # N日高点
    ma_max = quote.high.rolling(n1).max()
    # N日低点
    ma_min = quote.low.rolling(n2).min()

    # 跌幅超70%
    percent = 100 * (1 - ma_min / ma_max)
    percent = percent.rolling(5).max()
    mask1 = (percent > percent_down)

    # 当前涨幅 < 30%, 且 > 15%
    percent = 100 * (quote.close / ma_min - 1)
    percent = percent.rolling(5).max()
    mask2 = (percent < 30) & (percent > 15)

    quote = quote.assign(bottom=(mask1 & mask2))

    return quote


def bottom(quote, period, back_days):
    back_days = 10

    # 长期大底
    n1 = 750
    n2 = 30
    percent_des = 70

    quote = compute_bottom(quote, n1, n2, percent_des)

    return numpy.any(quote.bottom[-back_days:])


def fallen(quote, period, back_days=10):
    # 短时间内, 快速下跌
    n1 = 20
    n2 = 20
    percent_des = 50

    quote = compute_bottom(quote, n1, n2, percent_des)

    return numpy.any(quote.bottom[-back_days:])
