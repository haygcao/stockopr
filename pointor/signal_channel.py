# -*- coding: utf-8 -*-
import numpy

import indicator
from config.config import is_long_period, period_price_diff_ratio_atr_map
from indicator import dynamical_system
from util import macd


def function_enter(low, dlxt_long_period, dlxt, ema, atr, period):
    # if not is_long_period(period) and dlxt_long_period == -1:
    #     return numpy.nan

    # if dlxt == -1:
    #     if low <= ema - 3*atr:
    #         return low

    times = period_price_diff_ratio_atr_map[period]

    if dlxt >= 0:
        if low <= ema - times * atr:
            return low

    if low <= ema - (times + 1) * atr:
        return low

    return numpy.nan


def function_exit(high, dlxt_long_period, dlxt, ema, atr, period):
    # if not is_long_period(period) and dlxt_long_period == 1:
    #     return numpy.nan

    # if dlxt == 1:
    #     if high >= ema + 3*atr:
    #         return high

    times = period_price_diff_ratio_atr_map[period]

    if dlxt <= 0:
        if high >= ema + times * atr:
            return high

    if high >= ema + (times + 1) * atr:
        return high

    return numpy.nan


def compute_index(quote, period):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    quote = indicator.atr.compute_atr(quote)
    ema26 = macd.ema(quote, 26)
    quote['ema'] = ema26

    return quote


def signal_enter(quote, period):
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'channel_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(x.low, x.dlxt_long_period, x.dlxt, x.ema, x.atr, period), axis=1)

    return quote_copy


def signal_exit(quote, period):
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'channel_signal_exit'] = quote_copy.apply(
        lambda x: function_exit(x.high, x.dlxt_long_period, x.dlxt, x.ema, x.atr, period), axis=1)

    return quote_copy

