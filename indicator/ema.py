from indicator.decorator import computed


@computed(column_name='ema13')
def compute_ema(quote):
    quote['ema13'] = quote['close'].ewm(span=13, adjust=False).mean()
    quote['ema26'] = quote['close'].ewm(span=26, adjust=False).mean()

    return quote


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()
