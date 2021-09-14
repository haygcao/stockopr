# -*- coding: utf-8 -*-

import numpy


def compute_high_low(quote, adj=1):
    close = quote.close
    close_lshift = close.shift(periods=1)
    close_rshift = close.shift(periods=-1)

    days_after = 20
    days_before = 20
    days_before_after = 60
    agg = 'max' if adj == 1 else 'min'
    mask = (adj * close > adj * close_lshift) & (adj * close >= adj * close_rshift)

    close_high_low = quote.close.mask(~mask, numpy.nan)

    close_high_low_agg = eval('close_high_low.rolling({}, min_periods=1).{}()'.format(days_after, agg))
    mask = adj * close_high_low < adj * close_high_low_agg
    close_high_low_adj = close_high_low.mask(mask, numpy.nan)

    close_high_low_adj_lshift = close_high_low_adj.shift(periods=-days_before)
    close_high_low_agg = eval('close_high_low_adj_lshift.rolling({}, min_periods=1).{}()'.format(days_before, agg))
    mask = adj * close_high_low_adj < adj * close_high_low_agg
    mask[:days_before] = True
    series = close_high_low.iloc[:days_before]
    p = eval('series.{}()'.format(agg))
    index = numpy.where(series == p)[0][0]
    date = series.index[index]
    mask.at[date] = False
    close_high_low_adj = close_high_low_adj.mask(mask, numpy.nan)

    close_high_low = close_high_low_adj[close_high_low_adj.notna()]
    # index 不会 shift, 只是值 shift
    # close_high_low_shift = close_high_low.shift(periods=1)
    # days = close_high_low.index - close_high_low_shift.index

    # for i in range(1, len(close_high_low) - 1, 2):
    i = 1
    while i < len(close_high_low):
        delta_before = (close_high_low.index[i] - close_high_low.index[i - 1]).days
        # delta_after = (close_high_low.index[i + 1] - close_high_low.index[i]).days
        if delta_before > days_before_after:  # and delta_after > days_before_after:
            close_high_low.iat[i - 1] = numpy.nan
            i -= 1
        if delta_before < days_before:
            close_high_low.iat[i] = numpy.nan
            i -= 1
        if adj * close_high_low.iloc[i] < adj * close_high_low.iloc[i - 1]:
            close_high_low.iat[i] = numpy.nan
            i -= 1
        i += 2

    if (close_high_low.index[-1] - close_high_low.index[-2]).days > days_before_after:
        close_high_low.iat[-1] = numpy.nan

    close_high_low = close_high_low[close_high_low.notna()]
    if len(close_high_low) % 2 == 1:
        close_high_low = close_high_low.iloc[:-1]

    return close_high_low


def market_deviation(quote, period):
    # close_high = compute_high_low(quote, 1)
    close_low = compute_high_low(quote, -1)
    print('')
