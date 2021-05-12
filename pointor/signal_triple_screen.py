# -*- coding: utf-8 -*-
import numpy

from acquisition import quote_db
from config.config import period_map
from selector.plugin import dynamical_system, force_index


def function_enter(low, dlxt_long_period, dlxt_long_period_shift, dlxt, dlxt_shift, force_index, force_index_shift,
                   period):
    # 长中周期动量系统中任一为红色, 均禁止买入
    # if dlxt_long_period < 0 or dlxt < 0:
    #     return numpy.nan

    # 长周期动量系统变为 红->蓝/绿, 蓝->绿
    if dlxt_long_period_shift < dlxt_long_period:  # and dlxt_long_period > 0:
        return low

    # if dlxt_shift < dlxt:
    #     return low

    # if dlxt_long_period > 0 and dlxt > 0:
    #     return low

    if dlxt > 0 and 0 > force_index > force_index_shift:
        return low

    return numpy.nan


def function_exit(high, dlxt_long_period, dlxt_long_period_shift, dlxt, dlxt_shift, force_index, force_index_shift,
                  period):
    if dlxt_long_period_shift > dlxt_long_period:
        return high

    # 暂时不考虑做空, 即长周期动量为红色时, 是处于空仓状态的
    if dlxt_long_period < 0:
        return numpy.nan

    if period in ['week', 'day', 'm30'] and dlxt_shift > dlxt:
        return high

    if dlxt == 0 and 0 < force_index < force_index_shift:
        return high

    return numpy.nan


def compute_index(quote, period=None):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    # 强力指数
    quote = force_index.force_index(quote)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'force_index_shift'] = quote['force_index'].shift(periods=1)

    return quote_copy


def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'triple_screen_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(x.low, x.dlxt_long_period, x.dlxt_long_period_shift, x.dlxt, x.dlxt_shift,
                                 x.force_index, x.force_index_shift, period),
        axis=1)

    return quote_copy


def signal_exit(quote, period=None):
    # 长中周期动力系统中，波段操作时只要有一个变为红色，短线则任一变为蓝色
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'triple_screen_signal_exit'] = quote.apply(
        lambda x: function_exit(x.high, x.dlxt_long_period, x.dlxt_long_period_shift, x.dlxt, x.dlxt_shift,
                                x.force_index, x.force_index_shift, period),
        axis=1)

    return quote_copy


if __name__ == '__main__':
    signal_exit()
