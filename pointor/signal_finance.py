# -*- coding: utf-8 -*-

"""
HOW TO MAKE MONEYIN STOCKS(4TH) WILLIAM J. O'NEIL
P166 绝对不建议投资者买入最近一季度每股收益同比增长幅度不到 18% 或 20% 的股票
P168 最近一个季度的销售额增幅不应低于 25%

增幅下限是最基本要求
C= 可观或者加速增长的当季每股收益和每股销售收入, 如 高于 70% 或者 34% -> 53% -> 107% -> 126%
"""
import numpy

from indicator import finance
from indicator.decorator import computed


@computed(column_name='finance_signal_enter')
def signal_enter(quote, period):
    quote = finance.compute_finance(quote)

    quote['finance_signal_enter'] = numpy.nan

    mask = (quote['finance'] > 1) | (quote['dpnp_yoy_ratio'] > 70)
    quote['finance_signal_enter'] = quote['finance_signal_enter'].mask(mask, quote.low)

    return quote


@computed(column_name='finance_signal_exit')
def signal_exit(quote, period):
    quote = finance.compute_finance(quote)

    quote['finance_signal_exit'] = numpy.nan

    mask = (quote['finance'] < 1) & (quote['dpnp_yoy_ratio'] < 70)
    quote['finance_signal_exit'] = quote['finance_signal_exit'].mask(mask, quote.high)

    return quote
