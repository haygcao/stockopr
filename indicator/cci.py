# -*- encoding: utf-8 -*-

"""
TYP:=(HIGH+LOW+CLOSE)/3;
CCI:(TYP-MA(TYP,N))*1000/(15*AVEDEV(TYP,N));

与 talib.abstract.CCI 计算结果一致
"""
from indicator.decorator import computed


@computed(column_name='cci')
def compute_cci(quote, period):
    n = 14
    typ = (quote.high + quote.low + quote.close) / 3
    md = typ.rolling(window=n).apply(lambda x: abs(x-x.mean()).mean())  # , raw=False)
    # md = typ.rolling(n).std()
    cci = (typ - typ.rolling(n).mean()) * 1000 / (15 * md)
    quote['cci'] = cci
    return quote
