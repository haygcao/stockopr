# -*- coding: utf-8 -*-
import numpy.ma
import pandas

from util.macd import macd

# 牛市背离 bull market deviation
histogram = [-1, -2, -3, -2, -1,
             0, 1,
             0, -1, -2, -1,
             0, 1, 2]

# 牛市背离
histogram = [-1, -2, -3, -2, -1,
             1,
             -1, -2, -1,
             1, 2]

# 牛市背离
histogram = [-1, -2, -3, -2, -1,
             1,
             -1, -2]

# 牛市背离
histogram = [-1, -2, -3, -2, -1,
             1,
             -1, -2, -1]

# 牛市背离
histogram = numpy.array([-1, -2, -3, -2, -1,
                         1, 2, 1,
                         -1, -2, -1])

# 牛市背离
histogram = numpy.array([-1, -2, -3, -2, -1,
                         1, 2, 1,
                         -1, -2, -3,
                         1, 2, 3])


def bull_deviation(quote, histogram, back):
    # back = 125
    # 跳过最右的 histogram 为正的数据, 即可能已经进入夏季
    last_positive = 5

    # 背离的两个 0 的 index, 第一个是向上穿过 0 线的 index, 第二个是向下穿过 0 线的index
    # 忽略可能出现的最右边的向上穿过 0 线(春夏之交)的 index, 与 skip_last_positive 配合

    compute_range = len(histogram) - back
    pos_zero = [0, 0, compute_range-1]
    pos_zero_index = 2
    for index in range(compute_range-1, 0, -1):
        if last_positive > 0:
            if histogram[index] > 0:  # and histogram[index - 1] >= 0:
                last_positive -= 1
                continue
            if histogram[index] == 0 and histogram[index - 1] > 0:
                return False
        if last_positive == 0:
            return False

        last_positive = -1
        if histogram[index] * histogram[index-1] <= 0:
            pos_zero[pos_zero_index] = index
            if pos_zero_index == 0:
                break
            pos_zero_index -= 1

    if pos_zero_index >= 1:
        return False

    min_index = match_index(histogram, pos_zero, compute_range)
    if not min_index:
        return False

    if match_close(quote['close'], min_index):
        first_min_index = quote.index[min_index[0]]
        second_min_index = quote.index[min_index[1]]
        # print('{} {}, {} {}'.format(min_index[0], first_min_index, min_index[0], second_min_index))
        return first_min_index, second_min_index
    return None


def match_index(histogram, pos_zero, compute_range):
    # import pdb; pdb.set_trace()
    end_index = -1 if pos_zero[2] == compute_range - 1 else compute_range - 1
    first_min = min(histogram[pos_zero[0]:pos_zero[1] + 1])
    second_min = min(histogram[pos_zero[2]:end_index])

    if pos_zero[2] - pos_zero[1] < 3:
        return

    np_arr = histogram[pos_zero[2]:end_index]
    second_min_index = numpy.where(np_arr == second_min)[-1][0]
    second_less_zero_count = numpy.ma.sum(np_arr < 0)
    if second_less_zero_count < 3:
        return

    if second_min_index == second_less_zero_count - 1:
        return

    if first_min < second_min:
        if second_min / first_min > 0.7:
            return
        np_arr = histogram[pos_zero[0]:pos_zero[1]]
        first_min_index = numpy.where(np_arr == first_min)[-1][0]
        return first_min_index + pos_zero[0], second_min_index + pos_zero[2]
    return


def match_close(close, min_index):
    first_min_close = close[min_index[0]]
    second_min_close = close[min_index[1]]

    if second_min_close < first_min_close:
        return True
    return False


def niushibeili_macd(quote, back):
    if 'macd_bull_market_deviation' not in quote.columns:
        # quote.insert(-1, 'bull_market_deviation', numpy.nan)
        # quote.loc[:]['macd_bull_market_deviation'] = pandas.Series(numpy.nan, index=quote.index)
        quote = quote.assign(macd_bull_market_deviation=numpy.nan)

    # 价格新低
    # print(quote['close'])
    # MACD 没有新低
    df = macd(quote['close'])
    # import pdb; pdb.set_trace()
    histogram = df[2]

    ret = bull_deviation(quote, histogram, back)
    if ret:
        first_min_index, second_min_index = ret
        quote.loc[first_min_index, 'macd_bull_market_deviation'] = quote.loc[first_min_index, 'low']
        quote.loc[second_min_index, 'macd_bull_market_deviation'] = quote.loc[second_min_index, 'low']

    return quote
