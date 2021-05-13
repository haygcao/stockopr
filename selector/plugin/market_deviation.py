# -*- coding: utf-8 -*-
import numpy.ma
import pandas

from config.config import is_long_period
from selector.plugin import force_index
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


def _market_deviation(quote, histogram, back, will=1):

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
            if will * histogram[index] > 0:  # and histogram[index - 1] >= 0:
                last_positive -= 1
                continue
            if histogram[index] == 0 and will * histogram[index - 1] > 0:
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

    # print('next match index', quote.index[pos_zero[0]], quote.index[pos_zero[1]], quote.index[pos_zero[2]])
    min_index = match_index(histogram, pos_zero, compute_range, will)
    if not min_index:
        return False

    # print('next match close', quote.index[min_index[0]], quote.index[min_index[1]])
    if match_close(quote, min_index, will):
        first_min_index = quote.index[min_index[0]]
        second_min_index = quote.index[min_index[1]]
        # print('{} {}, {} {}'.format(min_index[0], first_min_index, min_index[0], second_min_index))
        return first_min_index, second_min_index
    return None


def match_index(histogram, pos_zero, compute_range, will):
    # import pdb; pdb.set_trace()
    end_index = -1 if pos_zero[2] == compute_range - 1 else compute_range - 1
    if will > 0:
        first_min = min(histogram[pos_zero[0]:pos_zero[1] + 1])
        second_min = min(histogram[pos_zero[2]:end_index])
    else:
        first_min = max(histogram[pos_zero[0]:pos_zero[1] + 1])
        second_min = max(histogram[pos_zero[2]:end_index])

    if pos_zero[2] - pos_zero[1] < 3:
        return

    np_arr = histogram[pos_zero[2]:end_index]
    second_min_index = numpy.where(np_arr == second_min)[-1][0]
    if will > 0:
        second_less_zero_count = numpy.ma.sum(np_arr < 0)
    else:
        second_less_zero_count = numpy.ma.sum(np_arr > 0)
    if second_less_zero_count < 3:
        return

    if second_min_index == second_less_zero_count - 1:
        return

    if will > 0:
        if first_min < second_min:
            if second_min / first_min > 0.7:
                return
            np_arr = histogram[pos_zero[0]:pos_zero[1]]
            first_min_index = numpy.where(np_arr == first_min)[-1][0]
            return first_min_index + pos_zero[0], second_min_index + pos_zero[2]
    else:
        if first_min > second_min:
            if second_min / first_min > 0.7:
                return
            np_arr = histogram[pos_zero[0]:pos_zero[1]]
            first_min_index = numpy.where(np_arr == first_min)[-1][0]
            return first_min_index + pos_zero[0], second_min_index + pos_zero[2]
    return


def match_close(quote, min_index, will):
    if will > 0:
        first_min_close = quote['close'][min_index[0]-1:min_index[0]+1].min()
        second_min_close = quote['close'][min_index[1]-1:min_index[1]+1].min()
        if second_min_close < first_min_close:
            return True
    else:
        first_min_close = quote['close'][min_index[0]-1:min_index[0]+1].max()
        second_min_close = quote['close'][min_index[1]-1:min_index[1]+1].max()
        if second_min_close > first_min_close:
            return True
    return False


def market_deviation(quote, histogram, back, column_name, will):
    # bull market deviation
    if column_name not in quote.columns:
        # column_name = 'macd_bull_market_deviation'
        quote.insert(len(quote.columns), column_name, numpy.nan)
        # quote.loc[:]['macd_bull_market_deviation'] = pandas.Series(numpy.nan, index=quote.index)
        # quote = quote.assign(macd_bull_market_deviation=numpy.nan)
    ret = _market_deviation(quote, histogram, back, will=will)
    if ret:
        first_min_index, second_min_index = ret
        price = 'low' if will > 0 else 'high'
        quote.loc[first_min_index, column_name] = quote.loc[first_min_index, price]
        quote.loc[second_min_index, column_name] = quote.loc[second_min_index, price]

    return quote


def market_deviation_macd(quote, back):
    # 价格新低
    # print(quote['close'])
    # MACD 没有新低
    df = macd(quote['close'])
    # import pdb; pdb.set_trace()
    histogram = df[2]

    quote = market_deviation(quote, histogram, back, 'macd_bull_market_deviation', 1)
    return market_deviation(quote, histogram, back, 'macd_bear_market_deviation', -1)


def market_deviation_force_index(quote, back, period):
    n = 13 if is_long_period(period) else 2
    quote = force_index.force_index(quote, n=n)
    histogram = quote['force_index']

    quote = market_deviation(quote, histogram, back, 'force_index_bull_market_deviation', 1)
    return market_deviation(quote, histogram, back, 'force_index_bear_market_deviation', -1)
