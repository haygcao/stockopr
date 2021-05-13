# -*- coding: utf-8 -*-
import numpy

from selector.plugin import bull_deviation


def compute_index(quote):
    back_days = 125
    for back_day in range(back_days, 0, -1):
        quote = bull_deviation.niushibeili_macd(quote, back_day)
        bull_market_deviation = quote['macd_bull_market_deviation']

    # print(bull_market_deviation[bull_market_deviation.notnull()])

    return quote


def signal_enter(quote, period):
    quote = compute_index(quote)

    return quote


def signal_exit(quote, period):
    quote = compute_index(quote)

    return quote

