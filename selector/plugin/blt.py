# -*- coding: utf-8 -*-

""" blt
股价突破 vcp 转折点时买入
"""
import numpy

from pointor import signal_blt


def blt(quote, back_days=3):
    quote = signal_blt.signal_enter(quote, period='day')
    column_list = ['blt_signal_enter']

    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-back_days:]):
            return True
    return False
