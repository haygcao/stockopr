# -*- coding: utf-8 -*-
import numpy
import pandas

from indicator import step, strong_base, resistance_support
from indicator.decorator import computed


@computed(column_name='resistance_breakout_signal_enter')
def resistance_breakout_signal_enter(quote, period):
    quote = resistance_support.compute_index_resistance(quote, period)
    quote_copy = quote
    mask = quote_copy['resistance_signal'].notna()
    quote_copy.loc[:, 'resistance_breakout_signal_enter'] = quote_copy['resistance_signal'].mask(mask, quote_copy.low)
    return quote_copy


@computed(column_name='support_breakout_signal_exit')
def support_breakout_signal_exit(quote, period):
    quote = resistance_support.compute_index_support(quote, period)
    quote_copy = quote
    mask = quote_copy['support_signal'].notna()
    quote_copy.loc[:, 'support_breakout_signal_exit'] = quote_copy['support_signal'].mask(mask, quote.high)
    return quote_copy


def compute_breakout(quote, period, mask):
    mask_base = mask.rolling(10, min_periods=1).max().astype(bool)

    quote = resistance_breakout_signal_enter(quote, period)
    mask = quote.resistance_breakout_signal_enter.notna()
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
        'resistance_breakout': resistance_breakout_signal_enter,
        'step_breakout': step_breakout_signal_enter,
        'strong_base_breakout': strong_base_breakout_signal_enter,
    }

    quote = m[column](quote, period=period)

    return quote


def signal_exit(quote, period, column):
    quote = support_breakout_signal_exit(quote, period=period)
    return quote
