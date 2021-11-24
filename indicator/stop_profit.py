# -*- encoding: utf-8 -*-
import numpy

from indicator import ema
from indicator.decorator import computed


@computed(column_name='stop_profit')
def stop_profit(quote, period):
    close = quote['close']
    close_yest = close.shift(periods=1)

    quote = ema.compute_ema(quote)
    ema26 = quote['ema26']

    series = (close_yest >= ema26) & (close < ema26)

    quote['stop_profit'] = numpy.nan

    quote['stop_profit'] = quote['stop_profit'].mask(series, quote.low)

    return quote
