from acquisition import quote_db


def new_high_new_low(quote, period='day'):
    market = quote_db.get_market_df_db_day(len(quote), end_date=quote.index[-1], period_type=period)

    return market
