# -*- coding: utf-8 -*-

""" vcp
股价突破 vcp 转折点时买入
"""
import numpy

from acquisition import quote_db
from pointor import signal_vcp


def check_price_correction(quote):
    high_of_52week = quote.close[-250:].max()
    low_of_52week = quote.close[-250:].min()
    index = numpy.where(quote.close == high_of_52week)[0][0]
    index_date = quote.index[index].date()

    low = quote.loc[index_date:]['close'].min()
    if (low - low_of_52week) < 0.5 * (high_of_52week - low_of_52week) or low > 0.85 * high_of_52week:
        return False
    return True


def vcp(quote, period, back_days=5):
    if period == 'week':
        quote = quote_db.resample_quote(quote, period_type='W')

    quote = signal_vcp.signal_enter(quote, period='day')
    column_list = ['vcp_signal_enter']

    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-back_days:]) and check_price_correction(quote):
            return True
    return False
