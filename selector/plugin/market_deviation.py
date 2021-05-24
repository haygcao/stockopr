import numpy

from pointor import signal_market_deviation


def market_deviation(quote):
    quote = signal_market_deviation.signal_enter(quote)
    column_list = ['force_index_bull_market_deviation', 'macd_bull_market_deviation']
    for column in column_list:
        deviation = quote[column]
        if numpy.any(deviation[-40:]):
            return True
    return False
