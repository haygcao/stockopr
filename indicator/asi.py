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
同花顺
    SI=16*X/R*MAX(AA,BB);
    ASI:SUM(SI,M1);  # 26
通达信
    SI:=8*X/R*MAX(AA,BB);
    ASI:SUM(SI,0), COLORBLACK, LINETHICK1;
ASIT:MA(ASI,M2);  # 10
"""
import numpy
import pandas

from indicator.decorator import computed


@computed(column_name='asi')
def compute_asi(quote, period, m1=26):
    """
    同花顺默认参数 26, 10
    通达信默认参数未知 暂确定为 0, 13
    背离信号通达信不容易出现, 同花顺更容易些
    """
    yest_close = quote.close.shift(periods=1)
    yest_low = quote.low.shift(periods=1)
    yest_open = quote.open.shift(periods=1)

    aa = (quote.high - yest_close).abs()
    bb = (quote.low - yest_close).abs()
    cc = (quote.high - yest_low).abs()
    dd = (yest_close - yest_open).abs()

    df = pandas.DataFrame(aa, index=quote.index)
    df['bb'] = bb
    df['cc'] = cc
    df['dd'] = dd

    r = cc + dd / 4
    mask1 = (aa > bb) & (aa > cc)
    r = r.mask(mask1, aa + bb / 2 + dd / 4)
    mask2 = (bb > cc) & (bb > aa)
    r = r.mask(mask2, bb + aa / 2 + dd / 4)

    df['mask1'] = mask1
    df['mask2'] = mask2
    df['r'] = r

    ee = quote.close - yest_close
    ff = quote.close - quote.open
    gg = yest_close - yest_open

    x = ee + ff / 2 + gg
    df['ee'] = ee
    df['ff'] = ff
    df['gg'] = gg
    df['x'] = x

    k = numpy.maximum(aa, bb)
    df['k'] = k

    # ths
    factor = 16 if m1 > 0 else 8
    si = factor * (x/r) * k  # ths
    asi = si.rolling(m1).sum() if m1 > 0 else si.cumsum()

    df['si'] = si
    m2 = 10 if m1 > 0 else 13
    masi = asi.rolling(m2).mean()

    df['asi'] = asi
    df['masi'] = masi

    quote['asi'] = asi
    quote['masi'] = masi

    return quote
