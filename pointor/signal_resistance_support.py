# -*- coding: utf-8 -*-
import numpy
import pandas

from config import config
from indicator import ema
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


@computed(column_name='resistance_60')
def compute_index(quote, period=None):
    # quote = ema.compute_ema(quote)
    quote.loc[:, 'resistance_120'] = quote.loc[:, 'high'].rolling(120, min_periods=1).max()
    quote.loc[:, 'resistance_60'] = quote.loc[:, 'high'].rolling(60, min_periods=1).max()
    quote.loc[:, 'resistance_30'] = quote.loc[:, 'high'].rolling(20, min_periods=1).max()
    quote.loc[:, 'resistance_20'] = quote.loc[:, 'high'].rolling(20, min_periods=1).max()
    quote.loc[:, 'support_10'] = quote.loc[:, 'low'].rolling(10, min_periods=1).min()
    quote.loc[:, 'support_5'] = quote.loc[:, 'low'].rolling(5, min_periods=1).min()
    quote.loc[:, 'support_2'] = quote.loc[:, 'low'].rolling(2, min_periods=1).min()

    return quote


@computed(column_name='resistance_support_signal_enter')
def signal_enter(quote, period=None):
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
    mask = quote_copy['resistance_signal'].notna()
    quote_copy.loc[:, 'resistance_support_signal_enter'] = quote_copy['resistance_signal'].mask(mask, quote_copy.low)

    return quote_copy


@computed(column_name='resistance_support_signal_exit')
def signal_exit(quote, period=None):
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
    mask = quote_copy['support_signal'].notna()
    quote_copy.loc[:, 'resistance_support_signal_exit'] = quote_copy['support_signal'].mask(mask, quote.high)

    return quote_copy
