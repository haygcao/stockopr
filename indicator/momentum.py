# -*- coding: utf-8 -*-

import calendar
import datetime

import numpy

from acquisition import quote_db
from indicator import util


def compute_fip(quote):
    quote = quote.assign(fip=numpy.nan)

    min_date = quote.index[0]
    max_date = quote.index[-1]

    years = [y for y in range(max_date.year, min_date.year - 1, -1)]

    datetimes = []
    for year in years:
        for month in range(12, 0, -1):
            if year == years[-1]:
                if month < min_date.month:
                    continue
            elif year == years[0]:
                if month > max_date.month:
                    continue

            day = calendar.monthrange(year, month)[1]
            datetimes.append(datetime.datetime(year, month, day))

    for _datetime in datetimes:
        date_index_last = quote.index[quote.index <= _datetime][-1]
        index_last = numpy.where(quote.index == date_index_last)[0][0]
        index_1st = index_last - 250
        index_1st = max(index_1st, 0)
        series_percent = quote.percent.iloc[index_1st:index_last]
        neg = numpy.count_nonzero(series_percent < 0)
        pos = numpy.count_nonzero(series_percent > 0)
        total = len(series_percent)
        coefficient = 1 if quote.loc[date_index_last]['momentum'] > 0 else -1
        fip = coefficient * (neg - pos) / total
        quote.at[date_index_last, 'fip'] = fip

    return quote


def compute_fip2(quote):
    def f(series_percent):
        neg = numpy.count_nonzero(series_percent < 0)
        pos = numpy.count_nonzero(series_percent > 0)
        total = len(series_percent)
        coefficient = 1  # if momentum > 0 else -1
        fip = coefficient * (neg - pos) / total
        return fip

    fip_comp = quote.percent.rolling(250).agg(lambda x: f(x))
    fip = fip_comp.mask(quote.momentum < 0, fip_comp * -1)
    quote['fip'] = fip

    return quote


def momentum_month(quote, period):
    quote_month = quote_db.resample_quote(quote, 'M')
    # m1 = (quote_month.percent/100 + 1).rolling(12).apply(numpy.prod, raw=True) - 1
    quote_month['momentum'] = (quote_month.percent / 100 + 1).rolling(12).apply(lambda x: numpy.prod(x[:-1]) - 1)
    # m2 = (quote.percent/100 + 1).rolling(250).apply(numpy.prod, raw=True) - 1

    momentum_long_period = util.resample_long_to_short(quote_month, quote, 'month', period, column='momentum')
    quote['momentum'] = momentum_long_period

    # quote = compute_fip(quote)
    quote = compute_fip2(quote)

    return quote
