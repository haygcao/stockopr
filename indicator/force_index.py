# -*- coding: utf-8 -*-

import math

from indicator.decorator import computed
from indicator import ema


@computed(column_name='force_index13')
def force_index(quote, n=2):
    if 'force_index' in quote.columns:
        return quote

    close = quote['close']
    close_shift = close.shift(periods=1)
    si_close = close - close_shift

    volume = quote['volume']
    max_vol = max(volume)

    # math.log10(0)
    # ValueError: math domain error
    digit = int(math.log10(max_vol)) + 1
    volume_adjust = volume / pow(10, digit-1)
    si = si_close * volume_adjust

    si_ema = ema.ema(si, 2)
    si_ema13 = ema.ema(si, 13)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'force_index'] = si_ema.values
    quote_copy.loc[:, 'force_index13'] = si_ema13.values

    return quote_copy
