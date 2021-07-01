from acquisition import quote_db


def advance_decline(quote, period='day'):
    market = quote_db.get_market_df_db_day(len(quote), end_date=quote.index[-1], period_type=period)

    ad = market['up'] - market['down']
    ad = ad.cumsum()

    return ad
