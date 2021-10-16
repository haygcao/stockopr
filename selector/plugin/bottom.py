# -*- encoding: utf-8 -*-
import numpy


def compute_bottom(quote):
    # 120日高点
    ma_max = quote.high.rolling(60).max()
    # 120日低点
    ma_min = quote.low.rolling(60).min()

    # 跌幅超70%
    percent = 100 * (1 - ma_min / ma_max)
    percent = percent.rolling(5).max()
    mask1 = (percent > 70)

    # 当前涨幅 < 30%, 且 > 15%
    percent = 100 * (quote.close / ma_min - 1)
    percent = percent.rolling(5).max()
    mask2 = (percent < 30) & (percent > 15)

    quote = quote.assign(bottom=(mask1 & mask2))

    return quote


def bottom(quote, period, back_days=10):
    quote = compute_bottom(quote)

    return numpy.any(quote.bottom[-back_days:])
