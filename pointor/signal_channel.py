# -*- coding: utf-8 -*-

import numpy

from config.config import is_long_period, period_price_diff_ratio_atr_map
from indicator import atr, dynamical_system, ema
from indicator.decorator import computed


def function_enter(low, dyn_sys_long_period, dyn_sys, ema, atr, period, date):
    if not is_long_period(period) and dyn_sys_long_period == -1:
        return numpy.nan

    if dyn_sys == -1:
        return numpy.nan

    # if dyn_sys == -1:
    #     if low <= ema - 3*atr:
    #         return low

    times = period_price_diff_ratio_atr_map[period]

    if dyn_sys >= 0:
        if low <= ema - times * atr:
            # print(date, '1')
            return low

    if low <= ema - (times + 1) * atr:
        # print(date, '2')
        return low

    return numpy.nan


def function_exit(high, dyn_sys_long_period, dyn_sys, ema, atr, period):
    # if not is_long_period(period) and dyn_sys_long_period == 1:
    #     return numpy.nan

    # if dyn_sys == 1:
    #     if high >= ema + 3*atr:
    #         return high

    times = period_price_diff_ratio_atr_map[period]

    if dyn_sys <= 0:
        if high >= ema + times * atr:
            return high

    if high >= ema + (times + 1) * atr:
        return high

    return numpy.nan


def compute_index(quote, period):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    quote = atr.compute_atr(quote)
    ema26 = ema.ema(quote['close'], 26)
    quote['ema'] = ema26

    return quote


def compute_signal(quote, exit_signal):
    greater_than_3atr = quote['close'] * exit_signal > (quote['ema'] + 3 * quote['atr'] * exit_signal) * exit_signal
    greater_than_2atr = quote['close'] * exit_signal > (quote['ema'] + 2 * quote['atr'] * exit_signal) * exit_signal

    column = 'channel_signal_exit' if exit_signal == 1 else 'channel_signal_enter'
    price = 'high' if exit_signal == 1 else 'low'
    # quote = quote.assign(channel_signal_exit=numpy.nan)
    quote.insert(len(quote.columns), column, numpy.nan)

    index3 = 0
    while True:
        r = numpy.where(greater_than_3atr[index3:])[0]
        if not numpy.any(r):
            break
        index2 = r[0] + index3

        r = numpy.where(~greater_than_2atr[index2:])[0]
        if not numpy.any(r):
            break
        index = index2 + r[0]
        # signal_exit_series.iloc[index] = quote.iloc[index]['high']
        # quote.iloc[index]['channel_signal_exit'] = quote.iloc[index]['high']
        # A value is trying to be set on a copy of a slice from a DataFrame
        quote[column].iat[index] = quote.iloc[index][price]
        # quote_copy[column][index] = quote.iloc[index]['high']
        index3 = index + 1

    return quote


@computed(column_name='channel_signal_enter')
def signal_enter(quote, period):
    quote = compute_index(quote, period)

    return compute_signal(quote, exit_signal=-1)


@computed(column_name='channel_signal_exit')
def signal_exit(quote, period):
    quote = compute_index(quote, period)

    return compute_signal(quote, exit_signal=1)
