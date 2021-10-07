# -*- coding: utf-8 -*-

import numpy
import pandas

from indicator import dynamical_system, second_stage, force_index, ad, skdj, rsi, asi, cci
from indicator.high_low import compute_high_low
from util.macd import macd


def market_deviation(quote, period, values, will=1):
    if 'max_period' not in quote.columns:
        quote = compute_high_low(quote, compute_high=True)
    if 'min_period' not in quote.columns:
        quote = compute_high_low(quote, compute_high=False)

    column = 'low' if will == 1 else 'high'
    val_period_series = quote['{}_period'.format('min' if will == 1 else 'max')]
    val_period_series = val_period_series[val_period_series.notna()]

    deviation_series = pandas.Series(numpy.nan, index=quote.index)
    for i in range(0, len(val_period_series) - 1, 2):
        date1 = val_period_series.index[i]
        date2 = val_period_series.index[i + 1]

        val1 = values.loc[date1]
        val2 = values.loc[date2]

        if will * val_period_series[i] > will * val_period_series[i + 1] and will * val1 < will * val2:
            deviation_series.at[date1] = quote[column].loc[date1]
            deviation_series.at[date2] = quote[column].loc[date2]

    return deviation_series


def market_deviation_macd(quote, period, will):
    # 价格新低
    # print(quote['close'])
    # MACD 没有新低
    df = macd(quote['close'])
    # import pdb; pdb.set_trace()
    quote['macd_line'] = df[0]
    quote['macd_signal'] = df[1]
    quote['macd_histogram'] = df[2]

    column_name = 'macd_bull_market_deviation' if will == 1 else 'macd_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['macd_histogram'], will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


def market_deviation_cci(quote, period, will):
    quote = cci.compute_cci(quote, period)

    column_name = 'cci_bull_market_deviation' if will == 1 else 'cci_bear_market_deviation'

    hist = quote['cci']
    hist = hist.mask((hist < 100) & (hist > -100), numpy.nan)
    deviation_series = market_deviation(quote, period, hist, will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


def market_deviation_asi(quote, period, will):
    quote = asi.compute_asi(quote, period)

    column_name = 'asi_bull_market_deviation' if will == 1 else 'asi_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['asi'], will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


def market_deviation_force_index(quote, period, will):
    # import ipdb;
    # ipdb.set_trace()
    # n = 13 if is_long_period(period) else 2
    n = 13 * 5 if period == 'day' else 13
    quote = force_index.force_index(quote, n=n)

    column_name = 'force_index_bull_market_deviation' if will == 1 else 'force_index_bear_market_deviation'
    deviation_series = market_deviation(quote, period, quote['force_index'], will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


def market_deviation_volume_ad(quote, period, will):
    quote = ad.compute_ad(quote)

    column_name = 'volume_ad_bull_market_deviation' if will == 1 else 'volume_ad_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['adosc'], will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


def market_deviation_skdj(quote, period, will):
    quote = skdj.compute_skdj(quote)

    column_name = 'skdj_bull_market_deviation' if will == 1 else 'skdj_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['d'] - 50, will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


def market_deviation_rsi(quote, period, will):
    quote = rsi.compute_rsi(quote)

    column_name = 'rsi_bull_market_deviation' if will == 1 else 'rsi_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['rsi'] - 50, will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


indicator_func = {
    'asi': market_deviation_asi,
    'force_index': market_deviation_force_index,
    'macd': market_deviation_macd,
    'cci': market_deviation_cci,
    'volume_ad': market_deviation_volume_ad,
    'skdj': market_deviation_skdj,
    'rsi': market_deviation_rsi
}


# @computed(column_name='macd_bull_market_deviation')
def compute_index(quote, period, column):
    if column in quote.columns:
        return quote

    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    quote = second_stage.second_stage(quote, period)

    func = indicator_func[column[:column.index('_b')]]
    for will in [1, -1]:
        quote = func(quote, period, will)

    return quote
