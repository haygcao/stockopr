# -*- coding: utf-8 -*-
from indicator import force_index


def force_index_positive(quote):
    quote = force_index.force_index(quote)

    return True if quote['force_index'][-1] > 0 else False


def force_index_minus(quote):
    quote = force_index.force_index(quote)

    return True if quote['force_index'][-1] < 0 else False