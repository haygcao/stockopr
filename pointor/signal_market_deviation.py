# -*- coding: utf-8 -*-
import numpy

from selector.plugin import market_deviation


def compute_index(quote, period):
    back_days = 125

    for func in [market_deviation.market_deviation_macd, market_deviation.market_deviation_force_index]:
        for will in [1, -1]:
            back_day = 0
            while back_day < back_days:
                n = func(quote, back_day, period, will)
                back_day += n

    # bull_market_deviation = quote['macd_bear_market_deviation']
    # print(bull_market_deviation[bull_market_deviation.notnull()])

    return quote


def signal(quote, period):
    quote = compute_index(quote, period)

    return quote


