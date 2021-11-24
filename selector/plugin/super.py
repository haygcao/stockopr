# -*- coding: utf-8 -*-

""" slope 暂未计算, 先由人工判断
"""

import numpy

from util import util
from indicator.ema import ema
from indicator import atr


g_vol_times = 3
g_up_percent = 1.5   # bottom()
g_up_percent_current = 7
g_up_percent_3day = 25
g_almost = 10
g_angle = 45


def volume(vol, vol_ema_s, vol_ema_m, vol_ema_l, back_day):
    # vol_ema5_shift = vol_ema5.shift(periods=1)
    current = -1 - back_day
    if vol.iloc[current: current + 3].mean() > g_vol_times * vol_ema_s.iloc[current - 1]:
        return True
    return False


def price(close, ema_l, ema_xl, ema_xxl, back_day):
    close_ = close.iloc[-1 - back_day]
    return ema_l.iloc[-1 - back_day] < close_   # < ema_l.iloc[-2 - back_day]


def bottom(close, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
    close_ = close.iloc[-2 - back_day]
    return close_ < ema_xl.iloc[-1 - back_day] * g_up_percent and close_ < ema_xxl.iloc[-1 - back_day] * g_up_percent


def strong_base(ema_xs, ema_s, ema_m, ema_l, ema_xl, back_day):
    # xxl = ema_xxl.iloc[-2 - back_day]
    # xl = ema_xl.iloc[-2 - back_day]
    index = -2 - back_day
    h = max(ema_xs.iloc[index], ema_s.iloc[index], ema_m.iloc[index], ema_l.iloc[index], ema_xl.iloc[index])
    l = min(ema_xs.iloc[index], ema_s.iloc[index], ema_m.iloc[index], ema_l.iloc[index], ema_xl.iloc[index])

    index = -250 if len(ema_s) > 250 else -len(ema_s)
    percent = 100 * (h / min(ema_s[index:]) - 1)
    if percent > 300:
        return False

    # print(len(close), xxl, xl, l, m)
    if 100 * (h / l - 1) < g_almost:
        return True
    return False


def price_amplitude(amplitude, back_day):
    return amplitude.iloc[-1 - back_day] > 0.05 or amplitude.iloc[:-back_day].max() >= 0.08


def trend(ema_l, back_day):
    return ema_l.iloc[-1 - back_day] > ema_l.iloc[-2 - back_day]


def strong_breakout(quote, current):
    third = quote.close.iloc[current + 2]
    first_two = quote.high.iloc[current: current + 2]
    first_two_max = first_two.max()

    percent = 100 * (quote.close.iloc[current + 2] / quote.close.iloc[current - 1] - 1)
    if third < first_two_max and percent < g_up_percent_3day:
        return False

    return True


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

    current = -1 - back_day
    tomorrow = current + 1
    after_tomorrow = current + 2
    yest = current - 1
    if quote.percent.iloc[current] < g_up_percent_current:
        return False

    if back_day == 0:
        return True

    yest_close = quote.close.iloc[yest]

    date = quote.index[current]
    if not strong_breakout(quote, current):
        return False

    # if not (quote.percent.iloc[-1 - back_day: -1 - back_day + 3] > 0).all():
    #     return False

    end_index = after_tomorrow + 1 if after_tomorrow < -1 else None
    series_low = quote.low.iloc[tomorrow: end_index]
    if len(series_low) == 0:
        print(quote.code[-1], series_low)
        return False
    low_max = series_low.max()
    low_min = series_low.min()
    if yest_close > low_min * 0.9:
        return False

    index = numpy.where(series_low == low_max)[0][0]
    y = (low_max / yest_close - 1) * 25
    x = index + 2

    angle = util.angle(x, y)
    # print('\n{} {}'.format(quote.code.iloc[-1], angle))
    if angle < g_angle:
        return False

    return True


def super_one_day(quote, vol_ema_s, vol_ema_m, vol_ema_l, ema_xs, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
    vol = quote.volume
    close = quote.close

    if not volume(vol, vol_ema_s, vol_ema_m, vol_ema_l, back_day):
        return False

    if not price(close, ema_l, ema_xl, ema_xxl, back_day):
        return False

    if not trend(ema_l, back_day):
        return False

    # print('trend ok')
    if not strong_base(ema_xs, ema_s, ema_m, ema_l, ema_xl, back_day):
        return False

    # print('strong base ok')
    # if not bottom(close, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
    #     return False

    if not high_angle(quote, back_day):
        return False

    # print('high angle ok')

    return True


def super(quote, period, back_days):
    back_days = 150

    # 重采样为 周数据
    # quote = quote_db.resample_quote(quote, period_type='W')

    times = 5

    vol_series = quote['volume']
    vol_ema_s = ema(vol_series, n=times * 5)
    vol_ema_m = ema(vol_series, n=times * 10)
    vol_ema_l = ema(vol_series, n=times * 30)

    atr5 = atr.compute_atr(quote, 5)['atr']
    close_yest = quote['close'].shift(periods=1)
    amplitude = atr5 / close_yest

    ema_xs = ema(quote['close'], n=times * 2)
    ema_s = ema(quote['close'], n=times * 5)
    ema_m = ema(quote['close'], n=times * 10)
    ema_l = ema(quote['close'], n=times * 30)
    ema_xl = ema(quote['close'], n=times * 40)
    # 100 周, 2年...
    ema_xxl = ema(quote['close'], n=times * 100)
    # ema_xxl = ema_xl

    # 回退 6个月, 最后预留2日, 计算中后推时需要使用
    for back_day in range(back_days, 1, -1):
        if super_one_day(quote, vol_ema_s, vol_ema_m, vol_ema_l, ema_xs, ema_s, ema_m, ema_l, ema_xl, ema_xxl, back_day):
            date = quote.index[-1 - back_day]
            # print(quote.code[-1], date)
            return True

    return False
