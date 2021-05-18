# -*- coding: utf-8 -*-
import numpy

from config.config import is_long_period
from indicator import force_index, dynamical_system


def function_enter(low, dlxt_long_period, dlxt,  dlxt_ema13, force_index, force_index_shift, period):
    if dlxt_long_period < 0 or dlxt < 0:
        return numpy.nan

    # ema13 向上, 强力指数下穿 0
    if dlxt_ema13 and force_index_shift >= 0 and force_index < 0:   # and dlxt > 0:
        return low

    # ema13 向上, 强力指数为负, 且开始变大
    if dlxt_ema13 and force_index_shift < 0 and force_index > force_index_shift:   # and dlxt > 0:
        return low

    return numpy.nan


def function_exit(high, dlxt_long_period, dlxt, force_index, force_index_shift, period):
    # 暂时不考虑做空, 即长周期动量为红色时, 是处于空仓状态的
    if dlxt_long_period < 0:
        return numpy.nan

    # if dlxt == 0 and 0 < force_index < force_index_shift:
    #     return high

    return numpy.nan


def compute_index(quote, period=None):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    # 强力指数
    n = 13 if is_long_period(period) else 2
    quote = force_index.force_index(quote, n=n)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'force_index_shift'] = quote['force_index'].shift(periods=1)

    return quote_copy


def signal_enter(quote, period=None):
    if is_long_period(period):
        quote = quote.assign(force_index_signal_enter=numpy.nan)
        return quote

    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'force_index_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(
            x.low, x.dlxt_long_period, x.dlxt, x.dlxt_ema13, x.force_index, x.force_index_shift, period), axis=1)

    # remove temp data
    quote_copy.drop(['force_index_shift'], axis=1)

    return quote_copy


def signal_exit(quote, period=None):
    if is_long_period(period):
        quote = quote.assign(force_index_signal_exit=numpy.nan)
        return quote

    # 长中周期动力系统中，波段操作时只要有一个变为红色，短线则任一变为蓝色
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'force_index_signal_exit'] = quote.apply(
        lambda x: function_exit(x.high, x.dlxt_long_period, x.dlxt, x.force_index, x.force_index_shift, period), axis=1)

    # remove temp data
    quote_copy.drop(['force_index_shift'], axis=1)

    return quote_copy


if __name__ == '__main__':
    signal_exit()
