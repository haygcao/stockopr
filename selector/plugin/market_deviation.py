import datetime

import numpy

from acquisition import quote_db
from config.config import period_map, USING_LONG_PERIOD, MAX_CLOSE_PAST_DAYS, DECLINE_RATIO
from . import dynamical_system
from pointor import signal_market_deviation


def check(quote):
    max_close_date = quote['close'][-250:].idxmax()
    max_close = quote.loc[max_close_date, 'close']
    current_close = quote['close'][-1]
    past_days = (datetime.datetime.now() - max_close_date).days
    if past_days < MAX_CLOSE_PAST_DAYS and current_close / max_close < DECLINE_RATIO:
        return True
    return False


def check_long_period_dynamical_system(quote):
    period = 'day'
    period_type = period_map[period]['long_period']
    quote_week = quote_db.resample_quote(quote, period_type)
    # if dynamical_system.dynamical_system_green(quote_week):
    if dynamical_system.dynamical_system_not_red(quote_week):
        return True
    return False


def market_deviation(quote, period):
    column_list = ['force_index_bull_market_deviation_signal_enter', 'macd_bull_market_deviation_signal_enter']
    column_list = ['macd_bull_market_deviation_signal_enter']

    days = 3 if period == 'day' else 2
    if period == 'week':
        quote = quote_db.resample_quote(quote, period_type='W')
        if datetime.datetime.today().weekday() < 4:
            days += 1
    for column in column_list:
        quote = signal_market_deviation.signal_enter(quote, period=period, column=column[:column.index('_signal')])
        deviation = quote[column][-days:]
        if numpy.any(deviation):
            if period == 'week':
                return True
            if check_long_period_dynamical_system(quote):
                return True
    return False
