# -*- coding: utf-8 -*-
import numpy

from config.config import is_long_period
from indicator import force_index, dynamical_system
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def function_enter(low, dyn_sys_long_period, dyn_sys_long_period_shift, dyn_sys, dyn_sys_shift, dyn_sys_ema13, period, date):
    # 非长周期, 不提供看多信号
    if not is_long_period(period):
        return numpy.nan

    # 长中周期动量系统中任一为红色, 均禁止买入
    if (not is_long_period(period) and dyn_sys_long_period < 0) or dyn_sys < 0:
        return numpy.nan

    # 长周期动量系统变为 红->蓝/绿, 蓝->绿
    if not is_long_period(period) and dyn_sys_long_period_shift < dyn_sys_long_period and dyn_sys_long_period_shift < 0:
        # print(date, '4')
        return low

    if is_long_period(period) and dyn_sys_shift < dyn_sys and dyn_sys_shift < 0:
        # print(date, '3')
        return low

    # if dyn_sys_long_period > 0 and dyn_sys > 0:
    #     return low

    return numpy.nan


def function_exit(high, dyn_sys_long_period, dyn_sys_long_period_shift, dyn_sys, dyn_sys_shift, period):
    if not is_long_period(period) and dyn_sys_long_period_shift > dyn_sys_long_period < 0:
        return high

    # 暂时不考虑做空, 即长周期动量为红色时, 是处于空仓状态的
    if not is_long_period(period) and dyn_sys_long_period < 0:
        return numpy.nan

    if period in ['week', 'day', 'm30'] and dyn_sys_shift > dyn_sys and dyn_sys < 0:
        return high

    return numpy.nan


def compute_index(quote, period=None):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    quote_copy = quote  # .copy()
    if 'dyn_sys_long_period_shift' not in quote_copy.columns:
        quote_copy.loc[:, 'dyn_sys_long_period_shift'] = quote['dyn_sys_long_period'].loc[:].shift(periods=1)
    if 'dyn_sys_shift' not in quote_copy.columns:
        quote_copy.loc[:, 'dyn_sys_shift'] = quote['dyn_sys'].shift(periods=1)

    return quote_copy


@computed(column_name='dynamical_system_signal_enter')
# @ignore_long_period(column_name='dynamical_system_signal_enter')
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
        mask1 = (quote_copy.dyn_sys_shift < quote_copy.dyn_sys) & (quote_copy.dyn_sys_shift < 0)
    else:
        mask1 = (quote_copy.dyn_sys_long_period_shift < quote_copy.dyn_sys_long_period) & (quote_copy.dyn_sys_long_period_shift < 0)

    mask = mask1
    quote_copy[signal_column] = quote_copy[signal_column].mask(mask, quote_copy['low'])

    # remove temp data
    quote_copy.drop(['dyn_sys_long_period_shift', 'dyn_sys_shift'], axis=1, inplace=True)

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
        mask1 = (quote_copy.dyn_sys_shift > quote_copy.dyn_sys) & (quote_copy.dyn_sys < 0)
    else:
        mask1 = (quote_copy.dyn_sys_long_period_shift > quote_copy.dyn_sys_long_period) & (quote_copy.dyn_sys_long_period < 0)
    mask = mask1
    quote_copy[signal_column] = quote_copy[signal_column].mask(mask, quote_copy['high'])

    # remove temp data
    quote_copy.drop(['dyn_sys_long_period_shift', 'dyn_sys_shift'], axis=1, inplace=True)

    return quote_copy


if __name__ == '__main__':
    signal_exit()
