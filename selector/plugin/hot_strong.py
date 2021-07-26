# -*- coding: utf-8 -*-
from util.macd import ema, atr


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


def hot_strong(quote, back_days=30):
    vol_series = quote['volume']
    vol_ema5 = ema(vol_series, n=5)['ema']
    vol_ema10 = ema(vol_series, n=10)['ema']

    atr5 = atr(quote, 5)['atr']
    close_yest = quote['close'].shift(periods=1)
    amplitude = atr5 / close_yest

    ema26 = ema(quote['close'], n=26)['ema']

    for back_day in range(0, back_days):
        if hot_strong_one_day(vol_ema5, vol_ema10, amplitude, ema26, back_day):
            return True

    return False