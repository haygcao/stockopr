import numpy

from indicator import ad, dmi
from indicator.decorator import computed, dynamic_system_filter


def compute_index(quote, period=None):
    quote = ad.compute_ad(quote)

    return quote


def signal(quote, direct=1):
    signal_column = 'volume_ad_signal_enter' if direct == 1 else 'volume_ad_signal_exit'
    price_column = 'low' if direct == 1 else 'high'
    quote.insert(len(quote.columns), signal_column, numpy.nan)

    adosc_shift = quote['adosc'].shift(periods=1)
    # adosc_shift_2 = quote['adosc'].shift(periods=2)

    diff = quote.ad - quote.ad_ma
    diff_shift = diff.shift(periods=1)

    # mask1 = (direct * adosc_shift_2 < 0) & (direct * adosc_shift >= 0) & (direct * quote.adosc > direct * adosc_shift)
    mask1 = (direct * adosc_shift < 0) & (direct * quote.adosc >= 0)
    mask2 = (direct * diff_shift < 0) & (direct * diff >= 0)
    mask = mask1 | mask2

    quote[signal_column] = quote[signal_column].mask(mask, quote[price_column])

    return quote


@computed(column_name='volume_ad_signal_enter')
# @ignore_long_period(column_name='force_index_signal_enter')
def signal_enter(quote, period=None):
    # if period.startswith('m'):
    #     quote = quote.assign(force_index_signal_enter=numpy.nan)
    #     return quote

    quote = compute_index(quote, period)

    quote = signal(quote, direct=1)

    return quote


@computed(column_name='volume_ad_signal_exit')
# @ignore_long_period(column_name='force_index_signal_exit')
def signal_exit(quote, period=None):
    if period.startswith('m'):
        quote = quote.assign(volume_ad_signal_exit=numpy.nan)
        return quote
    quote = compute_index(quote, period)

    return signal(quote, direct=-1)
