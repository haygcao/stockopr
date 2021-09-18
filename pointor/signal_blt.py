# -*- coding: utf-8 -*-
import numpy

from config import config
from config.config import is_long_period
from indicator import force_index, dynamical_system, ema, dmi, blt
from indicator.decorator import computed, ignore_long_period, dynamic_system_filter


def compute_index(quote, period=None):
    quote = blt.blt(quote, period)
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    quote = ema.compute_ema(quote)
    quote = dmi.compute_dmi(quote)

    return quote


@computed(column_name='blt_signal_enter')
@ignore_long_period(column_name='blt_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period)

    quote_copy = quote  # .copy()
    quote_copy.insert(len(quote_copy.columns), 'blt_signal_enter', quote_copy.blt)

    # 利用 dmi 过滤掉振荡走势中的信号
    mask1 = quote_copy['adx'] < quote_copy['pdi']
    mask2 = quote_copy['pdi'] < quote_copy['mdi']
    mask3 = quote_copy['adx'] < 50
    mask = mask1 | mask2 | mask3
    quote_copy['blt_signal_enter'] = quote_copy['blt_signal_enter'].mask(mask, numpy.nan)

    return quote_copy
