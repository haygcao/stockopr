# -*- coding: utf-8 -*-

from indicator import force_index, dynamical_system, ema, dmi, step
from indicator.decorator import computed, ignore_long_period


def compute_index(quote, period=None):
    quote = step.step(quote, period)
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    quote = ema.compute_ema(quote)

    return quote


@computed(column_name='step_signal_enter')
@ignore_long_period(column_name='step_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()

    mask = quote.step_ma.notna()
    values = quote.step_ma.mask(mask, quote.low[mask])
    quote_copy.insert(len(quote_copy.columns), 'step_signal_enter', values)

    # VCP 属于上涨后缩量调整, 实现筹码由弱方到强方的过程

    return quote_copy
