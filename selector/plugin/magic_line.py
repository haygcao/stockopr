# -*- coding: utf-8 -*-

""" 神奇支撑线 10周均线
股价触碰神奇支撑线时买入
"""
from acquisition import quote_db
from util.macd import ema

# 成交量缩小 50%
vol_times = 0.5


def magic_line_one_day(vol, vol_ema_s, vol_ema_m, vol_ema_l, quote, ema_xs, ema_s, ema_m, ema_l, back_day):
    emas = [ema_s, ema_m, ema_l]
    current = -1 - back_day
    for e in emas:
        if quote.low.iloc[current] < e.iloc[current]:
            break
    else:
        return False

    #
    if ema_xs.iloc[current + 1] < ema_xs.iloc[current]:
        return False

    # 10周均线向上
    if ema_m.iloc[current] <= ema_m.iloc[-2 - back_day]:
        return False

    # 成交量缩小 30% ~ 50%
    if vol.iloc[current] > vol.iloc[-10 - 1 - back_day: current].max() * vol_times:
        return False

    return True


def magic_line(quote, period, back_days=3):
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
    for back_day in range(back_days, 1, -1):
        if magic_line_one_day(vol_series, vol_ema_s, vol_ema_m, vol_ema_l, quote, ema_xs, ema_s, ema_m, ema_l, back_day):
            return True

    return False
