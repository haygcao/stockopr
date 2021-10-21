# -*- encoding: utf-8 -*-
import numpy


def compute_signal(quote, period, will):
    macd_line = quote['macd_line']
    macd_line_shift1 = macd_line.shift(periods=1)
    cond = (will * macd_line > will * macd_line_shift1) &\
           (will * macd_line_shift1 < will * macd_line.shift(periods=2))

    if will == 1:
        signal_column = 'macd_signal_enter'
        price_column = 'low'
        cond &= macd_line_shift1 > 0
    else:
        signal_column = 'macd_signal_exit'
        price_column = 'high'

    quote[signal_column] = numpy.nan
    quote[signal_column] = quote[signal_column].mask(cond, quote[price_column])

    return quote


def signal_enter(quote, period):
    return compute_signal(quote, period, 1)


def signal_exit(quote, period):
    return compute_signal(quote, period, -1)
