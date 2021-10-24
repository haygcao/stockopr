# -*- coding: utf-8 -*-

"""
相对强弱指数RSI 极端区域
1 MA200 向上, CLOSES > MA200
2 RSI4D < 30, buy 1/2
3 RSI4D < 25, buy 1/2
4 RSI4D > 55, sell
"""

import numpy
import pandas

from indicator import ma, rsi, ema
from pointor import signal


def _enter(quote, period):
    close = quote.close

    ma200 = ma.ma(close, 200)
    cond1 = (ma200 > ma200.shift(periods=1)) & (quote.close > ma200)

    rsi4d = rsi.rsi(close, 4)
    cond2 = rsi4d < 25

    series_enter = pandas.Series(numpy.nan, index=quote.index)
    series_enter = series_enter.mask(cond1 & cond2, quote.close)

    return series_enter


def _exit(quote, period):
    close = quote.close

    ma200 = ma.ma(close, 200)
    cond1 = (ma200 < ma200.shift(periods=1)) | (quote.close < ma200)

    rsi4d = rsi.rsi(close, 4)

    cond2 = rsi4d > 55
    cond = cond1 | cond2

    series_exit = pandas.Series(numpy.nan, index=quote.index)
    series_exit = series_exit.mask(cond, quote.close)

    return series_exit


def compute_signal(quote, period):
    enter_ = _enter(quote, period)
    exit_ = _exit(quote, period)

    enter_, exit_ = signal.clean_signal(quote, enter_, exit_)

    quote['signal_enter'] = enter_
    quote['signal_exit'] = exit_

    return quote

    # series_signal = pandas.Series(numpy.nan, index=quote.index)
    # series_signal = series_signal.mask(enter_, 1)
    # series_signal = series_signal.mask(exit_, -1)
    #
    # return series_signal



