# -*- coding: utf-8 -*-
import numpy

from config import config
from indicator import ema
from indicator.decorator import computed, ignore_long_period


def function_enter_origin(low, close, resistance, dlxt_long_period, dlxt, dlxt_ema13, ema13, ema26, ema26_shift, period, date):
    if dlxt_long_period < 0:  # or dlxt < 0:
        return numpy.nan

    if close < resistance:
        return numpy.nan

    # ema13 向上, close 回归 ema13 ~ ema26 价值区间
    # if ema26 >= ema26_shift and (close - resistance) / resistance > config.resistance_over_rate:
    if (close - resistance) / resistance > config.resistance_over_rate:
        return low

    return numpy.nan


def function_enter(signal, signal_shift):
    if numpy.isnan(signal_shift):
        return signal
    return numpy.nan


def function_exit(high, close, support, dlxt_long_period, dlxt, dlxt_ema13, ema13, ema26, ema26_shift, period, date):
    if close > support:
        return numpy.nan

    if (support - close) / support > config.support_under_rate:
        return high

    return numpy.nan


def compute_index(quote, period=None):
    quote = ema.compute_ema(quote)
    quote.loc[:, 'resistance_origin'] = quote.loc[:, 'high'].rolling(20, min_periods=1).max()
    quote.loc[:, 'support_origin'] = quote.loc[:, 'low'].rolling(10, min_periods=1).min()

    return quote


@computed(column_name='resistance_support_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'resistance'] = quote['resistance_origin'].shift(periods=config.resistance_support_backdays)
    quote_copy.loc[:, 'ema26_shift'] = quote['ema26'].shift(periods=1)
    quote_copy.loc[:, 'resistance_support_signal_enter_origin'] = quote_copy.apply(
        lambda x: function_enter_origin(x.low, x.close, x.resistance, x.dlxt_long_period, x.dlxt, x.dlxt_ema13, x.ema13,
                                 x.ema26, x.ema26_shift, period, x.name), axis=1)
    quote_copy.loc[:, 'resistance_support_signal_enter_shift'] = quote_copy['resistance_support_signal_enter_origin'].shift(periods=1)
    quote_copy.loc[:, 'resistance_support_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(x.resistance_support_signal_enter_origin, x.resistance_support_signal_enter_shift), axis=1)

    # remove temp data
    quote_copy.drop(['ema26_shift'], axis=1)
    quote_copy.drop(['resistance_support_signal_enter_origin'], axis=1)
    quote_copy.drop(['resistance_support_signal_enter_shift'], axis=1)

    return quote_copy


@computed(column_name='resistance_support_signal_exit')
def signal_exit(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'support'] = quote['support_origin'].shift(periods=config.resistance_support_backdays)
    quote_copy.loc[:, 'resistance_support_signal_exit'] = quote_copy.apply(
        lambda x: function_exit(x.high, x.close, x.support, x.dlxt_long_period, x.dlxt, x.dlxt_ema13, x.ema13, x.ema26,
                                 x.ema26_shift, period, x.name), axis=1)

    return quote_copy
