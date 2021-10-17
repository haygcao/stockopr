# -*- coding: utf-8 -*-

from indicator import value_return
from indicator.decorator import computed, ignore_long_period


def compute_index(quote, period, strict):
    quote = value_return.value_return(quote, period, strict)

    return quote


@computed(column_name='value_return_signal_enter')
@ignore_long_period(column_name='value_return_signal_enter')
def signal_enter(quote, period=None):
    quote = compute_index(quote, period, strict=True)

    quote_copy = quote  # .copy()
    values = quote_copy.value_return.mask(quote_copy.value_return.notna(), quote_copy.low)
    quote_copy.insert(len(quote_copy.columns), 'value_return_signal_enter', values)

    return quote_copy
