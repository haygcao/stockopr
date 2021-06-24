# -*- coding: utf-8 -*-
import numpy

from config.config import is_long_period
from indicator import force_index, dynamical_system
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def function_enter(low, dlxt_long_period, dlxt_long_period_shift, dlxt, dlxt_shift, dlxt_ema13, period, date):
    # 非长周期, 不提供看多信号
    if not is_long_period(period):
        return numpy.nan

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

    quote_copy = quote  # .copy()
    if 'dlxt_long_period_shift' not in quote_copy.columns:
        quote_copy.loc[:, 'dlxt_long_period_shift'] = quote['dlxt_long_period'].loc[:].shift(periods=1)
    if 'dlxt_shift' not in quote_copy.columns:
        quote_copy.loc[:, 'dlxt_shift'] = quote['dlxt'].shift(periods=1)

    return quote_copy


@computed(column_name='dynamical_system_signal_enter')
# @ignore_long_period(column_name='dynamical_system_signal_enter')
@dynamic_system_filter(column_name='dynamical_system_signal_enter')
def signal_enter(quote, period=None):
    """
    dynamic system 不处理日内信号
    """
    if period not in ['week', 'day']:
        quote = quote.assign(dynamical_system_signal_enter=numpy.nan)
        return quote

    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()

    signal_column = 'dynamical_system_signal_enter'
    quote_copy.insert(len(quote_copy.columns), signal_column, numpy.nan)
    if is_long_period(period):
        mask1 = (quote_copy.dlxt_shift < quote_copy.dlxt) & (quote_copy.dlxt_shift < 0)
    else:
        mask1 = (quote_copy.dlxt_long_period_shift < quote_copy.dlxt_long_period) & (quote_copy.dlxt_long_period_shift < 0)

    mask = mask1
    quote_copy[signal_column] = quote_copy[signal_column].mask(mask, quote_copy['low'])

    # remove temp data
    quote_copy.drop(['dlxt_long_period_shift', 'dlxt_shift'], axis=1, inplace=True)

    return quote_copy


@computed(column_name='dynamical_system_signal_exit')
# @ignore_long_period(column_name='dynamical_system_signal_exit')
def signal_exit(quote, period=None):
    """
        dynamic system 不处理日内信号
        """
    if period not in ['week', 'day']:
        quote = quote.assign(dynamical_system_signal_exit=numpy.nan)
        return quote

    # 长中周期动力系统中，波段操作时只要有一个变为红色，短线则任一变为蓝色
    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()

    signal_column = 'dynamical_system_signal_exit'
    quote_copy.insert(len(quote_copy.columns), signal_column, numpy.nan)
    if is_long_period(period):
        mask1 = (quote_copy.dlxt_shift > quote_copy.dlxt) & (quote_copy.dlxt < 0)
    else:
        mask1 = (quote_copy.dlxt_long_period_shift > quote_copy.dlxt_long_period) & (quote_copy.dlxt_long_period < 0)
    mask = mask1
    quote_copy[signal_column] = quote_copy[signal_column].mask(mask, quote_copy['high'])

    # remove temp data
    quote_copy.drop(['dlxt_long_period_shift', 'dlxt_shift'], axis=1, inplace=True)

    return quote_copy


if __name__ == '__main__':
    signal_exit()
