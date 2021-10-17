# -*- encoding: utf-8 -*-

import numpy
import pandas


def compute_vdu(quote, n, percent_shrink):
    vol = quote.volume
    vol_list = [vol]
    for i in range(1, n, 1):
        vol_list.append(vol.shift(periods=i))

    # 3天缩量
    cond1 = pandas.Series(True, index=vol.index)
    for i in range(n - 1):
        cond1 &= (vol_list[i] < vol_list[i + 1])

    # 10天内成交量萎缩 50% 以上
    vol_min = vol_list[0]
    ma_max = vol.rolling(5).max()
    cond2 = 100 * (vol_min / ma_max) < percent_shrink

    quote = quote.assign(vdu=(cond1 & cond2))

    return quote


def volume_dry_up(quote, period, back_days=10):
    percent_shrink = 30
    quote = compute_vdu(quote, 3, percent_shrink)

    return numpy.any(quote.vdu[-back_days:])


def volume_shrink(quote, period, back_days=10):
    percent_shrink = 50
    quote = compute_vdu(quote, 3, percent_shrink)

    return numpy.any(quote.vdu[-back_days:])
