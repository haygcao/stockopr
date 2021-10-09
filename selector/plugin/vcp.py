# -*- coding: utf-8 -*-

""" vcp
股价突破 vcp 转折点时买入
"""
import numpy

from acquisition import quote_db
from pointor import signal_vcp


def vcp(quote, period, back_days=5):
    if period == 'week':
        quote = quote_db.get_price_info_df_db_week(quote, period_type='W')

    quote = signal_vcp.signal_enter(quote, period='day')
    column_list = ['vcp_signal_enter']

    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-back_days:]):
            return True
    return False
