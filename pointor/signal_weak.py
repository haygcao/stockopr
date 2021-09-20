# -*- coding: utf-8 -*-
import numpy

from indicator import market_deviation_mat


def signal_one(quote, enter):
    quote = market_deviation_mat.compute_high_low(quote, compute_high=False, weak=True)
    if enter:
        high_low_column = 'min_period'
        signal_column = 'weak_signal_enter'
    else:
        high_low_column = 'max_period'
        signal_column = 'weak_signal_exit'
    high_low = quote[high_low_column]
    high_low = high_low[high_low.notna()]

    quote_copy = quote.copy()
    quote_copy.insert(len(quote.columns), signal_column, numpy.nan)
    for i in range(len(high_low) - 1, 0, -2):
        quote_copy.loc[high_low.index[i], signal_column] = quote_copy.loc[high_low.index[i], high_low_column]

    return quote_copy


def signal_enter(quote, period='day', back_days=125, column=None):
    return signal_one(quote, enter=True)


def signal_exit(quote, period='day', back_days=125, column=None):
    return signal_one(quote, enter=False)
