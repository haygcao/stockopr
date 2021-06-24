# -*- coding: utf-8 -*-
from indicator.decorator import computed
from util.macd import ad, ema


@computed(column_name='adosc')
def compute_ad(quote):
    df = ad(quote)
    quote['ad'] = df['ad']
    # quote['ad_ema'] = ema(df['ad'], 26)
    quote['ad_ema'] = df['ad_ema']
    quote['adosc'] = df['adosc']

    return quote
