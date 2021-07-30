# -*- coding: utf-8 -*-
"""(短期MA - 长期MA) 变小, 即短期长势减弱
"""
import numpy

from util.macd import ma


def value_return_one_day(quote, ma_s, ma_m, back_day):
    current = -1 - back_day
    begin_index = current - 9
    end_index = current + 1 if back_day > 0 else None
    diff = ma_s.iloc[begin_index: end_index] - ma_m.iloc[begin_index: end_index]

    # if diff.iloc[current] > diff.iloc[current - 1]:
    #     return False

    diff_shift = diff.shift(periods=1).fillna(diff.iloc[0])

    count = numpy.count_nonzero(diff < diff_shift)
    # if not ((diff - diff_shift) <= 0).all():
    if (count / len(diff)) < 0.7:
        return False
    # print('\n{} {}'.format(len(diff), count))

    return True


def value_return(quote, period, back_days=20):
    times = 1

    ma_s = ma(quote['close'], n=times * 3)['ma']
    ma_m = ma(quote['close'], n=times * 10)['ma']

    j = 15
    for i in [10, 5, 1]:
        if ma_m.iloc[-j] > ma_m.iloc[-i]:
            return False
        j = i

    if value_return_one_day(quote, ma_s, ma_m, 0):
        return True

    return False
