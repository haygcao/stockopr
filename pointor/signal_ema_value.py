# -*- coding: utf-8 -*-
import numpy

from config import config
from config.config import is_long_period
from indicator import force_index, dynamical_system, ema, dmi
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def function_enter(low, close, dlxt_long_period, dlxt, dlxt_ema13, ema13, ema26, ema26_shift, period, date):
    if dlxt_long_period < 0:  # or dlxt < 0:
        return numpy.nan

    # ema13 向上, close 回归 ema13 ~ ema26 价值区间, ema13 >= ema26
    if dlxt_long_period >= 0 and ema26_shift <= ema26 <= ema13 and low <= ema13:
        # print(date, '5')
        return low

    return numpy.nan


def compute_index(quote, period=None):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    quote = ema.compute_ema(quote)
    quote = dmi.compute_dmi(quote)

    return quote


@computed(column_name='ema_value_signal_enter')
@ignore_long_period(column_name='ema_value_signal_enter')
@dynamic_system_filter(column_name='ema_value_signal_enter')
def signal_enter(quote, period=None):
    # if is_long_period(period):
    #     quote = quote.assign(force_index_signal_enter=numpy.nan)
    #     return quote

    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'ema26_shift'] = quote['ema26'].shift(periods=1)
    quote_copy.loc[:, 'ema_value_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(
            x.low, x.close, x.dlxt_long_period, x.dlxt, x.dlxt_ema13, x.ema13, x.ema26, x.ema26_shift, period, x.name),
        axis=1)

    # 利用 dmi 过滤掉振荡走势中的信号
    mask1 = quote_copy['adx'] < quote_copy['pdi']
    mask2 = quote_copy['adx'] < quote_copy['mdi']
    mask3 = quote_copy['pdi'] < quote_copy['mdi']
    mask = (mask1 & mask2) | mask3
    quote_copy['ema_value_signal_enter'] = quote_copy['ema_value_signal_enter'].mask(mask, numpy.nan)

    # 利用 dmi 过滤掉振荡走势中的信号
    # ema26_rolling_min = quote_copy.loc[:, 'ema26'].rolling(20, min_periods=1).min()
    # ema_value_signal_enter = quote_copy.loc[:, 'ema_value_signal_enter']
    # quote_copy.loc[:, 'ema_value_signal_enter'] = ema_value_signal_enter.mask(
    #     ema_value_signal_enter / ema26_rolling_min < config.period_oscillation_threshold_map[period], numpy.nan)

    # remove temp data
    quote_copy.drop(['ema26_shift'], axis=1)

    return quote_copy
