#-*- encoding: utf-8 -*-

import time
import datetime

import copy

import numpy
import pandas

import acquisition.quote_db as quote_db
import acquisition.quote_www as quote_www

import pointor.signal_gd as signal_gd
import dealer.bought as basic
from config import config
from pointor import signal_dynamical_system, signal_channel, signal_market_deviation, signal_force_index, \
    signal_stop_loss, signal_ema_value


def mktime(_datetime):
    # time.mktime((tm_today.tm_year, tm_today.tm_mon, tm_today.tm_mday, 9, 30, 0, 0, 0, 0))
    return int(time.mktime(_datetime.timetuple()))


def function(price, signal_all, signal, column_name):
    # if not isinstance(signal_all, list):
    #     signal_all = []

    if not numpy.isnan(signal):
        signal_all = signal
        # if numpy.isnan(signal_all):
        #     signal_all = 1
        # else:
        #     signal_all += 1

    return signal_all


def function_conflict(signal_enter, signal_exit):
    pass


# supplemental_signal: [(code, date, 'B/S', price), (code, date, 'B/S', price), ...]
def get_supplemental_signal(supplemental_signal_path):
    import csv
    with open(supplemental_signal_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        signal_list = []
        for row in reader:
            row['date'] = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M')
            signal_list.append(row)

    return signal_list


def get_date_period(date, period, quote_date_index):
    ret = quote_date_index[quote_date_index >= date]
    return quote_date_index[-1] if ret.empty else ret[0]


def compute_signal(quote, period, supplemental_signal_path=None):
    # 动力系统
    quote = signal_dynamical_system.signal_enter(quote, period=period)
    quote = signal_dynamical_system.signal_exit(quote, period=period)

    # 通道
    quote = signal_channel.signal_enter(quote, period=period)
    quote = signal_channel.signal_exit(quote, period=period)

    # 背离
    quote = signal_market_deviation.signal_enter(quote, period)
    quote = signal_market_deviation.signal_exit(quote, period)

    # 强力指数
    quote = signal_force_index.signal_enter(quote, period)
    quote = signal_force_index.signal_exit(quote, period)

    # ema 价值回归
    quote = signal_ema_value.signal_enter(quote, period)

    if 'signal_enter' not in quote.columns:
        quote.insert(len(quote.columns), 'signal_enter', numpy.nan)
    if 'signal_exit' not in quote.columns:
        quote.insert(len(quote.columns), 'signal_exit', numpy.nan)

    quote_copy = quote.copy()

    tmp = quote_copy.index.duplicated()
    if tmp.any():
        quote_copy = quote_copy[~quote_copy.index.duplicated(keep='first')]

    # 处理系统外交易信号
    supplemental_signal_path = 'data/trade.csv'
    supplemental_signal = get_supplemental_signal(supplemental_signal_path)
    code = str(quote['code'][0])
    for signal_dict in supplemental_signal:
        if code != signal_dict['code']:
            continue
        date = get_date_period(signal_dict['date'], period, quote.index)
        signal_all_column = 'signal_enter' if signal_dict['command'] == 'B' else 'signal_exit'
        quote_copy.loc[date, signal_all_column] = quote_copy.loc[date, 'close']

    # 合并
    # 处理合并看多信号
    column_list = config.signal_enter_list
    # 'macd_bull_market_deviation',
    # 'force_index_bull_market_deviation']

    for column in column_list:
        quote_copy.loc[:, 'signal_enter'] = quote_copy.apply(
            lambda x: function(x.low, x.signal_enter, eval('x.{}'.format(column)), column), axis=1)

    # 处理合并看空信号
    column_list = config.signal_exit_list
    # 'macd_bear_market_deviation',
    # 'force_index_bear_market_deviation']

    # quote_copy = quote  # .copy()
    for column in column_list:
        quote_copy.loc[:, 'signal_exit'] = quote_copy.apply(
            lambda x: function(x.high, x.signal_exit, eval('x.{}'.format(column)), column), axis=1)

    positive_all = quote_copy['signal_enter'].copy()
    negative_all = quote_copy['signal_exit'].copy()

    # 合并看多
    for i in range(0, len(positive_all)):
        negative_all.iloc[i] = negative_all.iloc[i] if numpy.isnan(positive_all.iloc[i]) else numpy.nan

    positive = positive_all[positive_all > 0]
    negative = negative_all[negative_all > 0]

    # print('signals before merged')
    # print(positive)
    # print(negative)

    # 如果一天同时出现看多/看空信号，按看多处理
    # def func(n: numpy.float64, p: numpy.float64):
    #     if not numpy.isnan(p):
    #         return numpy.nan
    #     return n
    #
    # negative = negative.combine(positive, func=lambda x1, x2: func(x1, x2))

    # if not positive.empty and negative.empty:
    #     j = 1
    #     while j < len(positive):
    #         positive[j] = numpy.nan
    #         j += 1
    #
    # if positive.empty and not negative.empty:
    #     j = 1
    #     while j < len(negative):
    #         negative[j] = numpy.nan
    #         j += 1

    i = 0
    j = 0
    while not positive.empty and not negative.empty and i < len(positive) and j < len(negative):
        next_positive = positive.index[i]
        next_negative = negative.index[j]

        temp_positive = positive[i]
        temp_negative = negative[j]
        temp_positive_index = i
        temp_negative_index = j
        while next_positive <= next_negative and i < len(positive):
            positive[i] = numpy.nan
            i += 1
            if i == len(positive):
                break
            next_positive = positive.index[i]
            # next_negative = negative.index[j]
        positive[temp_positive_index] = temp_positive
        while next_positive > next_negative and j < len(negative):
            negative[j] = numpy.nan
            j += 1
            # next_positive = positive.index[i]
            if j == len(negative):
                break
            next_negative = negative.index[j]
        negative[temp_negative_index] = temp_negative

    i += 1
    j += 1
    while i < len(positive):
        if numpy.isnan(quote_copy.loc[positive.index[i], 'macd_bull_market_deviation'])\
                and numpy.isnan(quote_copy.loc[positive.index[i], 'force_index_bull_market_deviation']):
            positive[i] = numpy.nan
        i += 1
    while j < len(negative):
        if numpy.isnan(quote_copy.loc[negative.index[j], 'macd_bear_market_deviation']) \
                and numpy.isnan(quote_copy.loc[negative.index[j], 'force_index_bear_market_deviation']):
            negative[j] = numpy.nan
        j += 1

    positive = positive[positive > 0]
    negative = negative[negative > 0]

    # print('signals after merged')
    # print(positive)
    # print(negative)

    # positive = positive.mask(positive > 0, quote['low'])
    # negative = negative.mask(negative > 0, quote['high'])

    quote_copy.loc[:, 'signal_enter'] = positive
    quote_copy.loc[:, 'signal_exit'] = negative

    # 背离
    # 背离是重要的信号，不与其他信号合并
    column_list = ['force_index_bull_market_deviation_signal_enter',
                   'macd_bull_market_deviation_signal_enter',
                   'force_index_bear_market_deviation_signal_exit',
                   'macd_bear_market_deviation_signal_exit']
    for column in column_list:
        deviation = quote[column]
        # deviation = deviation[deviation < 0] if 'bull' in column else deviation[deviation < 0]
        if 'bull' in column:
            deviation = deviation[deviation > 0]
            signal_all_column = 'signal_enter'
        else:
            deviation = deviation[deviation > 0]
            signal_all_column = 'signal_exit'
        for i in range(0, len(deviation)):
            # quote_copy[signal_all_column][deviation.index[i]] = quote_copy.loc[deviation.index[i], column]
            quote_copy.loc[deviation.index[i], signal_all_column] = quote_copy.loc[deviation.index[i], column]

    # 止损
    quote_copy = signal_stop_loss.signal_exit(quote_copy)
    return quote_copy


def recognize(price_info_df):
    price_info_df_last = price_info_df[-1:]
    #price = price_info_df_last.get_values()
    r = signal_gd.gold_dead(price_info_df)
    if r == 'B':
        #trade_signal_indicator(None, 0)
        # add to bought
        basic.add_bought(price_info_df_last['code'][0])
        basic.add_trading_detail(price_info_df_last['code'][0], 'B', price_info_df_last['close'][0], 100, 'ZXZQ')
    elif r == 'S':
        #trade_signal_indicator(None, 0)
        # add to cleared
        basic.add_cleared(price_info_df_last['code'][0], price_info_df_last['close'][0], 100, 'ZXZQ')
        basic.add_trading_detail(price_info_df_last['code'][0], 'S', price_info_df_last['close'][0], 100, 'ZXZQ')
    else:
        pass


# 交易日14:45执行, 确定需要交易的股票
def check_signal(code):
    price_rt = quote_www.getChinaStockIndividualPriceInfoWy(code)
    #key_list = ['code', 'trading_date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
    key_list = ['code', 'open', 'high', 'low', 'close', 'volume', 'turnover']

    duration = 60
    price_info_df = quote_db.get_price_info_df_db(code, duration)

    import pandas as pd
    import numpy as np
    dates = pd.date_range(price_rt['trade_date'], periods=1)
    price_info = pd.DataFrame(np.array([[float(price_rt[key]) for key in key_list]]), index=dates, columns=list(key_list))
    price_info_df = price_info_df.append(price_info)

    recognize(price_info_df)
