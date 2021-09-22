# -*- coding: utf-8 -*-
import numpy
import pandas

from config import config
from indicator import ema
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


@computed(column_name='resistance_signal')
def compute_index_resistance(quote, period=None):
    quote_copy = quote.copy()
    quote_copy['resistance_signal'] = numpy.nan
    days = [20, 30, 60, 120]
    days.reverse()
    for day in days:
        resistance_origin = quote_copy.loc[:, 'high'].rolling(day, min_periods=1).max()
        resistance = resistance_origin.shift(periods=config.resistance_support_backdays)
        if day == config.resistance_day:
            quote_copy.loc[:, 'resistance'] = resistance

        mask_nan = quote_copy['resistance_signal'].isna()
        resistance_support_signal_enter_origin = pandas.Series(numpy.nan, index=quote.index)
        mask1 = quote_copy.close > resistance
        mask2 = quote_copy.close / resistance - 1 > config.period_price_diff_ratio_resistance_support_map[period]
        resistance_support_signal_enter_origin = resistance_support_signal_enter_origin.mask(mask1 & mask2, day)

        resistance_support_signal_enter_shift = resistance_support_signal_enter_origin.shift(periods=1)
        mask3 = resistance_support_signal_enter_origin.notna() & resistance_support_signal_enter_shift.notna()
        mask = (mask1 & mask2 & ~mask3)
        quote_copy.loc[:, 'resistance_signal'] = quote_copy.loc[:, 'resistance_signal'].mask(mask & mask_nan, day)

    return quote_copy


@computed(column_name='support_signal')
def compute_index_support(quote, period=None):
    quote_copy = quote.copy()
    quote_copy.loc[:, 'support_signal'] = numpy.nan
    days = [5, 10, 20]
    days.reverse()
    for day in days:
        support_origin = quote_copy.loc[:, 'low'].rolling(day, min_periods=1).min()
        support = support_origin.shift(periods=config.resistance_support_backdays)
        if day == config.support_day:
            quote_copy.loc[:, 'support'] = support

        mask_nan = quote_copy['support_signal'].isna()

        mask1 = quote_copy.close < support
        mask2 = 1 - quote_copy.close / support > config.period_price_diff_ratio_resistance_support_map[period]
        resistance_support_signal_exit = pandas.Series(numpy.nan, index=quote.index)
        mask = (mask1 & mask2)
        quote_copy.loc[:, 'support_signal'] = resistance_support_signal_exit.mask(mask & mask_nan, day)

    return quote_copy


def compute_index(quote, period):
    quote = compute_index_resistance(quote, period)
    quote = compute_index_support(quote, period)

    return quote
