# -*- coding: utf-8 -*-

""" blt
股价突破 vcp 转折点时买入
"""
import numpy

from indicator.decorator import computed
from util.macd import ma


def get_blt_low_index(quote, ema_m, ema_s, ema_xs, back_day, var_ma):
    current = -1 - back_day
    s = ema_s.iloc[current]
    m = ema_m.iloc[current]
    low = quote.low.iloc[current]
    if m < low * 0.98:
        return

    if s < low:
        return

    if quote.close.iloc[current + 1] < quote.high.iloc[current - 1]:
        return

    if quote.close.iloc[current + 1] < s:
        return

    d = {
        'm5': {'days': 5, 'percent_down': 10},
        'm10': {'days': 10, 'percent_down': 20},
        'm25': {'days': 25, 'percent_down': 30},
        'm50': {'days': 50, 'percent_down': 40},
    }

    days = d[var_ma]['days']
    percent_down = d[var_ma]['percent_down']

    close_series = quote.close.iloc[current - days: current + 1]
    close_high = close_series.max()
    index = numpy.where(close_series == close_high)[0][0]
    days = len(close_series) - index

    close_series = quote.close.iloc[current - days + 1: current + 1]
    close_low = close_series.min()
    percent = (1 - close_low/close_high) * 100
    if percent > percent_down:
        return

    vol_series = quote.volume.iloc[current - days + 1: current + 1]
    high = vol_series.max()
    low = vol_series.min()
    percent = (1 - low/high) * 100
    if percent > 50:
        return

    index = numpy.where(close_series == close_low)[0][0]
    index = close_series.index[index]
    # return len(close_series) - index
    return index


def blt_one_day(quote, ema_m, ema_s, ema_xs, back_day, var_ma):
    index = get_blt_low_index(quote, ema_m, ema_s, ema_xs, back_day, var_ma)
    return True if index else False


@computed(column_name='blt')
def blt(quote, period, back_days=125):
    # blt 使用日数据
    ema_xs = ma(quote['close'], n=3)['ma']
    ema_s = ma(quote['close'], n=5)['ma']
    ema_m = ma(quote['close'], n=10)['ma']
    ema_l = ma(quote['close'], n=20)['ma']

    quote.insert(len(quote.columns), 'blt', numpy.nan)
    for back_day in range(back_days, 0, -1):
        current = -1 - back_day
        if blt_one_day(quote, ema_m, ema_s, ema_xs, back_day, var_ma='m10'):
            quote.blt.iat[current] = quote.low.iloc[current]

    return quote
