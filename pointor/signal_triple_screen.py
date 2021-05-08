# -*- coding: utf-8 -*-


def function(ema_, macd_):
    if ema_ and macd_:
        return 1

    if not ema_ and not macd_:
        return -1

    return 0


def signal_enter(quote):
    # 长中周期动力系统中，均不为红色，且至少一个为绿色，强力指数为负
    quote['dlxt'] = quote.apply(lambda x: function(x.dlxt_ema13, x.dlxt_macd), axis=1)


def signal_exit(quote):
    # 长中周期动力系统中，波段操作时只要有一个变为红色，短线则任一变为蓝色
    pass