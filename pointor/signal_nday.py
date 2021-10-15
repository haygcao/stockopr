# -*- encoding: utf-8 -*-

import numpy

from config.config import is_long_period
from indicator.decorator import computed


@computed(column_name='nday_signal_exit')
def signal_exit(quote, period=None):
    if is_long_period(period):
        quote = quote.assign(nday_signal_exit=numpy.nan)
        return quote

    signal_enter_shift = quote.signal_enter.shift(periods=3)
    quote['nday_signal_exit'] = quote.high.mask(signal_enter_shift.isna(), numpy.nan)

    return quote
