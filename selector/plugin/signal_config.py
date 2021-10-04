# -*- coding: utf-8 -*-

import numpy

from pointor import signal


def mask_config(quote, period):
    # from config import signal_mask
    # mask_list = signal_mask.signal_mask_column['value_return_signal_enter']
    mask_list = ['mask_slow_ma_ins', 'mask_diff_fma_sma_positive']
    code = quote.code[-1]
    quote = signal.compute_signal(code, period, quote)
    for column in mask_list:
        if quote[column][-1]:
            return False
    return True


def signal_config(quote, period):
    code = quote.code[-1]
    quote = signal.compute_signal(code, period, quote)
    # if not numpy.isnan(quote['signal_enter'][-1]):
    if numpy.any(quote['signal_enter'][-1:]):
        return True
    return False
