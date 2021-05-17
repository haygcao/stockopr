# -*- coding: utf-8 -*-

from indicator import market_deviation


def signal(quote, period, back_days=125):
    quote = market_deviation.compute_index(quote, period, back_days)

    return quote
