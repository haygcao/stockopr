# -*- coding: utf-8 -*-

"""
HOW TO MAKE MONEYIN STOCKS(4TH) WILLIAM J. O'NEIL
P166 绝对不建议投资者买入最近一季度每股收益同比增长幅度不到 18% 或 20% 的股票
P168 最近一个季度的销售额增幅不应低于 25%

增幅下限是最基本要求
C= 可观或者加速增长的当季每股收益和每股销售收入, 如 高于 70% 或者 34% -> 53% -> 107% -> 126%
"""

from indicator import finance as finance_ind


def finance(quote, period, backdays):
    df_finance = finance_ind.finance([quote.code[-1]])

    cond1 = df_finance['dpnp_yoy_ratio'] > 18
    cond2 = df_finance['totaloperatereve_yoy_ratio'] > 25

    v = df_finance['dpnp_yoy_ratio_ins']
    cond3 = (v > 1) | (df_finance['dpnp_yoy_ratio'] > 70)
    cond = cond1 & cond2 & cond3

    return cond[-1]
