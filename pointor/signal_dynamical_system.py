# -*- coding: utf-8 -*-
import numpy

from config.config import is_long_period
from indicator import force_index, dynamical_system
from indicator.decorator import computed, ignore_long_period


def function_enter(low, dlxt_long_period, dlxt_long_period_shift, dlxt, dlxt_shift, dlxt_ema13, period, date):
    # 长中周期动量系统中任一为红色, 均禁止买入
    if (not is_long_period(period) and dlxt_long_period < 0) or dlxt < 0:
        return numpy.nan

    # 长周期动量系统变为 红->蓝/绿, 蓝->绿
    if not is_long_period(period) and dlxt_long_period_shift < dlxt_long_period and dlxt_long_period_shift < 0:
        # print(date, '4')
        return low

    if is_long_period(period) and dlxt_shift < dlxt and dlxt_shift < 0:
        # print(date, '3')
        return low

    # if dlxt_long_period > 0 and dlxt > 0:
    #     return low

    return numpy.nan


def function_exit(high, dlxt_long_period, dlxt_long_period_shift, dlxt, dlxt_shift, period):
    if not is_long_period(period) and dlxt_long_period_shift > dlxt_long_period < 0:
        return high

    # 暂时不考虑做空, 即长周期动量为红色时, 是处于空仓状态的
    if not is_long_period(period) and dlxt_long_period < 0:
        return numpy.nan

    if period in ['week', 'day', 'm30'] and dlxt_shift > dlxt and dlxt < 0:
        return high

    return numpy.nan


def compute_index(quote, period=None):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'dlxt_long_period_shift'] = quote['dlxt_long_period'].loc[:].shift(periods=1)
    quote_copy.loc[:, 'dlxt_shift'] = quote['dlxt'].shift(periods=1)

    return quote_copy


@computed(column_name='dynamical_system_signal_enter')
@ignore_long_period(column_name='dynamical_system_signal_enter')
def signal_enter(quote, period=None):
    # if is_long_period(period):
    #     quote = quote.assign(dynamical_system_signal_enter=numpy.nan)
    #     return quote

    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'dynamical_system_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(
            x.low, x.dlxt_long_period, x.dlxt_long_period_shift, x.dlxt, x.dlxt_shift, x.dlxt_ema13, period, x.name), axis=1)

    # remove temp data
    quote_copy.drop(['dlxt_long_period_shift', 'dlxt_shift'], axis=1)

    return quote_copy


@computed(column_name='dynamical_system_signal_exit')
@ignore_long_period(column_name='dynamical_system_signal_exit')
def signal_exit(quote, period=None):
    # if is_long_period(period):
    #     quote = quote.assign(dynamical_system_signal_exit=numpy.nan)
    #     return quote

    # 长中周期动力系统中，波段操作时只要有一个变为红色，短线则任一变为蓝色
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'dynamical_system_signal_exit'] = quote.apply(
        lambda x: function_exit(x.high, x.dlxt_long_period, x.dlxt_long_period_shift, x.dlxt, x.dlxt_shift, period),
        axis=1)

    # remove temp data
    quote_copy.drop(['dlxt_long_period_shift', 'dlxt_shift'], axis=1)

    return quote_copy


if __name__ == '__main__':
    signal_exit()
