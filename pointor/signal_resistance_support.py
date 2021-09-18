# -*- coding: utf-8 -*-
import numpy
import pandas

from config import config
from indicator import ema
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def compute_index(quote, period=None):
    # quote = ema.compute_ema(quote)
    quote.loc[:, 'resistance_origin'] = quote.loc[:, 'high'].rolling(20, min_periods=1).max()
    quote.loc[:, 'support_origin'] = quote.loc[:, 'low'].rolling(10, min_periods=1).min()

    return quote


@computed(column_name='resistance_support_signal_enter')
@dynamic_system_filter(column_name='resistance_support_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'resistance'] = quote['resistance_origin'].shift(periods=config.resistance_support_backdays)

    resistance_support_signal_enter_origin = pandas.Series(numpy.nan, index=quote.index)
    mask1 = quote_copy.close > quote_copy.resistance
    mask2 = quote_copy.close / quote_copy.resistance - 1 > config.period_price_diff_ratio_resistance_support_map[period]
    resistance_support_signal_enter_origin = resistance_support_signal_enter_origin.mask(mask1 & mask2, quote.low)

    resistance_support_signal_enter_shift = resistance_support_signal_enter_origin.shift(periods=1)
    mask = resistance_support_signal_enter_origin.notna() & resistance_support_signal_enter_shift.notna()
    quote_copy.loc[:, 'resistance_support_signal_enter'] = resistance_support_signal_enter_origin.mask(mask, numpy.nan)

    return quote_copy


@computed(column_name='resistance_support_signal_exit')
def signal_exit(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'support'] = quote['support_origin'].shift(periods=config.resistance_support_backdays)

    mask1 = quote_copy.close < quote_copy.support
    mask2 = 1 - quote_copy.close / quote_copy.support > config.period_price_diff_ratio_resistance_support_map[period]
    resistance_support_signal_exit = pandas.Series(numpy.nan, index=quote.index)
    quote_copy.loc[:, 'resistance_support_signal_exit'] = resistance_support_signal_exit.mask(mask1 & mask2, quote.high)

    return quote_copy
