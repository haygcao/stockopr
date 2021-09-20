# -*- coding: utf-8 -*-

import numpy
import pandas

from indicator import dynamical_system, second_stage, force_index, ad, skdj, rsi
from indicator.decorator import dynamic_system_filter, computed
from util.macd import macd


def compute_high_low(quote, compute_high=True, weak=False):
    """
    以高点计算为例
    1 低于往前20天的高点, 忽略   更低的高点
    2 往前10天以内有过高点, 忽略   太近的高点
    3
    """
    adj = 1 if compute_high else -1
    close = quote.close
    close_lshift = close.shift(periods=1)
    close_rshift = close.shift(periods=-1)

    days_before = 20
    days_before_after = 60
    agg = 'max' if adj == 1 else 'min'
    mask = (adj * close > adj * close_lshift) & (adj * close >= adj * close_rshift)

    close_high_low = quote.close.mask(~mask, numpy.nan)

    # 若往前 20 日已有更大/小值, 则忽略当前值
    close_high_low_agg = eval('close_high_low.rolling({}, min_periods=1).{}()'.format(days_before, agg))
    mask = adj * close_high_low < adj * close_high_low_agg
    close_high_low_adj = close_high_low.mask(mask, numpy.nan)

    # 若往前 20 日已有值, 则忽略当前值, 即保留最早的值(非最值), 忽略后面的更高/低的值, 即时间优先
    # close_high_low_adj_shift = close_high_low_adj.shift(periods=1)
    # mask = close_high_low_adj_shift.rolling(days_before // 2, min_periods=1).apply(lambda _s: _s.any()).fillna(0).astype(bool)
    # close_high_low_adj = close_high_low_adj.mask(mask, numpy.nan)

    # 不应该用到与当前交易日往后的数据
    # close_high_low_adj_lshift = close_high_low_adj.shift(periods=-days_before)
    # close_high_low_agg = eval('close_high_low_adj_lshift.rolling({}, min_periods=1).{}()'.format(days_before, agg))
    # mask = adj * close_high_low_adj < adj * close_high_low_agg
    # mask[:days_before] = True
    # series = close_high_low.iloc[:days_before]
    # p = eval('series.{}()'.format(agg))
    # index = numpy.where(series == p)[0][0]
    # date = series.index[index]
    # mask.at[date] = False
    # close_high_low_adj = close_high_low_adj.mask(mask, numpy.nan)

    close_high_low = close_high_low_adj[close_high_low_adj.notna()]
    # index 不会 shift, 只是值 shift
    # close_high_low_shift = close_high_low.shift(periods=1)
    # days = close_high_low.index - close_high_low_shift.index

    # for i in range(1, len(close_high_low) - 1, 2):
    close_high_low = filter_high_low(adj, close_high_low, days_before, days_before_after, weak)

    column = '{}_period'.format(agg)
    column = 'weak_' + column if weak else column
    quote[column] = quote.close.mask(~quote.index.isin(close_high_low.index), numpy.nan)

    return quote


