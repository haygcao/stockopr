from indicator.decorator import computed
from util.macd import macd


@computed(column_name='macd_histogram')
def compute_macd(quote):
    column_name = 'macd_histogram'

    quote[column_name] = macd(quote['close'])[2]

    return quote
