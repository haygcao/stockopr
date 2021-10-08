# -*- coding: utf-8 -*-

"""
N1: 6/12/24
BIAS1 :(CLOSE-MA(CLOSE,N1))/MA(CLOSE,N1)*100;
"""
from indicator.decorator import computed


@computed(column_name='bias')
def compute_bias(quote, period):
    n = 24
    close = quote.close
    ma = close.rolling(n).mean()
    bias = (close / ma - 1) * 100
    quote['bias'] = bias
    return quote
