# -*- coding: utf-8 -*-
import numpy
import pandas

from indicator import step, strong_base
from indicator.decorator import computed
from pointor import signal_resistance_support


def compute_breakout(quote, period, mask):
    mask_base = mask.rolling(10, min_periods=1).max().astype(bool)

    quote = signal_resistance_support.signal_enter(quote, period)
    mask = quote.resistance_support_signal_enter.notna()
    mask &= mask_base

    values = pandas.Series(numpy.nan, index=quote.index)
    values = values.mask(mask, quote.low[mask])

    return values


@computed(column_name='strong_base_breakout_signal_enter')
def strong_base_breakout_signal_enter(quote, period):
    quote = strong_base.strong_base(quote, period)
    mask = quote['strong_base'].notna()
    values = compute_breakout(quote, period, mask)

    quote_copy = quote
    quote_copy.insert(len(quote_copy.columns), 'strong_base_breakout_signal_enter', values)

    return quote_copy


@computed(column_name='step_breakout_signal_enter')
def step_breakout_signal_enter(quote, period):
    quote = step.step(quote, period)
    mask = quote['step_ma'].notna()
    values = compute_breakout(quote, period, mask)

    quote_copy = quote
    quote_copy.insert(len(quote_copy.columns), 'step_breakout_signal_enter', values)

    return quote_copy


def signal_enter(quote, period, column):
    m = {
        'step_ma': step_breakout_signal_enter,
        'strong_base': strong_base_breakout_signal_enter
    }

    quote = m[column](quote, period, column)

    return quote
