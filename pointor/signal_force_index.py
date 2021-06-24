# -*- coding: utf-8 -*-
import datetime

import numpy

from config import config
from config.config import is_long_period
from indicator import force_index, dynamical_system, dmi
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def function_enter(low, dlxt_long_period, dlxt,  dlxt_ema13, force_index, force_index_shift, period, date):
    if dlxt_long_period < 0 or dlxt < 0:
        return numpy.nan

    # ema13 向上, 强力指数下穿 0   # 信号出现时，买单价格设置为比最高价最一个最小单位，如果股价下跌，动态下调买入价，程序自动交易时，放弃
    # if dlxt_ema13 and force_index_shift >= 0 and force_index < 0:   # and dlxt > 0:
    #     return low

    # ema13 向上, 强力指数 <0 或上穿 0
    # if dlxt_ema13 > 0 and (force_index < 0 or force_index_shift < 0):
    #     # print(date, '5')
    #     return low

    # ema13 向上, 强力指数为负, 且开始变大
    if dlxt_ema13 > 0 and force_index_shift < 0 and force_index > force_index_shift:
        return low

    return numpy.nan


def function_exit(high, dlxt_long_period, dlxt, force_index, force_index_shift, period):
    """
    上涨趋势中, 忽略振荡指标的卖出信号
    """
    return numpy.nan

    # 暂时不考虑做空, 即长周期动量为红色时, 是处于空仓状态的
    if dlxt_long_period < 0:
        return numpy.nan

    # if dlxt == 0 and 0 < force_index < force_index_shift:
    #     return high

    return numpy.nan


def compute_index(quote, period=None):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    # 强力指数
    quote = force_index.force_index(quote)

    quote = dmi.compute_dmi(quote)

    return quote


@computed(column_name='force_index_signal_enter')
@ignore_long_period(column_name='force_index_signal_enter')
@dynamic_system_filter(column_name='force_index_signal_enter')
def signal_enter(quote, period=None):
    # if is_long_period(period):
    #     quote = quote.assign(force_index_signal_enter=numpy.nan)
    #     return quote

    quote = compute_index(quote, period)

    column = 'force_index13' if period == 'week' else 'force_index'
    quote_copy = quote  # .copy()
    quote_copy.loc[:, 'force_index_shift'] = quote[column].shift(periods=1)

    # quote_copy.loc[:, 'force_index_signal_enter'] = quote_copy.apply(
    #     lambda x: function_enter(
    #         x.low, x.dlxt_long_period, x.dlxt, x.dlxt_ema13,
    #         x.force_index13 if is_long_period(period) else x.force_index, x.force_index_shift, period, x.name), axis=1)

    # quote_copy = quote_copy.drop(['force_index_signal_enter'], axis=1)
    # dlxt_ema13 > 0 and force_index_shift < 0 and force_index > force_index_shift:
    signal_column = 'force_index_signal_enter'
    quote_copy.insert(len(quote_copy.columns), signal_column, numpy.nan)

    ema26_shift5 = quote['ema26'].shift(periods=5)

    mask1 = quote_copy.dlxt_ema13 > 0
    mask2 = quote_copy.force_index_shift < 0
    mask3 = quote_copy.force_index > quote_copy.force_index_shift
    mask4 = quote_copy.ema26 / ema26_shift5 > config.period_ema26_oscillation_threshold_map[period]
    mask = mask1 & mask2 & mask3 & mask4

    quote_copy[signal_column] = quote_copy[signal_column].mask(mask, quote_copy['low'])

    # 过滤掉振荡走势中的信号
    # 利用 dmi 过滤掉振荡走势中的信号
    mask1 = quote_copy['adx'] < quote_copy['pdi']
    mask2 = quote_copy['adx'] < quote_copy['mdi']
    mask3 = quote_copy['pdi'] < quote_copy['mdi']
    mask = (mask1 & mask2) | mask3
    quote_copy[signal_column] = quote_copy[signal_column].mask(mask, numpy.nan)

    # quote_copy.loc[:, 'force_index_signal_enter'] = force_index_signal_enter.mask(
    #     quote_copy['dlxt_long_period'] < 0, numpy.nan)
    # quote_copy.loc[:, 'force_index_signal_enter'] = force_index_signal_enter.mask(
    #     quote_copy['dlxt'] < 0, numpy.nan)

    # ema26_rolling_min = quote_copy.loc[:, 'ema26'].rolling(20, min_periods=1).min()
    # force_index_signal_enter = quote_copy.loc[:, 'force_index_signal_enter']
    # quote_copy.loc[:, 'force_index_signal_enter'] = force_index_signal_enter.mask(
    #     force_index_signal_enter / ema26_rolling_min < config.period_oscillation_threshold_map[period], numpy.nan)

    # remove temp data
    quote_copy.drop(['force_index_shift'], axis=1, inplace=True)

    return quote_copy


@computed(column_name='force_index_signal_exit')
@ignore_long_period(column_name='force_index_signal_exit')
def signal_exit(quote, period=None):
    # if is_long_period(period):
    #     quote = quote.assign(force_index_signal_exit=numpy.nan)
    #     return quote

    # 长中周期动力系统中，波段操作时只要有一个变为红色，短线则任一变为蓝色
    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()

    signal_column = 'force_index_signal_exit'
    quote_copy.insert(len(quote_copy.columns), signal_column, numpy.nan)

    # remove temp data
    # quote_copy.drop(['force_index_shift'], axis=1, inplace=True)

    return quote_copy


if __name__ == '__main__':
    signal_exit()
