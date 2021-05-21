# -*- coding: utf-8 -*-
import numpy

from indicator import market_deviation


def signal(quote, period, back_days=125):
    quote = market_deviation.compute_index(quote, period, back_days)

    column_list = ['force_index_bull_market_deviation',
                   'macd_bull_market_deviation',
                   'force_index_bear_market_deviation',
                   'macd_bear_market_deviation']

    quote_copy = quote.copy()
    for column in column_list:
        deviation = quote[column]
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
