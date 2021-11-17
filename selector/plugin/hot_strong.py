# -*- coding: utf-8 -*-
from indicator import ema
from indicator import atr


def volume(vol_ema5, vol_ema10, back_day):
    return vol_ema5.iloc[-1 - back_day] / vol_ema10.iloc[-5 - back_day] > 3


def price(amplitude, back_day):
    return amplitude.iloc[-1 - back_day] > 0.05 or amplitude.iloc[:-back_day].max() >= 0.08


def trend(ema26, back_day):
    return ema26.iloc[-1 - back_day] > ema26.iloc[-2 - back_day]


def hot_strong_one_day(vol_ema5, vol_ema10, amplitude, ema26, back_day):
    if not volume(vol_ema5, vol_ema10, back_day):
        return False

    if not price(amplitude, back_day):
        return False

    if not trend(ema26, back_day):
        return False

    return True


def hot_strong(quote, period, back_days):
    back_days = 5

    vol_series = quote['volume']
    vol_ema5 = ema.ema(vol_series, n=5)
    vol_ema10 = ema.ema(vol_series, n=10)

    atr5 = atr.compute_atr(quote, 5)['atr']
    close_yest = quote['close'].shift(periods=1)
    amplitude = atr5 / close_yest

    ema26 = ema.ema(quote['close'], n=26)

    for back_day in range(0, back_days):
        if hot_strong_one_day(vol_ema5, vol_ema10, amplitude, ema26, back_day):
            return True

    return False