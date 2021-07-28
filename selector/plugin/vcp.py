# -*- coding: utf-8 -*-

""" vcp
股价突破 vcp 转折点时买入
"""
import numpy

from pointor import signal_vcp


def vcp(quote, back_days=3):
    quote = signal_vcp.signal_enter(quote, period='day')
    column_list = ['vcp_signal_enter']

    end_index = None if back_days == 0 else -back_days
    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-1 - back_days: end_index]):
            return True
    return False