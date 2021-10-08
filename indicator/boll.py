# -*- encoding: utf-8 -*-

"""
M:=20
BOLL:MA(CLOSE,M);
UB:BOLL+2*STD(CLOSE,M);
LB:BOLL-2*STD(CLOSE,M);
"""
from indicator.decorator import computed


@computed(column_name='boll_u')
def compute_boll(quote, period):
    boll = quote.ma20
    quote['boll_u'] = boll + 2 * quote.close.rolling(20).std()
    quote['boll_l'] = boll - 2 * quote.close.rolling(20).std()
    return quote
