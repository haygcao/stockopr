# -*- coding: utf-8 -*-
import numpy

import indicator
from selector.plugin import dynamical_system
from util import macd


def function_enter(low, dlxt, ema, atr):
    if dlxt == -1:
        if low <= ema - 3*atr:
            return low
    elif dlxt == 0:
        if low <= ema - 2*atr:
            return low

    return numpy.nan


def function_exit(high, dlxt, ema, atr):
    if dlxt == 1:
        if high >= ema + 3*atr:
            return high
    elif dlxt == 0:
        if high >= ema + 2*atr:
            return high

    return numpy.nan


def compute_index(quote):
    quote = dynamical_system.dynamical_system(quote)
    quote = indicator.atr.compute_atr(quote)
    ema26 = macd.ema(quote, 26)
    quote['ema'] = ema26

    return quote


def signal_enter(quote):
    quote = compute_index(quote)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'channel_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(x.low, x.dlxt, x.ema, x.atr), axis=1)

    return quote_copy


def signal_exit(quote):
    quote = compute_index(quote)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'channel_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(x.low, x.dlxt, x.ema, x.atr), axis=1)

    return quote_copy


def signal_exit(quote):
    quote = compute_index(quote)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'channel_signal_exit'] = quote_copy.apply(
        lambda x: function_exit(x.high, x.dlxt, x.ema, x.atr), axis=1)

    return quote_copy
