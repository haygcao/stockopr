from indicator.decorator import computed


@computed(column_name='ma5')
def compute_ma(quote):
    periods = [5, 10, 20, 30, 60, 120, 150, 200, 12, 26, 50, 100]
    for _p in periods:
        quote['ma{}'.format(_p)] = quote.close.rolling(_p).mean()

    return quote


def ma(s, n):
    return s.rolling(n).mean()
