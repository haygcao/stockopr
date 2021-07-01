from acquisition import quote_db


def up_ema(quote, period, n=52):
    market = quote_db.get_market_df_db_day(len(quote), end_date=quote.index[-1], period_type=period)
    key = 'up_ema{}'.format(n)
    ema = 100 * market[key] / market['count']

    return ema
