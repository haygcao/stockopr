# -*- coding: utf-8 -*-
import numpy

from config import config
from config.config import is_long_period
from indicator import force_index, dynamical_system, ema, dmi, value_return
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def function_enter(low, close, dyn_sys_long_period, dyn_sys, dyn_sys_ema13, ema13, ema26, ema26_shift, period, date):
    if dyn_sys_long_period < 0:  # or dyn_sys < 0:
        return numpy.nan

    # ema13 向上, close 回归 ema13 ~ ema26 价值区间, ema13 >= ema26
    if dyn_sys_long_period >= 0 and ema26_shift <= ema26 <= ema13 and low <= ema13:
        # print(date, '5')
        return low

    return numpy.nan


def compute_index(quote, period=None):
    quote = value_return.value_return(quote, period)

    return quote


@computed(column_name='value_return_signal_enter')
@ignore_long_period(column_name='value_return_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()
    values = quote_copy.value_return.mask(quote_copy.value_return.notna(), quote_copy.low)
    quote_copy.insert(len(quote_copy.columns), 'value_return_signal_enter', values)

    return quote_copy
