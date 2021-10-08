# -*- encoding: utf-8 -*-
import numpy

from config import config, signal_mask
from indicator import ad, relative_price_strength, dmi
from util import macd


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
    ema = quote.close.ewm(span=26).mean()
    ema_shift = ema.shift(periods=1)
    ema_shift2 = ema.shift(periods=2)
    # 在交易信号出发当天, ema可能上涨, 所以, 检测前一日ema向上是必要的
    mask = (ema < ema_shift) | (ema_shift < ema_shift2)
    # quote.loc[:]['mask_slow_ma_ins'] = (ema <= ema_shift) | (quote.close <= ema)
    quote = quote.assign(mask_slow_ma_ins=mask)  # | (quote.close <= ema)

    # (快均线 - 慢均线) 值增大
    ema_fast = quote.close.ewm(span=12).mean()
    macd_line = ema_fast - ema
    macd_line_shift = macd_line.shift(periods=1)
    # quote.loc[:]['mask_diff_fma_sma_ins'] = (macd_line <= macd_line_shift)
    quote = quote.assign(mask_diff_fma_sma_ins=(macd_line <= macd_line_shift))

    # (快均线 - 慢均线) 值 > 0
    quote = quote.assign(mask_diff_fma_sma_positive=(macd_line < 0))

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
    # df = macd.dmi(quote)
    df = dmi.compute_dmi(quote)
    mask1 = df['pdi'] < df['mdi']
    mask2 = df['adx'] < df['mdi']
    # mask3 = df['adx'] < 50
    # mask4 = df['adx'] < df['adx'].shift(periods=1)
    # mask = mask1 | mask2  # | mask3
    # 在交易信号出发当天, pdi和adx都可能大量上涨, 所以, 检测前一日(pdi > mdi, adx > mdi)是必要的
    mask = mask1 | mask1.shift(periods=2).fillna(True) | mask2 | mask2.shift(periods=2).fillna(True)
    quote = quote.assign(mask_dmi=mask)

    mask = df['adx'] > 50
    mask = mask.rolling(30).max() > 0
    quote = quote.assign(mask_adx_less_n=~mask)

    ma_shift = quote.ma30.shift(periods=120)
    percent = 100 * (quote.close / ma_shift - 1)
    mask = (percent > 50)  # & (percent2.abs() > 50)
    quote = quote.assign(mask_bias_bear=~mask)

    percent = 100 * (1 - quote.close / ma_shift)
    mask = (percent > 45)
    quote = quote.assign(mask_bias_bull=~mask)

    # # pdi > mdi
    # quote = quote.assign(mask_diff_pdi_mdi_positive=mask1)
    #
    # # adx > mdi
    # quote = quote.assign(mask_diff_adx_mdi_positive=mask2)

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
    try:
        quote.loc[:, column] = quote[column].mask(mask, numpy.nan)
    except:
        print(column_mask)

    if column_mask not in signal_mask.mask_trend_up:
        return quote
    if 'exit' in column:
        return quote

    column_mask_exit = 'mask_signal_exit'
    if column_mask_exit not in quote.columns:
        quote[column_mask_exit] = numpy.nan
    mask_shift = mask.shift(periods=1)
    quote.loc[:, column_mask_exit] = quote[column_mask_exit].mask((mask_shift == False) & (mask == True), quote.high)

    return quote
