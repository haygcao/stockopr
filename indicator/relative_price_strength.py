import numpy
import pandas

from acquisition import quote_db
from config import config


def compute_rps_using_window(quote, market, n):
    stock_percent = quote.close.rolling(n).agg(lambda rows: round(100 * (rows[-1] / rows[0] - 1), 3))
    market_percent = market.close.rolling(n).agg(lambda rows: round(100 * (rows[-1] / rows[0] - 1), 3))

    key = 'rps{}'.format(n)
    quote.loc[:, key] = (stock_percent - market_percent).ewm(span=5, adjust=False).mean()
    # quote.loc[:, key] = stock_percent - market_percent

    return quote


def compute_rps_percent(quote, market, n):
    percent: pandas.Series = quote.percent - market.percent
    percent = percent.cumsum()
    return percent.ewm(span=n, adjust=False).mean()


def compute_rps(quote, market, n, market_index):
    percent: pandas.Series = quote.percent - market.percent
    percent[-1] = percent[-2] if numpy.isnan(percent[-1]) else percent[-1]
    # percent.iat[-1] = percent[-2] if numpy.isnan(percent[-1]) else percent[-1]

    if market_index != 'maq':
        market_index = ''
    quote_copy = quote.copy()
    quote_copy.loc[:, 'rps' + market_index] = percent.loc[:]

    quote_copy.loc[:, 'erps' + market_index] = percent.ewm(span=n, adjust=False).mean()

    return quote_copy


def relative_price_strength(quote, period='day', market_index='maq'):
    period_type = config.period_map[period]['period']
    if market_index != 'maq':
        code = str(quote.code[-1])
        if code[0] == '6':
            market_index = '0000001'
        elif code[0] == '0':
            market_index = '1399001'
        elif code[0] == '3':
            market_index = '1399006'
    market = quote_db.get_price_info_df_db(market_index, len(quote), end_date=quote.index[-1], period_type=period_type)
    # q = quote[~quote.index.isin(market.index)]

    # window
    # for n in [3, 10, 20]:
    #     quote = compute_rps(quote, market, n)

    # percent
    # s1 = compute_rps(quote, market, 3)
    # s2 = compute_rps(quote, market, 10)
    # quote.loc[:, 'rps'] = s1 - s2

    quote = compute_rps(quote, market, 30, market_index)

    return quote
