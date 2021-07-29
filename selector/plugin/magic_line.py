# -*- coding: utf-8 -*-

""" 神奇支撑线 10周均线
股价触碰神奇支撑线时买入
"""
import numpy

from acquisition import quote_db
from util import util
from util.macd import ema

# 成交量缩小 50%
g_vol_times = 2
g_up_percent = 40
g_current_close_vs_prev_high_percent = 1.1


def magic_line_one_day(vol, vol_ema_s, vol_ema_m, vol_ema_l, quote, ema_current, ema_xs, ema_s, ema_m, ema_l, back_day):
    current = -1 - back_day

    if quote.low.iloc[current] > ema_current.iloc[current]:
        return False

    ema_series = ema_current.iloc[current - 10: current]
    ema_series_shift = ema_series.shift(periods=1).fillna(ema_series.iloc[0])
    if not (ema_series >= ema_series_shift).all():
        return False

    high_series = quote.high.iloc[current - 10: current]
    prev_high = high_series.max()
    if prev_high > quote.close.iloc[current:].max() * g_current_close_vs_prev_high_percent:
        return False

    prev_high_index = numpy.where(high_series == prev_high)[0][0]
    # index = high_series.index[prev_high_index]
    days = len(high_series) - prev_high_index

    # 3天的涨幅
    close_series = quote.close.iloc[current - days - 5: current - days + 1]
    percent = (close_series.max()/close_series.min() - 1) * 100

    # print('\n{} {} {} {} {}'.format(
    #     quote.code[-1], high_series.index[prev_high_index], percent, close_series.max(), close_series.min()))
    if percent < g_up_percent:
        return False

    # 10周均线向上
    if ema_m.iloc[current] <= ema_m.iloc[current - 1]:
        return False

    # 成交量缩小 30% ~ 50%
    vol_series = vol.iloc[current - 10: current + 1]
    if vol_series.max() < vol_series.min() * g_vol_times:
        return False

    return True


def magic_line(quote, period, back_days=5):
    # 重采样为 周数据
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')

    vol_series = quote['volume']
    vol_ema_s = ema(vol_series, n=5)['ema']
    vol_ema_m = ema(vol_series, n=10)['ema']
    vol_ema_l = ema(vol_series, n=30)['ema']

    ema_xs = ema(quote['close'], n=3)['ema']
    ema_s = ema(quote['close'], n=9)['ema']
    ema_m = ema(quote['close'], n=10)['ema']
    ema_l = ema(quote['close'], n=11)['ema']

    j = 15
    for i in [10, 5, 1]:
        if ema_m.iloc[-j] > ema_m.iloc[-i]:
            return False
        j = i

    # 回退 6个月
    for back_day in range(back_days, -1, -1):
        for e in [ema_m]: # [ema_s, ema_m, ema_l]:
            if magic_line_one_day(vol_series, vol_ema_s, vol_ema_m, vol_ema_l, quote, e,
                                  ema_xs, ema_s, ema_m, ema_l, back_day):
                return True

    return False
