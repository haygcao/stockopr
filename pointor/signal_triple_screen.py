# -*- coding: utf-8 -*-
import numpy

from acquisition import quote_db
from config.config import period_map
from selector.plugin import dynamical_system, force_index


def function_enter(low, dlxt_long_period, dlxt, dlxt_long_period_shift, dlxt_shift, force_index):
    if dlxt_long_period < 0 or dlxt < 0:
        return numpy.nan

    if dlxt_long_period_shift < dlxt_long_period and dlxt_long_period > 0:
        return low

    if dlxt_shift < dlxt:
        return low

    # if dlxt_long_period > 0 and dlxt > 0:
    #     return low

    if dlxt > 0 and force_index < 0:
        return low

    return numpy.nan


def function_exit(high, dlxt_long_period, dlxt, dlxt_long_period_shift, dlxt_shift):
    if dlxt_long_period_shift > dlxt_long_period:
        return high

    if dlxt_shift > dlxt:
        return high

    return numpy.nan


def compute_period(quote):
    freq = quote.index.to_series().diff().min()
    minutes = freq.value / 10 ** 9 / 60
    if minutes == 5:
        period = 'm5'
    elif minutes == 30:
        period = 'm30'
    elif minutes == 1440:
        period = 'day'
    elif minutes > 1440:
        period = 'week'
    else:
        period = 'm5'

    return period


def compute_index(quote, quote_long_period=None, period=None):
    # 长中周期动力系统中，均不为红色，且至少一个为绿色，强力指数为负
    # pandas.infer_freq(candle.data_origin.index)   # If not continuous pandas.infer_freq will return None.
    if not period:
        period = compute_period(quote)
    period_type = period_map[period]['long_period']
    period_type_reverse = period_map[period]['period']

    # 长周期动力系统
    quote_week = quote_long_period if quote_long_period else quote_db.get_price_info_df_db_week(quote, period_type)
    quote_week = dynamical_system.dynamical_system(quote_week)
    # quote_week.rename(columns={'dlxt': 'dlxt_long_period'}, inplace=True)
    # quote_week.drop(['open', 'close'], axis=1, inplace=True)
    # quote_week = quote_week[['dlxt']]
    dlxt_long_period = quote_week.resample(period_type_reverse).last()
    dlxt_long_period['dlxt'] = quote_week['dlxt'].resample(period_type_reverse).pad()

    quote_copy = quote.copy()
    quote_copy.loc[:, 'dlxt_long_period'] = dlxt_long_period['dlxt']

    # 中周期动力系统
    quote = dynamical_system.dynamical_system(quote)

    quote_copy.loc[:, 'dlxt'] = quote['dlxt']
    quote_copy.loc[:, 'dlxt_long_period_shift'] = dlxt_long_period['dlxt'].shift(periods=1)   # quote['dlxt_long_period'].shift(periods=1)
    quote_copy.loc[:, 'dlxt_shift'] = quote['dlxt'].shift(periods=1)

    # print(quote_week['dlxt'])
    # print(quote['dlxt_long_period'])
    # print(quote['dlxt'])

    # 强力指数
    quote_copy = force_index.force_index(quote_copy)

    return quote_copy


def signal_enter(quote, quote_long_period=None, period=None):
    quote = compute_index(quote, quote_long_period, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'triple_screen_signal_enter'] = quote_copy.apply(
        lambda x: function_enter(x.low, x.dlxt_long_period, x.dlxt, x.dlxt_long_period_shift, x.dlxt_shift,
                                 x.force_index),
        axis=1)

    return quote_copy


def signal_exit(quote, quote_long_period=None, period=None):
    # 长中周期动力系统中，波段操作时只要有一个变为红色，短线则任一变为蓝色
    quote = compute_index(quote, quote_long_period, period)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'triple_screen_signal_exit'] = quote.apply(
        lambda x: function_exit(x.high, x.dlxt_long_period, x.dlxt, x.dlxt_long_period_shift, x.dlxt_shift),
        axis=1)

    return quote_copy


if __name__ == '__main__':
    signal_exit()
