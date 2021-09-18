# -*- coding: utf-8 -*-
import numpy
import pandas

from indicator.decorator import computed

g_percent = 3


@computed(column_name='step_ma')
def step(quote, period):
    """
    目标: 筛选上涨阶段, 整理中的股票
    计算周期 [20, 30, 60]
    大一号均线向上
    ma5 或者 ma10 向上
    当前 maN 比其 N天前 上涨
    ma120 > 或约等于 ma150   - 上涨阶段
    """
    ma_periods = [5, 10, 20, 30, 60, 120]  # , 150, 200]  # 会被 second_stage 过滤, 所以, 放到 strong_base
    df_mas = pandas.DataFrame()
    df_mas_shift_p = pandas.DataFrame()
    df_mas_shift_1 = pandas.DataFrame()
    df_mas_shift_2 = pandas.DataFrame()
    for p in ma_periods + [120, 150]:
        df_mas[p] = quote.close.rolling(p).mean()
        df_mas_shift_1[p] = df_mas[p].shift(periods=1)
        df_mas_shift_2[p] = df_mas[p].shift(periods=2)
        df_mas_shift_p[p] = df_mas[p].shift(periods=p)

    quote['step_ma'] = numpy.nan

    # # 两均线接近, 或快速均线在慢速均线之上
    # df_mas['ma_max'] = df_mas[[120, 150]].max(axis=1)
    # df_mas['ma_min'] = df_mas[[120, 150]].min(axis=1)
    # mask = (1 - df_mas['ma_min'] / df_mas['ma_max']) * 100 < 2
    # mask |= (df_mas[120] > df_mas[150])
    #
    # # 近20日有过信号
    # mask_base = mask.rolling(20, min_periods=1).max().astype(bool)
    #
    # # 两均线之差在变大, 即快速均线上涨快于慢速均线
    # for t in [(120, 150)]:
    #     diff = df_mas[t[0]] - df_mas[t[1]]
    #     diff_shift = diff.shift(periods=1)
    #     mask_base &= (diff > diff_shift)

    # ma120 > 或约等于 ma150, 即说明
    # mask_base &= (df_mas[150] > df_mas_shift_1[150])

    ma_periods_tmp = ma_periods.copy()

    # 处理 ma20/ma30/ma60
    for i in range(len(ma_periods) - 3):
        df_mas['ma_max'] = df_mas[ma_periods_tmp[-3:-1]].max(axis=1)
        df_mas['ma_min'] = df_mas[ma_periods_tmp[-3:-1]].min(axis=1)

        slowest = ma_periods_tmp[-2]
        percent = slowest // 10
        percent = max(2, percent)
        percent = min(4, percent)

        # 各均线值接近
        mask = ((1 - df_mas['ma_min']/df_mas['ma_max']) * 100 < percent)
        mask_nan = quote['step_ma'].isna()

        # ma5 大于 ma10
        # mask &= (df_mas[5] > df_mas[10])
        # mask &= (df_mas[10] > df_mas[20])
        # mask &= (df_mas[20] > df_mas[30])

        # 快速均线向上
        # mask &= ((df_mas[5] > df_mas_shift_1[5]) | (df_mas[10] > df_mas_shift_1[10]))

        # 当前均线在最近周期内上涨 15%
        # mask &= ((df_mas[slowest] / df_mas_shift_p[slowest] - 1) * 100 > min(15, (slowest // 10 * 5)))

        # 大一号均线 向上
        for _i in [-1]:
            p = ma_periods_tmp[-1]
            mask &= (df_mas[p] > df_mas_shift_1[p])
            # mask &= (df_mas_shift_1[p] > df_mas_shift_2[p])

        # 当前ma 约等于 ma120 或者 > ma120 15%
        # mask &= ((df_mas[slowest] / df_mas[120] - 1 > 0.15) | ((df_mas[slowest] - df_mas[120]).abs() / df_mas[120] < 0.02))

        quote['step_ma'] = quote['step_ma'].mask(mask & mask_nan, ma_periods_tmp[-2])
        ma_periods_tmp.pop()

    return quote
