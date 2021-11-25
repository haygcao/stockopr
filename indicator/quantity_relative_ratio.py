# -*- coding: utf-8 -*-

import datetime
import math

from util import dt


def quantity_relative_ratio(quote, period):
    minutes_day = 4 * 60
    minutes_5day = 5 * minutes_day
    series_vol = quote['volume']
    
    vol_5d = series_vol.rolling(5).sum()
    vol_5d_avg = vol_5d / minutes_5day
    vol_5d_avg_shift = vol_5d_avg.shift(periods=1)

    now = quote.index[-1]
    if now.hour == 0:
        minutes = minutes_day
    else:
        trade_date = now.date()
        am_begin = datetime.datetime(trade_date.year, trade_date.month, trade_date.day, 9, 30, 0)
        am_end = datetime.datetime(trade_date.year, trade_date.month, trade_date.day, 11, 30, 0)
        pm_begin = datetime.datetime(trade_date.year, trade_date.month, trade_date.day, 13, 0, 0)
        pm_end = datetime.datetime(trade_date.year, trade_date.month, trade_date.day, 15, 0, 0)
        if now <= am_end:
            minutes = math.ceil((now - am_begin).seconds / 60)
        elif now <= pm_end:
            minutes = 2 * 60 + math.ceil((now - pm_begin).seconds / 60)
        else:
            minutes = minutes_day

    vol_cur_avg = series_vol / minutes_day
    if minutes != minutes_day:
        vol_cur_avg.iat[-1] = series_vol[-1] / minutes

    series_qrr = round(vol_cur_avg / vol_5d_avg_shift, 2)

    quote['qrr'] = series_qrr

    return quote


