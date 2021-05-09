# -*- coding: utf-8 -*-

from util.macd import atr


def compute_atr(quote):
    quote['atr'] = atr(quote)

    return quote
