# -*- coding: utf-8 -*-

"""
SHORT:=12
LONG:=26
MID:=9
DIF:EMA(CLOSE,SHORT)-EMA(CLOSE,LONG);
DEA:EMA(DIF,MID);
MACD:(DIF-DEA)*2,COLORSTICK;
"""
from indicator.decorator import computed


@computed(column_name='macd_histogram')
def compute_macd(quote):
    exp12 = quote['close'].ewm(span=12, adjust=False).mean()
    exp26 = quote['close'].ewm(span=26, adjust=False).mean()
    macd_line = exp12 - exp26
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    histogram = (macd_line - macd_signal) * 2

    quote['macd_line'] = macd_line
    quote['macd_signal'] = macd_signal
    quote['macd_histogram'] = histogram

    return quote
