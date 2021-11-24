# -*- encoding: utf-8 -*-

from indicator import stop_profit
from indicator.decorator import computed


@computed(column_name='stop_profit_signal_exit')
def signal_exit(quote, period=None):
    quote = stop_profit.stop_profit(quote, period)

    quote['stop_profit_signal_exit'] = quote['stop_profit']

    return quote
