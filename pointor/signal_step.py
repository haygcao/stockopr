# -*- coding: utf-8 -*-
import numpy

from indicator import force_index, dynamical_system, ema, dmi, step
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def compute_index(quote, period=None):
    quote = step.step(quote, period)
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    quote = ema.compute_ema(quote)
    quote = dmi.compute_dmi(quote)

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
    # 利用 dmi 过滤掉振荡走势中的信号
    # mask1 = quote_copy['adx'] < quote_copy['pdi']
    # mask2 = quote_copy['pdi'] < quote_copy['mdi']
    # mask3 = quote_copy['adx'] < 50
    # mask = mask1 | mask2   # | mask3
    # quote_copy['vcp_signal_enter'] = quote_copy['vcp_signal_enter'].mask(mask, numpy.nan)

    return quote_copy
