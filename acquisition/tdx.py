import datetime

from acquisition import quote_db
from config.config import period_map
from trade_manager import tradeapi


def get_kline_data(code, period='day', count=250):
    if period not in ['day', 'week']:
        return

    # week 无法复权
    count = count * 5 if period == 'week' else count
    quote = quote_db.get_price_info_df_db(code, count, period_type='D')
    now = datetime.datetime.now()
    if quote.index[-1].date() == datetime.date.today() or now.hour < 9 or (now.hour == 9 and now.minute < 30):
        return quote

    quote_today = tradeapi.fetch_quote(code)
    quote = quote.append(quote_today)
    quote['rs_rating'].iat[-1] = quote['rs_rating'][-2]
    if period == 'week':
        quote = quote_db.resample_quote(quote, period_type=period_map[period]['period'])
    return quote
