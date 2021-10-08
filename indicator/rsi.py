# -*- coding: utf-8 -*-
"""
N1: 6/12/24
LC:=REF(CLOSE,1);
RSI1: SMA(MAX(CLOSE - LC, 0), N1, 1) / SMA(ABS(CLOSE - LC), N1, 1) * 100;
"""
import numpy

from indicator.decorator import computed


@computed(column_name='rsi')
def compute_rsi(quote, period):
    N = 12
    M = 1
    close = quote.close
    close_yest = quote.close.shift(periods=1)

    a = numpy.maximum(close - close_yest, 0)
    b = (close - close_yest).abs()

    rsi_12 = a.ewm(com=N - M, adjust=True).mean() / b.ewm(com=N - M, adjust=True).mean() * 100
    quote['rsi'] = rsi_12

    return quote
