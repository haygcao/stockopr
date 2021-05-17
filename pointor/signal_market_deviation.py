# -*- coding: utf-8 -*-
import numpy

from selector.plugin import market_deviation


def compute_index(quote, period, back_days):
    for func in [market_deviation.market_deviation_force_index, market_deviation.market_deviation_macd]:
        for will in [1, -1]:
            back_day = 0
            while back_day <= back_days:
                quote, n = func(quote, back_day, period, will)
                back_day += n

    # bull_market_deviation = quote['macd_bear_market_deviation']
    # print(bull_market_deviation[bull_market_deviation.notnull()])

    return quote


def signal(quote, period, back_days=125):
    quote = compute_index(quote, period, back_days)

    return quote


