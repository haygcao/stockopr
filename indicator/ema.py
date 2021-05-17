from indicator.decorator import computed
from util.macd import ema


@computed(column_name='ema13')
def compute_ema(quote):
    quote['ema13'] = ema(quote, 13)
    quote['ema26'] = ema(quote, 26)

    return quote
