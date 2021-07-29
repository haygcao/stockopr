# -*- coding: utf-8 -*-

from indicator import second_stage as second_stage_indicator


def second_stage(quote, period):
    return second_stage_indicator.second_stage(quote, 'day')
