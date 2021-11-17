# -*- coding: utf-8 -*-

from indicator import ema
from . import super


def strong_base(quote, period, back_days):
    """
    时间够长, 才够strong
    """
    back_days = 3

    times = 5  # if period == 'week' else 1

    ema_s = ema.ema(quote['close'], n=times * 5)
    ema_m = ema.ema(quote['close'], n=times * 10)
    ema_l = ema.ema(quote['close'], n=times * 30)

    for back_day in range(back_days, -1, -1):
        if super.strong_base(ema_s, ema_m, ema_l, back_day):
            return True

    return False
