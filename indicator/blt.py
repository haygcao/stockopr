# -*- coding: utf-8 -*-

""" blt
股价突破 vcp 转折点时买入
"""
import datetime

import numpy

from indicator.decorator import computed
from util import util
from util.macd import ma


def get_high_low_index(quote, emas, vol_ma, back_day, var_ma, first_high='vcp'):
    current = -1 - back_day
    last_trade_date = quote.index[current]

    d = {
        'm5': {'days': 5, 'percent_down': 10, 'vol_percent_down': 50},
        'm10': {'days': 10, 'percent_down': 10, 'vol_percent_down': 50},
        'm25': {'days': 25, 'percent_down': 10, 'vol_percent_down': 50},
        'm50': {'days': 50, 'percent_down': 10, 'vol_percent_down': 50},
    }

    days = d[var_ma]['days']
    percent_down = d[var_ma]['percent_down']
    vol_percent_down = d[var_ma]['vol_percent_down']

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
    # if m < low * 0.98:
    #     return
    #
    # if s < low:
    #     return
    #
    # if quote.close.iloc[current + 1] < quote.high.iloc[current - 1]:
    #     return
    #
    # if quote.close.iloc[current + 1] < s:
    #     return

    # 计算高低点
    ma5 = emas[5].iloc[current - days: current + 1]
    ma5_rshift = ma5.shift(periods=1)
    mask1 = ma5 > ma5_rshift
    mask1_lshift = mask1.shift(periods=-1).fillna(mask1[-1])
    mask2 = mask1 ^ mask1_lshift
    high_low = ma5[mask2]

    high_low_len = len(high_low)
    # MA5 高低点越多, 说明走势越不清晰
    if high_low_len < 3:  # or high_low_len > 6:
        return

    first_high_index = -1

    if first_high == 'vcp':
        # 确定第一个与最后两个high的avg约等的high
        last_high_index = high_low_len - 1 if high_low[-1] > high_low[-2] else high_low_len - 2

        if not util.almost_equal(high_low[last_high_index], high_low[last_high_index - 2], 3):
            return

        avg_high = (high_low[last_high_index] + high_low[last_high_index - 2]) / 2
        max_high = high_low.max()
        if (max_high/avg_high - 1) * 100 > 3:
            return

        for index in range(last_high_index - 2, -1, -2):
            if util.almost_equal(high_low[index], avg_high, 3):
                days_ = (last_trade_date - high_low.index[index]).days
                if days_ >= 10:   # 2周
                    first_high_index = index
                    break
    elif first_high == 'blt':
        # 确定第一个跌幅超过x%的high
        high = high_low[0]
        low = high_low[0]
        for index in range(high_low_len):
            if high_low[index] > high:
                first_high_index = index
                high = high_low[index]
            low = min(high_low[index], low)
            if (1 - low/high) * 100 > 15:
                break
    else:
        return

    if first_high_index < 0:
        return

    delta = datetime.timedelta(days=10)
    close_series = emas[2].loc[high_low.index[0] - delta: high_low.index[first_high_index] + delta]
    # close_series = quote.close.iloc[current - days: current + 1]
    # close_series = emas[2].iloc[current - days: current + 1]
    close_high = close_series.max()
    high_index = numpy.where(close_series == close_high)[0][0]
    high_date = close_series.index[high_index]

    days = len(close_series) - high_index + len(quote.loc[close_series.index[-1]: quote.index[current + 1]]) - 1
    if days == 0:
        return

    # close_series = quote.close.iloc[current - days + 1: current + 1]
    close_series = emas[2].iloc[current - days + 1: current + 1]
    close_low = close_series.min()
    percent = (1 - close_low/close_high) * 100
    if percent < percent_down:
        return

    vol_series = vol_ma.iloc[current - days + 1: current + 1]
    vol_high = vol_series.max()
    vol_low = vol_series.min()
    percent_dec = (1 - vol_low/vol_high) * 100
    if percent_dec < vol_percent_down:
        return

    low_index = numpy.where(close_series == close_low)[0][0]
    low_date = close_series.index[low_index]
    # return len(close_series) - index
    return high_date, low_date


def blt_one_day(quote, emas, vol_ma, back_day, var_ma):
    index = get_high_low_index(quote, emas, vol_ma, back_day, var_ma, first_high='blt')
    return True if index else False


@computed(column_name='blt')
def blt(quote, period, back_days=125):
    # blt 使用日数据
    periods = [2, 5, 10, 20]
    mas = {}
    for p in periods:
        mas.update({p: quote.close.rolling(p).mean()})

    vol_ma = quote.volume.rolling(2).mean()
    quote.insert(len(quote.columns), 'blt', numpy.nan)
    for back_day in range(back_days, 0, -1):
        current = -1 - back_day
        if blt_one_day(quote, mas, vol_ma, back_day, var_ma='m10'):
            quote.blt.iat[current] = quote.low.iloc[current]

    return quote
