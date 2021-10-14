# -*- coding: utf-8 -*-

"""
N:=14;
MTR:MAX(MAX((HIGH-LOW),ABS(REF(CLOSE,1)-HIGH)),ABS(REF(CLOSE,1)-LOW));
ATR:MA(MTR,N);
"""
import numpy

from indicator.decorator import computed


@computed(column_name='atr')
def compute_atr(quote):
    # quote['atr'] = atr(quote)

    close_yest = quote.close.shift(periods=1)
    high = quote.high
    low = quote.low

    mtr = numpy.maximum(numpy.maximum(high - low, (close_yest - high).abs()), (close_yest - low).abs())
    atr = mtr.rolling(14).mean()

    quote['atr'] = atr

    return quote
