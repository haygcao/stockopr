# -*- coding: utf-8 -*-
import numpy

from indicator import ma
from util import util


def trend_weak(quote, period, back_days):
    back_days = 1
    ma20 = ma.ma(quote.close, 20)
    ma50 = ma.ma(quote.close, 50)

    ma20_shift = ma20.shift(periods=1)
    ma20_shift2 = ma20.shift(periods=2)

    ma50_shift = ma50.shift(periods=1)

    # 连续两天, 仰角越来越小
    cond1 = ((ma20 - ma20_shift) - (ma20_shift - ma20_shift2)) < 0
    # ma20, 仰角小于5度
    angle20 = util.angle_np(1, 100 * (ma20 - ma20_shift) / ma20_shift)
    cond2 = angle20 < 10
    # ma50, 仰角小于5度
    # angle50 = util.angle_np(1, 100 * (ma50 - ma50_shift) / ma50_shift)
    # cond3 = angle50 < 5

    cond = cond1 & cond2  # & cond3

    return numpy.any(cond[-back_days:])
