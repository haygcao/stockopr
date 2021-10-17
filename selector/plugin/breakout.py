# -*- coding: utf-8 -*-

import numpy

from pointor import signal_breakout


def blt_breakout(quote, period, back_days):
    quote = signal_breakout.blt_breakout_signal_enter(quote, period)
    return numpy.any(quote['blt_breakout_signal_enter'][-back_days:])


def vcp_breakout(quote, period, back_days):
    quote = signal_breakout.vcp_breakout_signal_enter(quote, period)
    return numpy.any(quote['vcp_breakout_signal_enter'][-back_days:])


def breakout(quote, period, back_days):
    pass
