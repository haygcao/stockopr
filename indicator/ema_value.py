import numpy

from indicator.decorator import computed
from util.macd import ema

g_percent = 3


@computed(column_name='ema_value')
def ema_value(quote, period, s, l):
    # 使用以下方式计算 ema 时, 在计算 percent = 100 * (1 - ema_l / ema_s) 后,
    # 会导致 quote['ema_value'] = quote['ema_value'].mask(mask_final, quote['low']) 报错
    # "Wrong number of dimensions. values.ndim != ndim
    # ema_s = ema(quote, s)
    # ema_l = ema(quote, l)

    ema_s = quote.close.ewm(span=s, adjust=False).mean()
    ema_l = quote.close.ewm(span=l, adjust=False).mean()

    ema_s_shift = ema_s.shift(periods=1)
    ema_l_shift = ema_l.shift(periods=1)

    diff = ema_s - ema_l
    diff_shift = ema_s_shift - ema_l_shift

    percent = 100 * (1 - ema_l / ema_s)
    # percent = 100 * (1 - l / s)

    mask1 = ema_l >= ema_l_shift
    mask2 = ema_l <= ema_s
    # mask3 = util.almost_equal(ema_s, ema_l, 1)
    mask3 = (percent < g_percent) & (percent > 0)
    mask4 = diff < diff_shift
    # FutureWarning: Automatic reindexing on DataFrame vs Series comparisons is deprecated
    # and will raise ValueError in a future version.
    # Do `left, right = left.align(right, axis=1, copy=False)` before e.g. `left == right`
    # mask5 = ema_s >= quote.low
    # mask4 = quote_copy.ema26 / ema26_shift5 > config.period_ema26_oscillation_threshold_map[period]
    mask_final = mask1 & mask2 & mask3 & mask4
    # mask_final.to_csv('mask1.csv')

    quote.insert(len(quote.columns), 'ema_value', numpy.nan)
    quote['ema_value'] = quote['ema_value'].mask(mask_final, quote['low'])

    return quote
