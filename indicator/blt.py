# -*- coding: utf-8 -*-

""" blt
股价突破 vcp 转折点时买入
"""
import datetime

import numpy

from indicator.decorator import computed
from util.macd import ma


def get_blt_high_low_index(quote, emas, back_day, var_ma):
    current = -1 - back_day
    last_trade_date = quote.index[current]

    d = {
        'm5': {'days': 5, 'percent_down': 10},
        'm10': {'days': 10, 'percent_down': 20},
        'm25': {'days': 25, 'percent_down': 30},
        'm50': {'days': 50, 'percent_down': 40},
    }

    days = d[var_ma]['days']
    percent_down = d[var_ma]['percent_down']

    s = emas[5].iloc[current]
    # s_first_date = last_trade_date - datetime.timedelta(days=d['m5']['days'])
    # ema_s = emas[5].loc[s_first_date:]
    # s_first_date = emas[5].index[0]
    # s = ema_s.iloc[0]

    m = emas[10].iloc[current]
    # m_first_date = last_trade_date - datetime.timedelta(days=d['m10']['days'])
    # ema_m = emas[10].loc[m_first_date:]
    # m_first_date = ema_m.index[0]
    # m = ema_m.iloc[0]

    low = quote.low.iloc[current]
    if m < low * 0.98:
        return

    if s < low:
        return

    if quote.close.iloc[current + 1] < quote.high.iloc[current - 1]:
        return

    if quote.close.iloc[current + 1] < s:
        return

    close_series = quote.close.iloc[current - days: current + 1]
    close_high = close_series.max()
    high_index = numpy.where(close_series == close_high)[0][0]
    high_date = close_series.index[high_index]

    days = len(close_series) - high_index

    close_series = quote.close.iloc[current - days + 1: current + 1]
    close_low = close_series.min()
    percent = (1 - close_low/close_high) * 100
    if percent > percent_down:
        return

    vol_series = quote.volume.iloc[current - days + 1: current + 1]
    high = vol_series.max()
    low = vol_series.min()
    percent_dec = (1 - low/high) * 100
    if percent_dec < 50:
        return

    low_index = numpy.where(close_series == close_low)[0][0]
    low_date = close_series.index[low_index]
    # return len(close_series) - index
    return high_date, low_date


def blt_one_day(quote, emas, back_day, var_ma):
    index = get_blt_high_low_index(quote, emas, back_day, var_ma)
    return True if index else False


@computed(column_name='blt')
def blt(quote, period, back_days=125):
    # blt 使用日数据
    periods = [3, 5, 10, 20]
    emas = {}
    for p in periods:
        emas.update({p: quote.close.rolling(p).mean()})

    quote.insert(len(quote.columns), 'blt', numpy.nan)
    for back_day in range(back_days, 0, -1):
        current = -1 - back_day
        if blt_one_day(quote, emas, back_day, var_ma='m10'):
            quote.blt.iat[current] = quote.low.iloc[current]

    return quote
