# -*- coding: utf-8 -*-
from indicator.decorator import computed
from util.macd import rsi


@computed(column_name='rsi')
def compute_rsi(quote):
    df = rsi(quote)
    quote['rsi'] = df['rsi_12']

    return quote
