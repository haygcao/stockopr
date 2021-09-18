# -*- coding: utf-8 -*-
import numpy

from indicator import dynamical_system, ema, blt
from indicator.decorator import computed, ignore_long_period


def compute_index(quote, period=None):
    quote = blt.blt(quote, period)
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    quote = ema.compute_ema(quote)

    return quote


@computed(column_name='blt_signal_enter')
@ignore_long_period(column_name='blt_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()
    quote_copy.insert(len(quote_copy.columns), 'blt_signal_enter', quote_copy.blt)

    return quote_copy
