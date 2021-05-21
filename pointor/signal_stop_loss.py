import datetime

import numpy
import pandas
import pandas as pd

import indicator
from config.config import is_long_period, stop_loss_atr_ratio, stop_loss_atr_back_days, stop_loss_atr_price
from indicator.decorator import computed


# def function(high, close, stop_loss, stop_loss_shift, atr, period):
#     if stop_loss >= stop_loss_shift:
#         return stop_loss - stop_loss_atr_ratio * atr
#
#     return numpy.nan


def function_exit(high, close, stop_loss):
    if close < stop_loss:
        return high

    return numpy.nan


def compute_index(quote, period=None):
    quote = indicator.atr.compute_atr(quote)

    # 牛市背离

    # quote = quote.assign(signal_enter_merged=numpy.nan)
    # signal_enter_merged = quote['signal_enter_merged']
    signal_enter_merged = quote['force_index_bull_market_deviation_signal_enter'].copy()

    # def func(x1, x2):
    #     if numpy.isnan(x1):
    #         return x2
    #
    #     if numpy.isnan(x2):
    #         return x1
    #
    #     return max(x1, x2)
    #
    # column_list = ['force_index_bull_market_deviation_signal_enter',
    #                'macd_bull_market_deviation_signal_enter']
    # for column in column_list:
    #     deviation = quote['macd_bull_market_deviation_signal_enter']
    #     signal_enter_merged = signal_enter_merged.combine(deviation, func=lambda x1, x2: func(x1, x2))

    deviation = quote['macd_bull_market_deviation_signal_enter']
    for i in range(0, len(signal_enter_merged)):
        signal_enter_merged.iloc[i] = max(signal_enter_merged.iloc[i], deviation.iloc[i])

    quote = quote.assign(stop_loss=numpy.nan)
    date_index0 = signal_enter_merged.index[0]
    date_index_list = signal_enter_merged[signal_enter_merged > 0].index.to_list()
    date_index_list.append(quote.index[-1])
    for date_index in date_index_list:
        quote.loc[date_index0:date_index, 'stop_loss'] = quote.loc[date_index0:date_index, stop_loss_atr_price].rolling(stop_loss_atr_back_days, min_periods=1).max() - stop_loss_atr_ratio * quote.loc[date_index0:date_index, 'atr']
        date_index0 = date_index

    return quote

    # quote.loc[:, 'stop_loss_roll_max'] = quote[stop_loss_atr_price].rolling(stop_loss_atr_back_days, min_periods=1).max()
    # quote.loc[:, 'stop_loss_roll_max_shift'] = quote['stop_loss_roll_max'].shift(periods=1)
    #
    # quote_copy = quote.copy()
    # quote_copy.loc[:, 'stop_loss'] = quote_copy.apply(
    #     lambda x: function(x.high, x.close, x.stop_loss_roll_max, x.stop_loss_roll_max_shift, x.atr, period), axis=1)
    #
    # return quote_copy


@computed(column_name='stop_loss_signal_exit')
def signal_exit(quote, period=None):
    if is_long_period(period):
        quote = quote.assign(stop_loss_signal_exit=numpy.nan)
        return quote

    # if 'signal_enter' not in quote.columns:
    #     raise Exception('signal enter not computed')
    signal_enter: pandas.Series = quote['signal_enter']

    quote = compute_index(quote, period)

    quote_copy = quote.copy()
    # quote_copy.loc[:, 'stop_loss_shift'] = quote['stop_loss'].shift(periods=1)
    # quote_copy.loc[:, 'stop_loss_signal_exit'] = quote['close'] < quote['stop_loss']
    quote_copy.loc[:, 'stop_loss_signal_exit'] = quote_copy.apply(
        lambda x: function_exit(x.high, x.close, x.stop_loss), axis=1)

    # remove temp data
    # quote_copy.drop(['stop_loss_shift'], axis=1)

    stop_loss = quote_copy['stop_loss']
    stop_loss_signal_exit = quote_copy['stop_loss_signal_exit']
    stop_loss_signal_exit_tmp = stop_loss_signal_exit[stop_loss_signal_exit > 0]
    date = stop_loss_signal_exit_tmp.index[0] if not stop_loss_signal_exit_tmp.empty else None
    # print(signal_enter[signal_enter > 0])
    while date:
        r = signal_enter[signal_enter.index >= date]
        date_enter = stop_loss_signal_exit.last_valid_index() if r.empty else r.first_valid_index()

        # while date_enter and (not numpy.isnan(quote_copy.loc[date_enter, 'macd_bull_market_deviation'])\
        #         or not numpy.isnan(quote_copy.loc[date_enter, 'force_index_bull_market_deviation'])):
        #     r = signal_enter[signal_enter.index > date_enter]
        #     date_enter = stop_loss_signal_exit.last_valid_index() if r.empty else r.first_valid_index()
        #
        #     # r = numpy.where(stop_loss_signal_exit_tmp.index > date_enter)
        #     # if len(r[0]) > 0:
        #     #     date = stop_loss_signal_exit_tmp.index[r[0][0]]
        #     # else:
        #     #     break
        #     # continue

        # stop_loss_signal_exit = stop_loss_signal_exit.mask(date < stop_loss_signal_exit.index <= date_enter, numpy.nan)
        # mask = stop_loss_signal_exit.index.between(date, date_enter)
        # stop_loss_signal_exit[mask] = numpy.nan
        quote_copy = remove_signal(date, date_enter, quote_copy)

        # A value is trying to be set on a copy of a slice from a DataFrame
        # for s in [stop_loss_signal_exit, stop_loss]:
        #     value = s.loc[date]
        #     s.loc[date:date_enter] = numpy.nan
        #     s.loc[date] = value

        if not date_enter:
            break

        r = stop_loss_signal_exit[stop_loss_signal_exit.index > date_enter]
        if r.empty:
            break
        date = r.first_valid_index()

    return quote_copy


def remove_signal(date, date_enter, quote_copy, inclusive_left=False):
    column_list = ['stop_loss_signal_exit', 'stop_loss']
    # column_list = ['stop_loss_signal_exit']
    for s in column_list:
        value = quote_copy.loc[date, s]
        quote_copy.loc[date:date_enter, s] = numpy.nan
        if date == date_enter:
            continue
        if not inclusive_left:
            quote_copy.loc[date, s] = value

    return quote_copy