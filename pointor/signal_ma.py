# -*- encoding: utf-8 -*-
import numpy

from indicator import ema
from indicator.decorator import computed
from util import util


@computed(column_name='ma_signal_enter')
def signal_enter(quote, period):
    close = quote['close']
    close_yest = close.shift(periods=1)

    quote = ema.compute_ema(quote)
    ema26 = quote['ema26']
    ema26_shift = ema26.shift(periods=1)
    ema26_shift2 = ema26.shift(periods=2)

    # 股价上穿 ema26, 或者ema26 由降转升
    cond = (close_yest <= ema26) | (ema26_shift2 >= ema26_shift)
    cond &= (ema26 > ema26_shift) & (close > ema26)

    if period == 'm5':
        # 30分钟
        ema_l = ema.ema(close, 26 * 6)
        ema_l_shift = ema_l.shift(periods=1)
        angle20 = util.angle_np(1, 100 * (ema_l - ema_l_shift) / ema_l_shift)
        cond &= (angle20 > 10)

    quote['ma_signal_enter'] = numpy.nan
    quote['ma_signal_enter'] = quote['ma_signal_enter'].mask(cond, quote.low)

    return quote


@computed(column_name='ma_signal_exit')
def signal_exit(quote, period):
    close = quote['close']
    close_yest = close.shift(periods=1)

    quote = ema.compute_ema(quote)
    ema26 = quote['ema26']
    ema26_shift = ema26.shift(periods=1)
    ema26_shift2 = ema26.shift(periods=2)

    # 股价下穿 ema26, 或者 ema26 由升转降
    cond = (close_yest >= ema26) | (ema26_shift2 <= ema26_shift)
    cond &= (ema26 < ema26_shift) & (close < ema26)

    if period == 'm5':
        # 30分钟
        ema_l = ema.ema(close, 26 * 6)
        ema_l_shift = ema_l.shift(periods=1)
        angle20 = util.angle_np(1, 100 * (ema_l - ema_l_shift) / ema_l_shift)
        cond &= (angle20 < 5)

    quote['ma_signal_exit'] = numpy.nan
    quote['ma_signal_exit'] = quote['ma_signal_exit'].mask(cond, quote.low)

    return quote
