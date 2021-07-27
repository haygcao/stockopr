# -*- coding: utf-8 -*-

""" slope 暂未计算, 先由人工判断
"""
import math

import numpy

from acquisition import quote_db
from util import util
from util.macd import ema, atr


vol_times = 5
up_percent = 1.5
almost = 10


def volume(vol, vol_ema_s, vol_ema_m, vol_ema_l, back_day):
    # vol_ema5_shift = vol_ema5.shift(periods=1)
    for n in range(2):
        if vol.iloc[-1 - back_day] > vol_times * vol_ema_s.iloc[-2 - n - back_day]:
            return True
    return False


def price(close, ema_l, ema_xl, ema_xxl, back_day):
    close_ = close.iloc[-1 - back_day]
    return ema_l.iloc[-1 - back_day] < close_   # < ema_l.iloc[-2 - back_day]


def bottom(close, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
    close_ = close.iloc[-2 - back_day]
    return close_ < ema_xl.iloc[-1 - back_day] * up_percent and close_ < ema_xxl.iloc[-1 - back_day] * up_percent


def strong_base(close, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
    xxl_l = ema_xxl.iloc[-20 - 1 - back_day]
    xxl = ema_xxl.iloc[-10 - 1 - back_day]
    xl_l = ema_xl.iloc[-20 - 1 - back_day]
    xl = ema_xl.iloc[-10 - 1 - back_day]

    # print(len(close), xxl, xl, l, m)
    if util.almost_equal(xxl_l, xl_l, almost) and util.almost_equal(xxl, xl, almost) and util.almost_equal(xxl_l, xl, almost):
        return True
    return False


def price_amplitude(amplitude, back_day):
    return amplitude.iloc[-1 - back_day] > 0.05 or amplitude.iloc[:-back_day].max() >= 0.08


def trend(ema_l, back_day):
    return ema_l.iloc[-1 - back_day] > ema_l.iloc[-2 - back_day]


def high_angle(quote, back_day):
    """
    60度角的直角三角形, 三边长度比例为, 1:sqrt(3):2

    In[1]: math.sqrt(3)
    Out[1]: 1.7320508075688772

    In[2]: math.tan(math.radians(60))
    Out[2]: 1.7320508075688767

    In[3]: math.degrees(math.atan(math.sqrt(3)))
    Out[3]: 59.99999999999999
    """
    if back_day == 0:
        return quote.percent.iloc[-1 - back_day] > 15

    low = quote.close.iloc[-back_day - 2]
    series_low = quote.low.iloc[len(quote) - back_day:]
    low_max = series_low.max()
    low_min = series_low.min()
    if low > low_min * 1.1:
        return False

    index = numpy.where(series_low == low_max)[0][0]
    y = (low_max / low - 1) * 20
    x = index + 2

    angle = math.degrees(math.atan(y/x))
    if angle < 45:
        return False

    return True


def super_one_day(quote, vol_ema_s, vol_ema_m, vol_ema_l, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
    vol = quote.volume
    close = quote.close

    if not volume(vol, vol_ema_s, vol_ema_m, vol_ema_l, back_day):
        return False

    # print('volume ok')
    if not price(close, ema_l, ema_xl, ema_xxl, back_day):
        return False

    # print('price ok')
    if not trend(ema_l, back_day):
        return False

    # print('trend ok')
    if not strong_base(close, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
        return False

    # print('strong base ok')
    # if not bottom(close, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
    #     return False

    if not high_angle(quote, back_day):
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

    ema_s = ema(quote['close'], n=5)['ema']
    ema_m = ema(quote['close'], n=10)['ema']
    ema_l = ema(quote['close'], n=30)['ema']
    ema_xl = ema(quote['close'], n=50)['ema']
    # 100 周, 2年...
    ema_xxl = ema(quote['close'], n=100)['ema']
    # ema_xxl = ema_xl

    # 回退 6个月
    for back_day in range(back_days, -1, -1):
        if super_one_day(quote, vol_ema_s, vol_ema_m, vol_ema_l, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
            return True

    return False
