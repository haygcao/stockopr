# -*- coding: utf-8 -*-

""" vcp
股价突破 vcp 转折点时买入
"""

from selector.plugin import blt

from util.macd import ma


def vcp_one_day(quote, low_index, ema_l, ema_m, ema_s, back_day, var_ma='m50'):
    ema_s = ema_s.loc[low_index:]
    ema_s_rshift = ema_s.shift(periods=1)
    ema_s_lshift = ema_s.shift(periods=-1)

    low_list = [ema_s.iloc[0]]
    high_list = []
    for i in range(1, len(ema_s) - 1):
        if ema_s.iloc[i] < ema_s_lshift and ema_s < ema_s_rshift:
            low_list.append(ema_s.iloc[i])
            continue
        if ema_s.iloc[i] > ema_s_lshift and ema_s > ema_s_rshift:
            high_list.append(ema_s.iloc[i])
            continue

    if len(low_list) < 2:
        return False

    for l in [low_list, high_list]:
        list_sorted = l.copy()
        list_sorted.sort()
        if l != list_sorted:
            return False

    return True


def vcp(quote, back_days=30):
    # vcp 使用日数据
    ema_s = ma(quote['close'], n=5)['ma']
    ema_m = ma(quote['close'], n=20)['ma']
    ema_l = ma(quote['close'], n=50)['ma']

    for back_day in range(2, 0, -1):
        low_index = blt.get_blt_low_index(quote, ema_l, ema_m, ema_s, back_day, var_ma='m50')
        if not low_index:
            continue

        if vcp_one_day(quote, low_index, ema_l, ema_m, ema_s, back_day, var_ma='m50'):
            return True
    return False
