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

    # 上穿 ema26
    # cond = (close_yest <= ema26) & (close > ema26)
    cond = (close > ema26)

    ema26_shift = ema26.shift(periods=1)
    cond &= (ema26 > ema26_shift)

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

    # 下穿 ema26
    # cond = (close_yest >= ema26) & (close < ema26)
    cond = (close < ema26)

    ema26_shift = ema26.shift(periods=1)
    cond &= (ema26 < ema26_shift)

    if period == 'm5':
        # 30分钟
        ema_l = ema.ema(close, 26 * 6)
        ema_l_shift = ema_l.shift(periods=1)
        angle20 = util.angle_np(1, 100 * (ema_l - ema_l_shift) / ema_l_shift)
        cond &= (angle20 < 10)

    quote['ma_signal_exit'] = numpy.nan
    quote['ma_signal_exit'] = quote['ma_signal_exit'].mask(cond, quote.low)

    return quote