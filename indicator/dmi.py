# -*- coding: utf-8 -*-
from indicator.decorator import computed
from util.macd import dmi


@computed(column_name='adx')
def compute_dmi(quote):
    df = dmi(quote)
    quote['pdi'] = df['pdi']
    quote['mdi'] = df['mdi']
    quote['adx'] = df['adx']
    quote['adxr'] = df['adxr']

    return quote
