# -*- coding: utf-8 -*-

""" slope 暂未计算, 先由人工判断
"""

from acquisition import quote_db
from util.macd import ema, atr


vol_times = 10
up_percent = 1.1


def volume(vol, vol_ema_s, vol_ema_m, vol_ema_l, back_day):
    # vol_ema5_shift = vol_ema5.shift(periods=1)
    return vol.iloc[-1 - back_day] > vol_times * vol_ema_s.iloc[-2 - back_day]


def price(close, ema_l, ema_xl, ema_xxl, back_day):
    close_ = close.iloc[-1 - back_day]
    return ema_l.iloc[-1 - back_day] < close_   # < ema_l.iloc[-2 - back_day]


def bottom(close, ema_l, ema_xl, ema_xxl, back_day):
    close_ = close.iloc[-2 - back_day]
    return close_ < ema_xl.iloc[-1 - back_day] * up_percent and close_ < ema_xxl.iloc[-1 - back_day] * up_percent


def price_amplitude(amplitude, back_day):
    return amplitude.iloc[-1 - back_day] > 0.05 or amplitude.iloc[:-back_day].max() >= 0.08


def trend(ema_l, back_day):
    return ema_l.iloc[-1 - back_day] > ema_l.iloc[-2 - back_day]


def super_one_day(vol, vol_ema_s, vol_ema_m, vol_ema_l, close, ema_l, ema_xl, ema_xxl, back_day):
    if not volume(vol, vol_ema_s, vol_ema_m, vol_ema_l, back_day):
        return False

    if not price(close, ema_l, ema_xl, ema_xxl, back_day):
        return False

    if not trend(ema_l, back_day):
        return False

    if not bottom(close, ema_l, ema_xl, ema_xxl, back_day):
        return False

    return True


def super(quote, back_days=30):
    # 重采样为 周数据
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')

    vol_series = quote['volume']
    vol_ema_s = ema(vol_series, n=5)['ema']
    vol_ema_m = ema(vol_series, n=10)['ema']
    vol_ema_l = ema(vol_series, n=30)['ema']

    atr5 = atr(quote, 5)['atr']
    close_yest = quote['close'].shift(periods=1)
    amplitude = atr5 / close_yest

    ema_l = ema(quote['close'], n=30)['ema']
    ema_xl = ema(quote['close'], n=50)['ema']
    # 100 周, 2年...
    ema_xxl = ema(quote['close'], n=100)['ema']
    # ema_xxl = ema_xl

    # 回退 6个月
    for back_day in range(0, back_days):
        if super_one_day(vol_series, vol_ema_s, vol_ema_m, vol_ema_l, quote['close'], ema_l, ema_xl, ema_xxl, back_day):
            return True

    return False
