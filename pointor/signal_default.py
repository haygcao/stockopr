# -*- encoding: utf-8 -*-
import numpy

from indicator import cci
from indicator.decorator import computed


@computed(column_name='default_signal_enter')
def signal_enter(quote, period):
    quote = cci.compute_cci(quote, period)
    # close = quote.close
    # close_shift = quote.close.shift(periods=1)
    i = quote.cci
    i_shift = i.shift(periods=1)
    quote['default_signal_enter'] = numpy.nan
    cond = (i > 100) & (i_shift < 100)
    # cond |= (i > i_shift) & (close < close_shift)
    quote['default_signal_enter'] = quote['default_signal_enter'].mask(cond, quote.low)

    return quote


@computed(column_name='default_signal_exit')
def signal_exit(quote, period):
    quote = cci.compute_cci(quote, period)
    # close = quote.close
    # close_shift = quote.close.shift(periods=1)
    i = quote.cci
    i_shift = i.shift(periods=1)

    quote['default_signal_exit'] = numpy.nan
    cond = (i < -100) & (i_shift > -100)
    # cond |= (i < i_shift) & (close > close_shift)
    quote['default_signal_exit'] = quote['default_signal_exit'].mask(cond, quote.high)

    return quote
