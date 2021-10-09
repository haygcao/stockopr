# -*- coding: utf-8 -*-
import numpy

from indicator import force_index, dynamical_system, ema, dmi, vcp
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def compute_index(quote, period=None):
    quote = vcp.vcp(quote, period)
    # quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    # quote = ema.compute_ema(quote)

    return quote


@computed(column_name='vcp_signal_enter')
@ignore_long_period(column_name='vcp_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()

    quote_copy.insert(len(quote_copy.columns), 'vcp_signal_enter', quote_copy.vcp)

    # VCP 属于上涨后缩量调整, 实现筹码由弱方到强方的过程

    return quote_copy
