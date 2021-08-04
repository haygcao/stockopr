# -*- coding: utf-8 -*-

"""
趋势型 振动升降指标 Accumulation Swing Index

同花顺公式
LC=REF(CLOSE,1);
AA=ABS(HIGH-LC);
BB=ABS(LOW-LC);
CC=ABS(HIGH-REF(LOW,1));
DD=ABS(LC-REF(OPEN,1));
R=IF(AA>BB AND AA>CC,AA+BB/2+DD/4,IF(BB>CC AND BB>AA,BB+AA/2+DD/4,CC+DD/4));
X=(CLOSE-LC+(CLOSE-OPEN)/2+LC-REF(OPEN,1));
SI=16*X/R*MAX(AA,BB);
ASI:SUM(SI,M1);
ASIT:MA(ASI,M2);
"""


def asi(quote, m1=26, m2=10):
    yest_close = quote.close.shift(periods=1)
    yest_low = quote.low.shift(periods=1)
    yest_open = quote.open.shift(periods=1)

    aa = (quote.high - yest_close).abs()
    bb = (quote.low - yest_close).abs()
    cc = (quote.high - yest_low).abs()
    dd = (yest_close - yest_open).abs()

    ee = quote.close - yest_close
    ff = quote.close - quote.open
    gg = yest_close - yest_open

    k = max(aa, bb)

    x = ee + ff/2 + gg

    if aa > bb and aa > cc:
        r = aa + bb/2 + dd/4
    elif bb > cc and bb > aa:
        r = bb + aa/2 + dd/4
    else:
        r = cc + dd/4

    si = 16 * (x/r) * k
    # l = 3
    # si = (50 / l) * (x / r) * k
    quote['asi'] = si.rolling(m1).sum()
    quote['masi'] = quote.asi.rolling(m2).mean()

    return quote
