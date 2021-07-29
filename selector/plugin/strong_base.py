# -*- coding: utf-8 -*-

from util.macd import ema
from . import super


def strong_base(quote, period, back_days=3):
    times = 5

    ema_s = ema(quote['close'], n=times * 5)['ema']
    ema_m = ema(quote['close'], n=times * 10)['ema']
    ema_l = ema(quote['close'], n=times * 30)['ema']

    for back_day in range(back_days, -1, -1):
        if super.strong_base(ema_s, ema_m, ema_l, back_day):
            return True

    return False
