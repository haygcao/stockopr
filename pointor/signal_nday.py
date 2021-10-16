# -*- encoding: utf-8 -*-

import numpy

from config.config import is_long_period
from indicator.decorator import computed
from pointor import signal


@computed(column_name='nday_signal_exit')
def signal_exit(quote, period=None):
    if is_long_period(period):
        quote = quote.assign(nday_signal_exit=numpy.nan)
        return quote

    signal_column = 'nday_signal_exit'

    quote = signal.compute_cond_signal(quote, period, signal_column)

    return quote

