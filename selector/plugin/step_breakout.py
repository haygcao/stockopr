# -*- coding: utf-8 -*-

from acquisition import quote_db
import config.config as config
from selector.plugin.bull import bull_ma_one_day
from selector.plugin.step import step_ma


def breakout_ma_one_day(quote, mas, back_day, breakout_percent=config.TP_RANGE):
    # print(quote.code[-1], back_day)
    current = -back_day - 1
    if breakout_percent < 100 * (quote.close[current] / mas[20][current] - 1):  # < breakout_percent + 5:
        return True

    return False


def step_breakout(quote, period, periods=None, almost=1, back_days=3, const_slowest_period=None):
    if period == 'week':
        quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    if periods is None:
        periods = [5, 10, 20, 30, 60]

    mas = {}
    for p in periods:
        mas.update({p: quote.close.rolling(p).mean()})

    # 20天前, 还在整理
    back_day = step_ma(quote, mas, almost, back_days, const_slowest_period)
    if back_day is None:
        return False

    # if not hp_boll(quote):
    #    return False

    # if not step_ma(quote, r=2):
    #    return False

    for back_day in range(back_day, back_day - 5, -1):
        # ma30, ma60 向上
        if not bull_ma_one_day(quote, mas, 3, back_day):
            continue
        if breakout_ma_one_day(quote, mas, back_day):
            break
    else:
        return False

    return True


def step_breakout_p(quote, period, periods=None, almost=1, back_days=3):
    return step_breakout(quote, period, periods, almost, back_days, const_slowest_period=60)
