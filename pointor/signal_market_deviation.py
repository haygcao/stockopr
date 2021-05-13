# -*- coding: utf-8 -*-
import numpy

from selector.plugin import market_deviation


def compute_index(quote, period):
    back_days = 150  # 125
    for back_day in range(back_days, 0, -1):
        quote = market_deviation.market_deviation_macd(quote, back_day)
        # quote = market_deviation.bear_deviation_macd(quote, back_day)
        quote = market_deviation.market_deviation_force_index(quote, back_day, period)
        # quote = market_deviation.bear_deviation_force_index(quote, back_day, period)
        # bull_market_deviation = quote['macd_bull_market_deviation']

    # bull_market_deviation = quote['macd_bear_market_deviation']
    # print(bull_market_deviation[bull_market_deviation.notnull()])

    return quote


def signal(quote, period):
    quote = compute_index(quote, period)

    return quote


