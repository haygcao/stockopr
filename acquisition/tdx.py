import datetime
import time

import pandas

from acquisition import quote_db
from config.config import period_map
from trade_manager import tradeapi
from util import dt
from util.log import logger


def get_kline_data(code, period='day', count=250):
    if period not in ['day', 'week']:
        return

    # week 无法复权
    count = count * 5 if period == 'week' else count
    quote = quote_db.get_price_info_df_db(code, count, period_type='D')

    last_trade_date = dt.get_trade_date()
    last_trade_date_db = quote.index[-1].date()
    if last_trade_date == last_trade_date_db:
        return quote

    t1 = time.time()
    quote_today = tradeapi.fetch_quote(code)
    t2 = time.time()
    logger.info('[{}] fetch quote by tdx cost: [{}s]'.format(code, int(t2 - t1)))

    if not isinstance(quote_today, pandas.Series) or quote_today.close is None:
        logger.error('fetch quote by tdx failed')
        return quote

    quote = quote.append(quote_today)
    quote['rs_rating'].iat[-1] = quote['rs_rating'][-2]
    if period == 'week':
        quote = quote_db.resample_quote(quote, period_type=period_map[period]['period'])
    return quote
