# -*- coding: utf-8 -*-
import pandas

from indicator import macd, dmi
from indicator.decorator import computed


def compute_strength(quote, trend_up):
    df_up = pandas.DataFrame()

    adj = 1 if trend_up else -1

    ema26 = quote['ema26']
    ema26_shift = ema26.shift(periods=1)
    direct = ema26 > ema26_shift if adj == 1 else ema26 < ema26_shift

    macd_line = quote['macd_line']
    df_up['macd_line'] = direct & (adj * macd_line > 0)
    df_up['macd_line_direct'] = direct & (adj * macd_line > adj * macd_line.shift(periods=1))

    df_up['dmi'] = direct & (adj * quote['pdi'] > adj * quote['mdi'])
    df_up['adx_direct'] = df_up['dmi'] & (quote['adx'] > quote['adx'].shift(periods=1))

    di = 'pdi' if adj == 1 else 'mdi'
    df_up['di_direct'] = df_up['dmi'] & (quote[di] > quote[di].shift(periods=1))
    return df_up.eq(True).sum(axis=1)


@computed(column_name='trend_strength')
def compute_trend_strength(quote, period):
    quote = macd.compute_macd(quote)
    quote = dmi.compute_dmi(quote, period)

    series_up = compute_strength(quote, trend_up=True)
    series_down = compute_strength(quote, trend_up=False)

    quote['trend_strength'] = series_up.mask(series_down != 0, series_down * -1)

    return quote
