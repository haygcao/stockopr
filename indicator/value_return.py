# -*- coding: utf-8 -*-

import numpy

from indicator.decorator import computed

g_percent = 3


@computed(column_name='value_return')
def value_return(quote, period, strict):
    # 使用以下方式计算 ema 时, 在计算 percent = 100 * (1 - ema_l / ema_s) 后,
    # 会导致 quote['value_return'] = quote['ema_value'].mask(mask_final, quote['low']) 报错
    # "Wrong number of dimensions. values.ndim != ndim
    # ema_s = ema(quote, s)
    # ema_l = ema(quote, l)

    quote.insert(len(quote.columns), 'value_return', numpy.nan)
    for s, l in [(12, 26), ]:
        ema_s = quote.close.ewm(span=s, adjust=False).mean()
        ema_l = quote.close.ewm(span=l, adjust=False).mean()
        # ema_s = quote['ma{}'.format(s)]
        # ema_l = quote['ma{}'.format(l)]

        ema_s_shift = ema_s.shift(periods=1)
        ema_l_shift = ema_l.shift(periods=1)

        # diff 可看作 MACD
        diff = ema_s - ema_l
        diff_shift1 = diff.shift(periods=1)

        mask_nan = quote['value_return'].isna()

        # # 慢速ma 在上升   # EMA26 向上
        # mask1 = ema_l >= ema_l_shift

        # # 快速ma 大于 慢速ma   # MACD > 0
        # mask2 = diff > 0

        # 快速ma 比 快速ma 大, 但小于 3%
        # percent = 100 * (1 - ema_l_shift / ema_s_shift)
        # mask3 = util.almost_equal(ema_s, ema_l, 1)
        # mask3 = (percent < g_percent) & (percent > 0)

        # 快速ma 与 慢速ma 在靠近   # MACD 向下/走平 -> 再向上
        if strict:
            diff_shift2 = diff.shift(periods=2)
            diff_shift3 = diff.shift(periods=3)
            mask4 = (diff > diff_shift1) & (diff_shift1 <= diff_shift2) & (diff_shift2 <= diff_shift3)
        else:
            mask4 = diff < diff_shift1

        # FutureWarning: Automatic reindexing on DataFrame vs Series comparisons is deprecated
        # and will raise ValueError in a future version.
        # Do `left, right = left.align(right, axis=1, copy=False)` before e.g. `left == right`
        # mask5 = ema_s >= quote.low
        # mask4 = quote_copy.ema26 / ema26_shift5 > config.period_ema26_oscillation_threshold_map[period]
        mask_final = mask4 & mask_nan   # & mask3
        # mask_final.to_csv('mask1.csv')

        quote['value_return'] = quote['value_return'].mask(mask_final, l)

    return quote
