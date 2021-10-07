# -*- coding: utf-8 -*-
import numpy

from indicator import market_deviation, dynamical_system, market_deviation_mat
from util import dt


def signal_one(quote_copy, column):
    deviation = quote_copy[column]
    # deviation = deviation[deviation < 0] if 'bull' in column else deviation[deviation < 0]
    if 'bull' in column:
        deviation = deviation[deviation > 0]
        signal_column = '{}_signal_enter'.format(column)
    else:
        deviation = deviation[deviation > 0]
        signal_column = '{}_signal_exit'.format(column)
    if signal_column not in quote_copy.columns:
        quote_copy.insert(len(quote_copy.columns), signal_column, numpy.nan)

    for i in range(len(deviation) - 1, 0, -2):
        # quote_copy[signal_all_column][deviation.index[i]] = quote_copy.loc[deviation.index[i], column]
        index_date = deviation.index[i]
        index = numpy.where(quote_copy.index == index_date)[0][0]
        if index == len(quote_copy.index) - 1:
            continue
        index_date_next = quote_copy.index[index + 1]
        quote_copy.loc[index_date_next, signal_column] = quote_copy.loc[index_date_next, 'low']
        # print(deviation.index[i], '0')

    return quote_copy


def signal(quote, column, period, back_days):
    back_days = 0 if dt.istradetime() else back_days
    # quote = market_deviation.compute_index(quote, period, back_days, column)
    quote = market_deviation_mat.compute_index(quote, period, column)

    quote_copy = quote.copy()
    quote_copy = signal_one(quote_copy, column)

    return quote_copy


def signal_enter(quote, period='day', back_days=125, column=None):
    return signal(quote, column, period, back_days)


def signal_exit(quote, period='day', back_days=125, column=None):
    return signal(quote, column, period, back_days)


def signal_enter_and_exit(quote, period, back_days=125):
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    column_list = [
        'asi_bull_market_deviation',
        'force_index_bull_market_deviation',
        'macd_bull_market_deviation',
        'cci_bull_market_deviation',
        'volume_ad_bull_market_deviation',
        'skdj_bull_market_deviation',
        'rsi_bull_market_deviation',

        'asi_bear_market_deviation',
        'force_index_bear_market_deviation',
        'macd_bear_market_deviation',
        'cci_bear_market_deviation',
        'volume_ad_bear_market_deviation',
        'skdj_bear_market_deviation',
        'rsi_bear_market_deviation',
    ]
    for column in column_list:
        # quote = market_deviation.compute_index(quote, period, back_days, column)
        quote = market_deviation_mat.compute_index(quote, period, column)
    return signal(quote, column_list, period, back_days)
