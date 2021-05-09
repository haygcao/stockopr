# -*- coding: utf-8 -*-

import pandas as pd

from util.macd import macd
from util.macd import ema


def function(ema_, macd_):
    if ema_ and macd_:
        return 1

    if not ema_ and not macd_:
        return -1

    return 0


def dynamical_system(quote, n=13):
    ema13 = ema(quote['close'], n)['ema']
    # ema26 = ema(quote['close'], 26)

    # print(ema13.iloc[-1])
    # print(ema13.values[-1])

    histogram = pd.Series(macd(quote['close'])[2])

    ema13_shift = ema13.shift(periods=1)
    dlxt_ema = ema13 > ema13_shift

    quote_copy = quote.copy()
    quote_copy.loc[:, 'dlxt_ema13'] = dlxt_ema.values

    quote_copy.loc[:, 'macd'] = histogram
    histogram_shift = histogram.shift(periods=1)
    dlxt_macd = histogram > histogram_shift
    quote_copy.loc[:, 'dlxt_macd'] = dlxt_macd.values

    # df.city.apply(lambda x: 1 if 'ing' in x else 0)
    # quote_copy_copy = quote_copy.copy()
    quote_copy.loc[:, 'dlxt'] = quote_copy.apply(lambda x: function(x.dlxt_ema13, x.dlxt_macd), axis=1)

    return quote_copy

    # ema_ = ema13.iloc[-1] > ema13.iloc[-2]
    # macd_ = histogram[-1] > histogram[-2]
    # if ema_ and macd_:
    #     return 1
    #
    # if not ema_ and not macd_:
    #     return -1
    #
    # return 0


def dynamical_system_green(quote):
    quote = dynamical_system(quote)

    return True if quote['dlxt'][-1] == 1 else False


def dynamical_system_red(quote):
    quote = dynamical_system(quote)

    return True if quote['dlxt'][-1] == -1 else False


def dynamical_system_blue(quote):
    quote = dynamical_system(quote)

    return True if quote['dlxt'][-1] == 0 else False
