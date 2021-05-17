# -*- coding: utf-8 -*-
from indicator.decorator import computed
from util.macd import atr


@computed(column_name='atr')
def compute_atr(quote):
    quote['atr'] = atr(quote)

    return quote
