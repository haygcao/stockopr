# -*- coding: utf-8 -*-

""" 神奇支撑线 10周均线
股价触碰神奇支撑线时买入
"""
from acquisition import quote_db
from util.macd import ema

# 成交量缩小 50%
vol_times = 0.5


def magic_line_one_day(vol, vol_ema_s, vol_ema_m, vol_ema_l, quote, ema_s, ema_m, ema_l, back_day):
    emas = [ema_s, ema_m, ema_l]
    for e in emas:
        if quote.low.iloc[-1 - back_day] < e.iloc[-1 - back_day]:
            break
    else:
        return False

    # 10周均线向上
    if ema_m.iloc[-1 - back_day] <= ema_m.iloc[-2 - back_day]:
        return False

    # 成交量缩小 30% ~ 50%
    if vol.iloc[-1 - back_day] > vol.iloc[-10 - 1 - back_day: -1 - back_day].max() * vol_times:
        return False

    return True


def magic_line(quote, back_days=5):
    # 重采样为 周数据
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')

    vol_series = quote['volume']
    vol_ema_s = ema(vol_series, n=5)['ema']
    vol_ema_m = ema(vol_series, n=10)['ema']
    vol_ema_l = ema(vol_series, n=30)['ema']

    ema_s = ema(quote['close'], n=9)['ema']
    ema_m = ema(quote['close'], n=10)['ema']
    ema_l = ema(quote['close'], n=11)['ema']

    # 回退 6个月
    for back_day in range(0, back_days):
        if magic_line_one_day(vol_series, vol_ema_s, vol_ema_m, vol_ema_l, quote, ema_s, ema_m, ema_l, back_day):
            return True

    return False
