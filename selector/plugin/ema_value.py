import numpy

from pointor import signal_ema_value


def ema_value(quote):
    quote = signal_ema_value.signal_enter(quote)
    column_list = ['ema_value_signal_enter']
    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-40:]):
            return True
    return False
