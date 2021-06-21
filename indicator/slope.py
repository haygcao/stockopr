# -*- coding: utf-8 -*-
from indicator.decorator import computed
from util.macd import atr


@computed(column_name='slope')
def compute_slope(quote):
    # ema20 20 天的斜率
    # x: 一个交易日为一个单位
    # y: 涨幅 x20, 即放大20倍
    # 如果一天涨5%, 那么斜率为1, tan(45) = 1,   y/x = 0.05*20/1 = 1
    quote['slope'] = atr(quote)

    return quote