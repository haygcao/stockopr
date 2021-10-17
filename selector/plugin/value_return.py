import numpy

from pointor import signal_value_return


def value_return(quote, period, back_days=3):
    quote = signal_value_return.signal_enter(quote, period='day')
    column_list = ['value_return_signal_enter']

    # end_index = None if back_days == 0 else -back_days
    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-back_days:]):
            return True
    return False


def value_return_ing(quote, period, back_days=1):
    quote = signal_value_return.compute_index(quote, period, strict=False)

    cond = quote.value_return.notna()

    # end_index = None if back_days == 0 else -back_days
    return numpy.any(cond[-back_days:])
