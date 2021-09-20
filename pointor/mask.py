# -*- encoding: utf-8 -*-
import numpy

from config import config, signal_config
from indicator import dmi, ad, relative_price_strength


def compute_enter_mask(quote, period):
    # quote.loc[:]['mask_second_stage'] = (quote['second_stage'] == 0)
    # pandas.Series 不能使用 is False, e.g.
    # >>> s1 is False
    # False
    # >>> s1 == False
    # 2021-09-14    False
    # 2021-09-15    False
    # dtype: bool
    quote = quote.assign(mask_second_stage=(quote['second_stage'] == False))

    # 动量系统
    # quote.loc[:]['mask_dyn_sys_long_period'] = (quote['dyn_sys_long_period'] < 0)
    # quote.loc[:]['mask_dyn_sys'] = (quote['dyn_sys'] < 0)

    quote = quote.assign(mask_dyn_sys_long_period=(quote['dyn_sys_long_period'] < 0))
    quote = quote.assign(mask_dyn_sys=(quote['dyn_sys'] < 0))

    # 长周期 ema26 向上, 且 close > 长周期 ema26
    n = 26  # if is_long_period(period) else 120
    ema = quote.close.ewm(span=n).mean()
    ema_shift = ema.shift(periods=1)
    # quote.loc[:]['mask_slow_ma_ins'] = (ema <= ema_shift) | (quote.close <= ema)
    quote = quote.assign(mask_slow_ma_ins=(ema <= ema_shift) | (quote.close <= ema))

    # (快均线 - 慢均线) 值增大
    ema_fast = quote.close.ewm(span=int(n / 2)).mean()
    macd_line = ema_fast - ema
    macd_line_shift = macd_line.shift(periods=1)
    # quote.loc[:]['mask_diff_fma_sma_ins'] = (macd_line <= macd_line_shift)
    quote = quote.assign(mask_diff_fma_sma_ins=(macd_line <= macd_line_shift))

    # step
    quote = quote.assign(mask_value_return=(~quote.value_return.isin(config.value_return_mas)))

    # step
    quote = quote.assign(mask_step=(~quote.step_ma.isin(config.step_mas)))

    # resistance
    quote = quote.assign(mask_resistance=~(quote.resistance_signal > config.resistance_day))

    # support
    # pandas.Series.eq()
    quote = quote.assign(mask_support=~(quote.support_signal > config.support_day))

    # dmi
    quote = dmi.compute_dmi(quote)
    mask1 = quote['adx'] < quote['pdi']
    mask2 = quote['pdi'] < quote['mdi']
    mask3 = quote['adx'] < 50
    mask = mask1 | mask2 | mask3
    quote = quote.assign(mask_dmi=mask)

    # ad
    quote = ad.compute_ad(quote)
    # ad_ma 向上
    mask1 = quote['ad_ma'] < quote['ad_ma'].shift(periods=1)
    # ad > ad_ma
    mask2 = quote['ad'] < quote['ad_ma']
    mask = mask1 | mask2
    quote = quote.assign(mask_ad=mask)

    # rps
    quote = relative_price_strength.relative_price_strength(quote)
    # rps_ma 向上
    mask1 = quote['erpsmaq'] < quote['erpsmaq'].shift(periods=1)
    # rps > rps_ma
    mask2 = quote['rpsmaq'] < quote['erpsmaq']
    mask = mask1 | mask2
    quote = quote.assign(mask_rps=mask)

    return quote


def mask_signal(quote, column, column_mask):
    mask = quote[column_mask]
    quote.loc[:, column] = quote[column].mask(mask, numpy.nan)

    if column_mask not in signal_config.mask_trend_up:
        return quote
    if 'exit' in column:
        return quote

    column_op = column.replace('enter', 'exit')
    column_op = column_op if 'deviation' not in column else column_op.replace('bull', 'bear')
    mask_shift = mask.shift(periods=1)
    quote.loc[:, column_op] = quote[column_op].mask((mask_shift == False) & (mask == True), quote.high)

    return quote
