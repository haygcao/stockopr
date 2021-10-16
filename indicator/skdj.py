import pandas

from indicator.decorator import computed


@computed(column_name='k')
def compute_skdj(quote):
    """
    通达信 SKDJ
    N = 9, M = 3
    LOWV:=LLV(LOW,N);
    HIGHV:=HHV(HIGH,N);
    RSV:=EMA((CLOSE-LOWV)/(HIGHV-LOWV)*100,M);
    K:EMA(RSV,M);
    D:MA(K,M);

    from talib import MA_Type
    e.g. slowk_matype=MA_Type.SMA, slowd_matype=MA_Type.SMA
    """
    df = pandas.DataFrame()

    # 9 3 3
    Hn = quote['high'].rolling(9).max()
    Ln = quote['low'].rolling(9).min()
    rsv = (quote['close'] - Ln) / (Hn - Ln) * 100
    rsv = rsv.ewm(span=3, adjust=False).mean()

    quote['k'] = rsv.ewm(span=3, adjust=False).mean()
    quote['d'] = quote.k.rolling(3).mean()
    # quote['j'] = 3*quote.k - 2*quote.d
    quote['skdj'] = quote['k']

    return quote
