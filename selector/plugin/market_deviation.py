import datetime

import numpy

from acquisition import quote_db
from config.config import period_map, USING_LONG_PERIOD, MAX_CLOSE_PAST_DAYS, DECLINE_RATIO
from pointor import signal_market_deviation


def check(quote):
    max_close_date = quote['close'][-250:].idxmax()
    max_close = quote.loc[max_close_date, 'close']
    current_close = quote['close'][-1]
    past_days = (datetime.datetime.now() - max_close_date).days
    if past_days < MAX_CLOSE_PAST_DAYS and current_close / max_close < DECLINE_RATIO:
        return True
    return False


def market_deviation(quote):
    period = 'day'
    if USING_LONG_PERIOD:
        quote_day = quote
        period_type = period_map[period]['long_period']
        quote = quote_db.get_price_info_df_db_week(quote, period_type)
        period = 'week'
    quote = signal_market_deviation.signal_enter(quote, period=period)
    column_list = ['force_index_bull_market_deviation_signal_enter', 'macd_bull_market_deviation_signal_enter']

    days = 20 if period == 'day' else 4
    if period == 'week' and datetime.datetime.today().weekday() < 4:
        days += 1
    for column in column_list:
        deviation = quote[column][-days:]
        if numpy.any(deviation) and check(quote_day):
            return True
    return False
