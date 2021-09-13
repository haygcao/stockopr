# -*- coding: utf-8 -*-

from indicator import second_stage as second_stage_indicator


def second_stage(quote, period):
    quote = second_stage_indicator.second_stage(quote, 'day')

    return quote['second_stage'][-1]
