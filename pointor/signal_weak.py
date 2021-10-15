# -*- coding: utf-8 -*-

import indicator.high_low
from pointor import signal_market_deviation


def signal_enter(quote, period='day', back_days=125, column=None):
    quote = indicator.high_low.compute_high_low(quote, column='close', compute_high=False, weak=True)  # 'low'

    high_low_column = 'weak_bull'
    quote = signal_market_deviation.signal_one(quote, quote[high_low_column], high_low_column, weak=True)

    return quote


def signal_exit(quote, period='day', back_days=125, column=None):
    quote = indicator.high_low.compute_high_low(quote, column='close', compute_high=True, weak=True)  # 'high'

    high_low_column = 'weak_bear'
    quote = signal_market_deviation.signal_one(quote, quote[high_low_column], high_low_column, weak=True)

    return quote
