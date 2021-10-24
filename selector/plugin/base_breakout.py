# -*- coding: utf-8 -*-
from acquisition import quote_db
from util import util
from indicator.ema import ema
from . import super


def base_breakout_one_day(quote, ema_m, ema_s, back_day):
    if not util.almost_equal(ema_m.iloc[-4 - back_day], ema_s.iloc[-4 - back_day], 10):
        return False

    if not super.high_angle(quote, back_day=back_day + 2):
        return False

    return super.strong_breakout(quote, current=-3 - back_day)


def base_breakout(quote, period):
    # 重采样为 周数据
    # quote = quote_db.resample_quote(quote, period_type='W')

    times = 5
    ema_s = ema(quote['close'], n=times * 5)['ema']
    ema_m = ema(quote['close'], n=times * 10)['ema']

    for back_day in range(1, -1, -1):
        if base_breakout_one_day(quote, ema_m, ema_s, back_day):
            return True
    return False
