# -*- coding: utf-8 -*-
import numpy
import pandas

from indicator import force_index, dynamical_system, ema, dmi, step
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter, second_stage_filter
from pointor import signal_resistance_support


@computed(column_name='step_breakout_signal_enter')
# @ignore_long_period(column_name='step_signal_enter')
@dynamic_system_filter(column_name='step_breakout_signal_enter')
@second_stage_filter(column_name='step_breakout_signal_enter')
def signal_enter(quote, period=None):
    quote = step.step(quote, period)
    mask = quote.step_ma.notna()
    mask_base = mask.rolling(10, min_periods=1).max().astype(bool)

    quote = signal_resistance_support.signal_enter(quote, period)
    mask = quote.resistance_support_signal_enter.notna()
    mask &= mask_base

    quote_copy = quote  # .copy()

    values = pandas.Series(numpy.nan, index=quote.index)
    values = values.mask(mask, quote.low[mask])
    quote_copy.insert(len(quote_copy.columns), 'step_breakout_signal_enter', values)

    return quote_copy
