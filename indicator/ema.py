from indicator.decorator import computed


@computed(column_name='ema26')
def compute_ema(quote):
    quote['ema12'] = quote['close'].ewm(span=12, adjust=False).mean()
    quote['ema26'] = quote['close'].ewm(span=26, adjust=False).mean()

    return quote


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()
