# -*- coding: utf-8 -*-
import pandas

from indicator import macd, dmi, ema
from indicator.decorator import computed
from util import util


def compute_strength(quote, period, trend_up):
    df = pandas.DataFrame()

    adj = 1 if trend_up else -1

    close_shift = quote['close'].shift(periods=1)
    ema26 = quote['ema26']
    ema26_shift = ema26.shift(periods=1)
    direct = ema26 > ema26_shift if adj == 1 else ema26 < ema26_shift

    macd_line = quote['macd_line']
    macd_line_shift = macd_line.shift(periods=1)
    df['macd_line'] = direct & (adj * macd_line > 0)
    df['macd_signal'] = direct & (adj * quote['macd_signal'] > 0)
    df['macd_hist'] = direct & (adj * quote['macd_histogram'] > 0)
    df['macd_line_direct'] = direct & (adj * macd_line > adj * macd_line_shift)
    df['macd_signal_direct'] = direct & (adj * quote['macd_signal'] > adj * quote['macd_signal'].shift(periods=1))
    df['macd_hist_direct'] = direct & (adj * quote['macd_histogram'] > adj * quote['macd_histogram'].shift(periods=1))

    adx = quote['adx']
    adx_shift = adx.shift(periods=1)
    df['dmi'] = direct & (adj * quote['pdi'] > adj * quote['mdi'])
    df['adx_direct'] = df['dmi'] & (adx > adx_shift)

    di = quote['pdi'] if adj == 1 else quote['mdi']
    di_shift = di.shift(periods=1)
    df['di_direct'] = df['dmi'] & (di > di_shift)

    di2 = quote['mdi'] if adj == 1 else quote['pdi']
    df['strong_di'] = df['dmi'] & (di >= 40) & (di2 <= 10)

    df['strong_adx'] = df['dmi'] & (adx > di)
    df['strong_adx2'] = df['dmi'] & (adx > 50)

    adj_period = 1
    if period == 'week':
        adj_period = 1 / 5
    elif period == 'm30':
        adj_period = 8
    elif period == 'm5':
        adj_period = 6 * 8

    ema_angle_ori = util.angle_np(1, 100 * adj_period * (ema26 - ema26_shift) / ema26_shift)
    ema_angle = ema.ema(ema_angle_ori, 2)
    angle_adj = 0 if adj == 1 else 10

    df['ema_angle_1'] = direct & (adj * ema_angle > 45 - angle_adj)
    df['ema_angle_2'] = direct & (adj * ema_angle > 50 - angle_adj)
    df['ema_angle_3'] = direct & (adj * ema_angle > 55 - angle_adj)
    df['ema_angle_4'] = direct & (adj * ema_angle > 60 - angle_adj)

    # macd_line_angle_ori = util.angle_np(1, 100 * (macd_line - macd_line_shift) / close_shift)
    # macd_line_angle = macd_line_angle_ori  # ema.ema(macd_line_angle_ori, 2)
    # angle_adj = 0 if adj == 1 else 5
    # df['macd_angle_1'] = direct & (adj * macd_line_angle > 15 - angle_adj)
    # df['macd_angle_2'] = direct & (adj * macd_line_angle > 20 - angle_adj)
    # df['macd_angle_3'] = direct & (adj * macd_line_angle > 25 - angle_adj)
    # df['macd_angle_4'] = direct & (adj * macd_line_angle > 30 - angle_adj)

    adx_line_angle_ori = util.angle_np(1, adx - adx_shift)
    adx_line_angle = ema.ema(adx_line_angle_ori, 2)
    df['adx_angle_1'] = df['dmi'] & (adx_line_angle > 60)
    df['adx_angle_2'] = df['dmi'] & (adx_line_angle > 65)
    df['adx_angle_3'] = df['dmi'] & (adx_line_angle > 70)
    df['adx_angle_4'] = df['dmi'] & (adx_line_angle > 75)

    # di_line_angle_ori = util.angle_np(1, di - di_shift)
    # di_line_angle = ema.ema(di_line_angle_ori, 2)
    # df['di_angle_1'] = di_line_angle > 60
    # df['di_angle_2'] = di_line_angle > 65

    # df_tmp = pandas.DataFrame()
    # df_tmp['ema'] = ema_angle
    # df_tmp['adx'] = adx_line_angle
    # df_tmp['macd'] = macd_line_angle

    r = (100 * (df.eq(True).sum(axis=1) / len(df.columns))).astype(int)

    mask = (adx < 20) | ((adx < quote['pdi']) & (adx < quote['mdi']))

    r = r.mask(mask, 0)

    return r


@computed(column_name='trend_strength')
def compute_trend_strength(quote, period, always=False):
    quote = macd.compute_macd(quote, always=always)
    quote = dmi.compute_dmi(quote, period, always=always)

    series_up = compute_strength(quote, period, trend_up=True)
    series_down = compute_strength(quote, period, trend_up=False)

    quote['trend_strength'] = series_up.mask(series_down != 0, series_down * -1)

    return quote
