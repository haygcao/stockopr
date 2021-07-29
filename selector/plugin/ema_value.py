import numpy

from pointor import signal_ema_value


def ema_value(quote, period, back_days=3):
    quote = signal_ema_value.signal_enter(quote, period='day')
    column_list = ['ema_value_signal_enter']

    # end_index = None if back_days == 0 else -back_days
    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-back_days:]):
            return True
    return False
