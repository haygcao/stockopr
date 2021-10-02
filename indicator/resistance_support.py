# -*- coding: utf-8 -*-
import numpy
import pandas

from config import config
from indicator import ema
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def compute_index_resistance_impl(quote, period, column_hl, column_close, column_signal):
    quote_copy = quote.copy()
    quote_copy[column_signal] = numpy.nan
    days = [20, 30, 60, 120]
    days.reverse()
    for day in days:
        resistance_origin = quote_copy.loc[:, column_hl].rolling(day, min_periods=1).max()
        resistance = resistance_origin.shift(periods=config.resistance_support_backdays)
        if 'resistance' in column_signal and day == config.resistance_day:
            quote_copy.loc[:, 'resistance'] = resistance

        mask_nan = quote_copy[column_signal].isna()
        resistance_support_signal_enter_origin = pandas.Series(numpy.nan, index=quote.index)
        mask1 = quote_copy[column_close] > resistance
        percent = 0 if 'asi' in column_signal else config.period_price_diff_ratio_resistance_support_map[period]
        mask2 = quote_copy[column_close] / resistance - 1 > percent
        resistance_support_signal_enter_origin = resistance_support_signal_enter_origin.mask(mask1 & mask2, day)

        resistance_support_signal_enter_shift = resistance_support_signal_enter_origin.shift(periods=1)
        mask3 = resistance_support_signal_enter_origin.notna() & resistance_support_signal_enter_shift.notna()
        mask = (mask1 & mask2 & ~mask3)
        quote_copy.loc[:, column_signal] = quote_copy.loc[:, column_signal].mask(mask & mask_nan, day)

    return quote_copy


@computed(column_name='resistance_signal')
def compute_index_resistance(quote, period):
    quote = compute_index_resistance_impl(quote, period, 'high', 'close', 'resistance_signal')
    return quote


@computed(column_name='asi_resistance_signal')
def compute_index_resistance_asi(quote, period):
    quote = compute_index_resistance_impl(quote, period, 'asi', 'asi', 'asi_resistance_signal')
    return quote


def compute_index_support_impl(quote, period, column_hl, column_close, column_signal):
    quote_copy = quote.copy()
    quote_copy.loc[:, column_signal] = numpy.nan
    days = [5, 10, 20]
    days.reverse()
    for day in days:
        support_origin = quote_copy.loc[:, column_hl].rolling(day, min_periods=1).min()
        support = support_origin.shift(periods=config.resistance_support_backdays)
        if 'support' in column_signal and day == config.support_day:
            quote_copy.loc[:, 'support'] = support

        mask_nan = quote_copy[column_signal].isna()

        mask1 = quote_copy[column_close] < support
        percent = 0 if 'asi' in column_signal else config.period_price_diff_ratio_resistance_support_map[period]
        mask2 = 1 - quote_copy[column_close] / support > percent
        resistance_support_signal_exit = pandas.Series(numpy.nan, index=quote.index)
        mask = (mask1 & mask2)
        quote_copy.loc[:, column_signal] = resistance_support_signal_exit.mask(mask & mask_nan, day)

    return quote_copy


@computed(column_name='support_signal')
def compute_index_support(quote, period):
    quote = compute_index_support_impl(quote, period, 'low', 'close', 'support_signal')
    return quote


@computed(column_name='asi_support_signal')
def compute_index_support_asi(quote, period):
    quote = compute_index_support_impl(quote, period, 'asi', 'asi', 'asi_support_signal')
    return quote


def compute_index(quote, period):
    quote = compute_index_resistance(quote, period)
    quote = compute_index_support(quote, period)

    return quote
