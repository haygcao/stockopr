# -*- coding: utf-8 -*-
from util.macd import ema, atr


def volume(quote, back_days):
    vol_series = quote['volume']
    vol_ema5 = ema(vol_series, n=5)
    vol_ema10 = ema(vol_series, n=10)
    return vol_ema5[-1 - back_days] / vol_ema10[-5 - back_days] > 5


def price(quote, back_days):
    atr5 = atr(quote, 5)
    return atr5[-1 - back_days] > 5 or atr5[:-back_days].max() >= 8


def trend(quote, back_days):
    ema26 = ema(quote['close'], n=26)
    return ema26[-1 - back_days] > ema26[-2 - back_days]


def hot_strong(quote, back_days=0):
    if not volume(quote, back_days):
        return False

    if not price(quote, back_days):
        return False

    if not trend(quote, back_days):
        return False

    return True
