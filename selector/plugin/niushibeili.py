# -*- coding: utf-8 -*-

from util.macd import macd


def niushibeili(quote):
    # 价格新低
    # MACD 没有新低
    df = macd(quote['close'])
    # import pdb; pdb.set_trace()
    histogram = df[2]

    # 牛市背离
    histogram = [-1, -2, -3, -2, -1,
                 0, 1,
                 0, -1, -2, -1,
                 0, 1, 2]

    # 牛市背离
    histogram = [-1, -2, -3, -2, -1,
                 1,
                 -1, -2, -1,
                 1, 2]

    # 跳过最右的 histogram 为正的数据, 即可能已经进入夏季
    last_positive = 5

    # 背离的两个 0 的 index, 第一个是向上穿过 0 线的 index, 第二个是向下穿过 0 线的index
    # 忽略可能出现的最右边的向上穿过 0 线(春夏之交)的 index, 与 skip_last_positive 配合

    pos_zero = [0, 0, len(histogram)-1]
    pos_zero_index = 2
    for index in range(len(histogram)-1, 0, -1):
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
                if min(histogram[pos_zero[0]:pos_zero[1]+1]) < min(histogram[pos_zero[2]:]):
                    print(pos_zero)
                    return True
            pos_zero_index -= 1
    print(last_positive)
    print(pos_zero)
    print(min(histogram[pos_zero[0]:pos_zero[1] + 1]), min(histogram[pos_zero[2]:]))
    return True if pos_zero_index < 1 else False