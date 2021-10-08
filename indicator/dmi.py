# -*- coding: utf-8 -*-
import numpy
import pandas

from indicator.decorator import computed
from util.macd import dmi


@computed(column_name='adx')
def compute_dmi(quote, period):
    """
    通达信公式
    MTR:=SUM(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(REF(CLOSE,1)-LOW)),N);
    HD :=HIGH-REF(HIGH,1);
    LD :=REF(LOW,1)-LOW;
    DMP:=SUM(IF(HD>0&&HD>LD,HD,0),N);
    DMM:=SUM(IF(LD>0&&LD>HD,LD,0),N);
    PDI: DMP*100/MTR;
    MDI: DMM*100/MTR;
    ADX: MA(ABS(MDI-PDI)/(MDI+PDI)*100,M);
    ADXR:(ADX+REF(ADX,M))/2;
    """

    high = quote.high
    low = quote.low
    close = quote.close

    high_yest = high.shift(periods=1)
    low_yest = low.shift(periods=1)
    close_yest = close.shift(periods=1)

    # MTR := SUM(MAX(MAX(HIGH - LOW, ABS(HIGH - REF(CLOSE, 1))), ABS(REF(CLOSE, 1) - LOW)), N);
    diff_high_low = high - low
    abs_diff_high_yclose = abs(high - close_yest)
    max1 = numpy.maximum(diff_high_low, abs_diff_high_yclose)

    abs_diff_yclose_low = abs(close_yest - low)
    _ = numpy.maximum(max1, abs_diff_yclose_low)
    mtr = _.rolling(14).sum()

    # HD := HIGH - REF(HIGH, 1);
    hd = high - high_yest

    # LD := REF(LOW, 1) - LOW;
    ld = low_yest - low

    # DMP := SUM(IF(HD > 0 & & HD > LD, HD, 0), N);
    dmp = pandas.Series(0, index=quote.index)
    mask = (hd > 0) & (hd > ld)
    dmp = dmp.mask(mask, hd)
    dmp = dmp.rolling(14).sum()

    # DMM:=SUM(IF(LD>0&&LD>HD,LD,0),N);
    dmm = pandas.Series(0, index=quote.index)
    mask = (ld > 0) & (ld > hd)
    dmm = dmm.mask(mask, ld)
    dmm = dmm.rolling(14).sum()

    # PDI: DMP * 100 / MTR;
    pdi = dmp * 100 / mtr

    # MDI: DMM * 100 / MTR;
    mdi = dmm * 100 / mtr

    # ADX: MA(ABS(MDI - PDI) / (MDI + PDI) * 100, M);
    adx = abs(mdi - pdi) / (mdi + pdi) * 100
    adx = adx.rolling(6).mean()

    # ADXR: (ADX + REF(ADX, M)) / 2;
    adxr = (adx + adx.shift(periods=6)) / 2

    quote['pdi'] = pdi
    quote['mdi'] = mdi
    quote['adx'] = adx
    quote['adxr'] = adxr

    return quote


@computed(column_name='adx')
def compute_dmi_finta(quote):
    from finta import TA
    df = TA.DMI(quote, adjust=False)
    return df


@computed(column_name='adx')
def compute_dmi_talib(quote):
    df = dmi(quote)
    quote['pdi'] = df['pdi']
    quote['mdi'] = df['mdi']
    quote['adx'] = df['adx']
    quote['adxr'] = df['adxr']

    return quote
