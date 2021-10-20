# -*- encoding: utf-8 -*-
import numpy


def signal_exit(quote, period):
    macd_line = quote['macd_line']
    macd_line_shift1 = macd_line.shift(periods=1)
    cond = (macd_line < macd_line_shift1) & (macd_line_shift1 > macd_line.shift(periods=2)) & (macd_line_shift1 > 0)
    quote['macd_signal_exit'] = numpy.nan
    quote['macd_signal_exit'] = quote['macd_signal_exit'].mask(cond, quote.high)

    return quote
