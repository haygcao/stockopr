# -*- encoding: utf-8 -*-
import numpy

from config import config


def compute_enter_mask(quote, period):
    # quote.loc[:]['mask_second_stage'] = (quote['second_stage'] == 0)
    quote = quote.assign(mask_second_stage=(quote['second_stage'] == 0))

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
    quote = quote.assign(mask_step=(~quote.step_ma.isin(config.step_mas)))

    # resistance
    quote = quote.assign(mask_resistance=~(quote.resistance_signal > config.resistance_day))

    # support
    # pandas.Series.eq()
    quote = quote.assign(mask_support=~(quote.support_signal > config.support_day))

    # ad

    # rps

    return quote


def mask_signal(quote, column, column_mask):
    mask = quote[column_mask]
    quote.loc[:, column] = quote[column].mask(mask, numpy.nan)
    return quote