def filter_high_low(adj, close_high_low, days_before, days_before_after, weak=False):
    adj = adj if not weak else -adj
    i = 1
    i_prev = i - 1
    i_ignore_set = set()
    i_valid = -1
    i_prev_valid = -1
    while i < len(close_high_low):
        delta_before = (close_high_low.index[i] - close_high_low.index[i_prev]).days
        # delta_after = (close_high_low.index[i + 1] - close_high_low.index[i]).days
        if delta_before > days_before_after:  # and delta_after > days_before_after:
            # 忽略曾经的值, 应该是没有问题的
            # 比如 A B C D E 中 C 会被忽略
            # 时间点1, B, AB 值有效
            # 时间点2, C, AB 值有效, C被忽略, 因为 C 为单独的值
            # 时间点3, D, AB 值有效, C被忽略, 因为 C D 间隔时间大于 60 天, D被忽略, 因为 D 为单独的值
            # 时间点4, E, AB 值有效, C被忽略, 因为 C D 间隔时间大于 60 天, DE 值有效
            # 所以, 在 C 之前之后的时间点, 所有高低值是稳定的, 基于高低值计算的信号也是稳定的
            close_high_low.iat[i_prev] = numpy.nan

            # 可能会丢失高低值
            # 比如, A B C, A B 间隔小于 20 天, B 被忽略
            # A C 间隔大于 60 天, A 被忽略
            # B C 间隔大于20天, 小于60天, 属于有效高低值, 但会被忽略
            # i_prev = i
            # i += 1
            i_prev += 1
            i = i + 1 if i == i_prev else i
            continue
        if delta_before < days_before:
            # 可能不会被忽略
            i_ignore_set.add(i)
            i += 1

            # A B C 三个点价格
            # close_high_low.iat[i_prev] = numpy.nan
            # i_prev += 1
            # i = i + 1 if i == i_prev else i
            continue
        if adj * close_high_low.iloc[i] < adj * close_high_low.iloc[i_prev]:
            # close_high_low.iat[i] = numpy.nan
            i_ignore_set.add(i)
            i += 1
            continue

        reset_invalid_value(close_high_low, i, i_ignore_set, i_prev)
        i_valid = i
        i_prev_valid = i_prev
        i += 2
        i_prev = i - 1

        if i_prev >= len(close_high_low):
            break
        # 当矩阵运算未处理近期高低值时, 需要忽略往前近期的次高低值, 即最值优先
        delta_before = (close_high_low.index[i_prev] - close_high_low.index[i_valid]).days
        if delta_before < days_before // 2:
            close_high_low.iat[i_prev] = numpy.nan
            i_prev += 1
            i = i + 1 if i == i_prev else i
            continue
    reset_invalid_value(close_high_low, i_valid, i_ignore_set, i_prev_valid)
    if len(close_high_low) > 1 and (close_high_low.index[-1] - close_high_low.index[-2]).days > days_before_after:
        close_high_low.iat[-1] = numpy.nan
    close_high_low = close_high_low[close_high_low.notna()]
    if len(close_high_low) % 2 == 1:
        close_high_low = close_high_low.iloc[:-1]

    return close_high_low


def reset_invalid_value(close_high_low, i, i_ignore_set, i_prev):
    if i_prev in i_ignore_set:
        i_ignore_set.remove(i_prev)
    if i in i_ignore_set:
        i_ignore_set.remove(i)
    if i_ignore_set:
        close_high_low[list(i_ignore_set)] = numpy.nan


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


@dynamic_system_filter(column_name='macd_bull_market_deviation')
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


@dynamic_system_filter(column_name='force_index_bull_market_deviation')
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


@dynamic_system_filter(column_name='volume_ad_bull_market_deviation')
def market_deviation_volume_ad(quote, period, will):
    quote = ad.compute_ad(quote)

    column_name = 'volume_ad_bull_market_deviation' if will == 1 else 'volume_ad_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['adosc'], will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


@dynamic_system_filter(column_name='skdj_bull_market_deviation')
def market_deviation_skdj(quote, period, will):
    quote = skdj.compute_skdj(quote)

    column_name = 'skdj_bull_market_deviation' if will == 1 else 'skdj_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['d'] - 50, will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


@dynamic_system_filter(column_name='rsi_bull_market_deviation')
def market_deviation_rsi(quote, period, will):
    quote = rsi.compute_rsi(quote)

    column_name = 'rsi_bull_market_deviation' if will == 1 else 'rsi_bear_market_deviation'

    deviation_series = market_deviation(quote, period, quote['rsi'] - 50, will)
    quote.insert(len(quote.columns), column_name, deviation_series)

    return quote


indicator_func = {
    'force_index': market_deviation_force_index,
    'macd': market_deviation_macd,
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
