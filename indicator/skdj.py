from indicator.decorator import computed
from util.macd import skdj


@computed(column_name='k')
def compute_skdj(quote):
    df = skdj(quote)
    quote['k'] = df['k']
    quote['d'] = df['d']
    quote['skdj'] = df['k']

    return quote
