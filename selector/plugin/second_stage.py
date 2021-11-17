# -*- coding: utf-8 -*-
import numpy

from indicator import second_stage as second_stage_indicator


def second_stage(quote, period, back_days=5):
    quote = second_stage_indicator.second_stage(quote, 'day')

    return not numpy.isnan(quote['second_stage'][-1])
