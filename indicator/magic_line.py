# -*- coding: utf-8 -*-

""" 神奇支撑线 10周均线
股价触碰神奇支撑线时买入
"""
import numpy

from acquisition import quote_db
from indicator import util
from indicator.decorator import computed
from indicator.ema import ema

# 成交量缩小 50%
g_vol_times = 2
g_up_percent = 40
g_current_close_vs_prev_high_percent = 1.1


@computed(column_name='magic_line')
def magic_line(quote, period):
    if period not in ['day', 'week']:
        quote = quote.assign(magic_line=numpy.nan)
        return quote

    # 重采样为 周数据
    if period == 'day':
        quote_week = quote_db.resample_quote(quote, period_type='W')
    else:
        quote_week = quote

    ema_m = ema(quote_week['close'], n=10)

    cond1 = quote_week.low < ema_m
    # if quote_week.low.iloc[current] > ema_current.iloc[current]:
    #     return False

    s = ema_m >= ema_m.shift(periods=1)
    window = s.rolling(10)
    cond2 = (window.max() == window.min()) & s

    # ema_series = ema_current.iloc[current - 10: current]
    # ema_series_shift = ema_series.shift(periods=1).fillna(ema_series.iloc[0])
    # if not (ema_series >= ema_series_shift).all():
    #     return False

    win_high = quote_week.high.rolling(10)
    cond3 = quote_week.high.rolling(10).max() <= quote_week.close * g_current_close_vs_prev_high_percent
    # high_series = quote_week.high.iloc[current - 10: current]
    # prev_high = high_series.max()
    # if prev_high > quote_week.close.iloc[current:].max() * g_current_close_vs_prev_high_percent:
    #     return False

    win_close = quote_week.close.rolling(10)
    cond4 = (win_close.max() / win_close.min() - 1) * 100 > g_up_percent
    # prev_high_index = numpy.where(high_series == prev_high)[0][0]
    # # index = high_series.index[prev_high_index]
    # days = len(high_series) - prev_high_index
    #
    # # 3天的涨幅
    # close_series = quote_week.close.iloc[current - days - 5: current - days + 1]
    # percent = (close_series.max()/close_series.min() - 1) * 100
    #
    # # print('\n{} {} {} {} {}'.format(
    # #     quote_week.code[-1], high_series.index[prev_high_index], percent, close_series.max(), close_series.min()))
    # if percent < g_up_percent:
    #     return False

    cond5 = ema_m > ema_m.shift(periods=1)
    # # 10周均线向上
    # if ema_m.iloc[current] <= ema_m.iloc[current - 1]:
    #     return False

    win_vol = quote_week.volume.rolling(10)
    cond6 = win_vol.max() > win_vol.min() * g_vol_times

    # # 成交量缩小 30% ~ 50%
    # vol_series = vol.iloc[current - 10: current + 1]
    # if vol_series.max() < vol_series.min() * g_vol_times:
    #     return False

    cond = cond1 & cond2 & cond3 & cond4 & cond5 & cond6
    quote_week['magic_line'] = numpy.nan
    quote_week['magic_line'] = quote_week['magic_line'].mask(cond, quote_week.low)

    if period != 'week':
        quote['magic_line'] = util.resample_long_to_short(quote_week, quote, 'week', period, 'magic_line')

    return quote
