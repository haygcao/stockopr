# -*- coding: utf-8 -*-
import math

from util.macd import ema


def force_index(quote, n=2):
    if 'force_index' in quote.columns:
        return quote

    close = quote['close']
    close_shift = close.shift(periods=1)
    si_close = close - close_shift

    volume = quote['volume']
    max_vol = max(volume)
    digit = int(math.log10(max_vol)) + 1
    volume_adjust = volume / pow(10, digit-1)
    si = si_close * volume_adjust
    si_ema = ema(si, n)

    quote_copy = quote.copy()
    quote_copy.loc[:, 'force_index'] = si_ema.values

    return quote_copy


def force_index_positive(quote):
    quote = force_index(quote)

    return True if quote['force_index'][-1] > 0 else False


def force_index_minus(quote):
    quote = force_index(quote)

    return True if quote['force_index'][-1] < 0 else False
