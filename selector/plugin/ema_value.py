import numpy

from pointor import signal_ema_value


def ema_value(quote, back_days=5):
    quote = signal_ema_value.signal_enter(quote, period='day')
    column_list = ['ema_value_signal_enter']

    end_index = None if back_days == 0 else -back_days
    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-1 - back_days: end_index]):
            return True
    return False
