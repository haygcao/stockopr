import numpy

from indicator import ad, dmi
from indicator.decorator import computed


def compute_index(quote, period=None):
    quote = ad.compute_ad(quote)
    quote = dmi.compute_dmi(quote)

    return quote


def signal(quote, direct=1):
    signal_column = 'volume_ad_signal_enter' if direct == 1 else 'volume_ad_signal_exit'
    price_column = 'low' if direct == 1 else 'high'
    quote.insert(len(quote.columns), signal_column, numpy.nan)

    adosc_shift = quote['adosc'].shift(periods=1)
    # adosc_shift_2 = quote['adosc'].shift(periods=2)

    diff = quote.ad - quote.ad_ema
    diff_shift = diff.shift(periods=1)

    # mask1 = (direct * adosc_shift_2 < 0) & (direct * adosc_shift >= 0) & (direct * quote.adosc > direct * adosc_shift)
    mask1 = (direct * adosc_shift < 0) & (direct * quote.adosc >= 0)
    mask2 = (direct * diff_shift < 0) & (direct * diff >= 0)
    mask = mask1 | mask2

    quote[signal_column] = quote[signal_column].mask(mask, quote[price_column])

    return quote


@computed(column_name='volume_ad_signal_enter')
# @ignore_long_period(column_name='force_index_signal_enter')
# @dynamic_system_filter(column_name='force_index_signal_enter')
def signal_enter(quote, period=None):
    # if is_long_period(period):
    #     quote = quote.assign(force_index_signal_enter=numpy.nan)
    #     return quote

    quote = compute_index(quote, period)

    quote = signal(quote, direct=1)

    signal_column = 'volume_ad_signal_enter'
    # 利用 dmi 过滤掉振荡走势中的信号
    mask1 = quote['adx'] < quote['pdi']
    mask2 = quote['adx'] < quote['mdi']
    mask3 = quote['pdi'] < quote['mdi']
    mask = (mask1 & mask2) | mask3
    quote[signal_column] = quote[signal_column].mask(mask, numpy.nan)

    return quote


@computed(column_name='volume_ad_signal_exit')
# @ignore_long_period(column_name='force_index_signal_exit')
def signal_exit(quote, period=None):
    quote = compute_index(quote, period)

    return signal(quote, direct=-1)
