# -*- coding: utf-8 -*-

"""
HOW TO MAKE MONEYIN STOCKS(4TH) WILLIAM J. O'NEIL
P166 绝对不建议投资者买入最近一季度每股收益同比增长幅度不到 18% 或 20% 的股票
P168 最近一个季度的销售额增幅不应低于 25%

增幅下限是最基本要求
C= 可观或者加速增长的当季每股收益和每股销售收入, 如 高于 70% 或者 34% -> 53% -> 107% -> 126%
"""
import pandas

from indicator import finance as finance_ind


def finance(quote, period, backdays):
    df_finance = finance_ind.finance([quote.code[-1]])

    # 按季度
    cond1 = df_finance['dpnp_yoy_ratio'] > 18

    series = df_finance['totaloperatereve_yoy_ratio']
    cond2 = (series > 25) | ((series > 0) & (series.shift(periods=1) > 0) & (series.shift(periods=2) > 0))

    v = df_finance['dpnp_yoy_ratio_ins']
    cond3 = (v > 1) | (df_finance['dpnp_yoy_ratio'] > 70)

    # 按年度
    group = df_finance.groupby(pandas.Grouper(freq='4Q'))
    group_sum = group.sum()
    group_mean = group.mean()

    # 扣非每股收益
    dpnp = group_sum['dedu_parent_profit'][-1]
    dpnp_prev = group_sum['dedu_parent_profit'][-2]

    dpnp_yoy_ratio_4q = (dpnp / dpnp_prev) - 1
    cond4 = dpnp_yoy_ratio_4q > 0.25

    # 收益稳定性
    # cond5 = df_finance['eps_std_rank'] < 25

    # eps_std = df_finance['dpnp_yoy_ratio'].rolling(4).std()
    # cond5 = eps_std < 30   # 40 选出 18 只  # 3年 对应30

    # 净资产收益率
    # roe1 = group_sum['roe'][-1]
    roe = round(100 * group_sum['eps'] / group_mean['bps'], 3)
    cond6 = roe > 17

    cond = cond1 & cond2 & cond3 & cond4 & cond6

    return cond[-1]
