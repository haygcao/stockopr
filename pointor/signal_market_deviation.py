# -*- coding: utf-8 -*-
import numpy

from indicator import market_deviation
from util import dt


def signal_one(quote_copy, column):
    deviation = quote_copy[column]
    # deviation = deviation[deviation < 0] if 'bull' in column else deviation[deviation < 0]
    if 'bull' in column:
        deviation = deviation[deviation > 0]
        signal_all_column = '{}_signal_enter'.format(column)
    else:
        deviation = deviation[deviation > 0]
        signal_all_column = '{}_signal_exit'.format(column)
    if signal_all_column not in quote_copy.columns:
        quote_copy.insert(len(quote_copy.columns), signal_all_column, numpy.nan)
    for i in range(len(deviation) - 1, 0, -2):
        # quote_copy[signal_all_column][deviation.index[i]] = quote_copy.loc[deviation.index[i], column]
        quote_copy.loc[deviation.index[i], signal_all_column] = quote_copy.loc[deviation.index[i], column]
        # print(deviation.index[i], '0')

    return quote_copy


def signal(quote, column, period, back_days):
    back_days = 0 if dt.istradetime() else back_days
    quote = market_deviation.compute_index(quote, period, back_days, column)

    quote_copy = quote.copy()
    quote_copy = signal_one(quote_copy, column)

    return quote_copy


def signal_enter(quote, period='day', back_days=125, column=None):
    return signal(quote, column, period, back_days)


def signal_exit(quote, period='day', back_days=125, column=None):
    return signal(quote, column, period, back_days)


def signal_enter_and_exit(quote, period, back_days=125):
    column_list = ['force_index_bull_market_deviation',
                   'macd_bull_market_deviation',
                   'volume_ad_bull_market_deviation',
                   'skdj_bull_market_deviation',
                   'rsi_bull_market_deviation',
                   'force_index_bear_market_deviation',
                   'macd_bear_market_deviation',
                   'volume_ad_bear_market_deviation',
                   'skdj_bear_market_deviation',
                   'rsi_bear_market_deviation',
                   ]
    for column in column_list:
        quote = market_deviation.compute_index(quote, period, back_days, column)
    return signal(quote, column_list, period, back_days)
