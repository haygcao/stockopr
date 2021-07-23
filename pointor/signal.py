#-*- encoding: utf-8 -*-
import os
import pathlib
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
from indicator import dynamical_system, second_stage
from pointor import signal_dynamical_system, signal_channel, signal_market_deviation, signal_force_index, \
    signal_stop_loss, signal_ema_value, signal_resistance_support, signal_volume_ad
from util import util
from util.log import logger


signal_func = {
    "dynamical_system_signal_enter": signal_dynamical_system.signal_enter,
    "channel_signal_enter": signal_channel.signal_enter,
    "force_index_signal_enter": signal_force_index.signal_enter,
    "ema_value_signal_enter": signal_ema_value.signal_enter,
    "volume_ad_signal_enter": signal_volume_ad.signal_enter,
    "resistance_support_signal_enter": signal_resistance_support.signal_enter,
    "force_index_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "volume_ad_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "skdj_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "rsi_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "macd_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,

    "dynamical_system_signal_exit": signal_dynamical_system.signal_exit,
    "channel_signal_exit": signal_channel.signal_exit,
    "force_index_signal_exit": signal_force_index.signal_exit,
    "volume_ad_signal_exit": signal_volume_ad.signal_exit,
    "resistance_support_signal_exit": signal_resistance_support.signal_exit,
    "force_index_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "volume_ad_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "skdj_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "rsi_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "macd_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "stop_loss_signal_exit": signal_stop_loss.signal_exit
  }


def gen_cache_path(code, date, period):
    file = '{}-{}-{}.csv'.format(code, date.strftime('%Y%m%d'), period)
    root_dir = util.get_root_dir()
    dir_name = os.path.join(root_dir, 'data', 'cache')  # , file)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    return os.path.join(dir_name, file)


def get_cache_file(code, period):
    cache_file = gen_cache_path(code, datetime.date.today(), period)
    dir_name = os.path.dirname(cache_file)
    file_list = os.listdir(dir_name)
    for file in file_list:
        file = os.path.join(dir_name, file)
        fname = pathlib.Path(file)
        if (datetime.datetime.now() - datetime.datetime.fromtimestamp(fname.stat().st_mtime)).seconds > 3 * 60:
            os.remove(file)

    if not os.path.exists(cache_file):
        return

    # fname = pathlib.Path(file)
    # if not fname.exists():
    #     return

    return cache_file


def dump(data, period):
    file = gen_cache_path(data.code[-1], datetime.date.today(), period)
    if os.path.exists(file):
        os.remove(file)

    if 'date' not in data.columns:
        data.insert(len(data.columns), 'date', data.index)
    data.to_csv(file)


def load(code, period):
    file = gen_cache_path(code, datetime.date.today(), period)
    data = pandas.read_csv(file)

    data['date'] = pandas.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S')
    # 将日期列作为行索引
    data.set_index(['date'], inplace=True)
    data.sort_index(ascending=True, inplace=True)

    return data


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


def function_tune_enter_signal_by_stop_loss(signal_enter, high, low, close, stop_loss):
    if numpy.isnan(signal_enter):
        return signal_enter

    if (close - stop_loss) / close < 0.02 or (low < stop_loss):
        return numpy.nan

    return signal_enter


# supplemental_signal: [(code, date, 'B/S', price), (code, date, 'B/S', price), ...]
def get_supplemental_signal(supplemental_signal_path, period):
    import csv
    with open(supplemental_signal_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        signal_list = []
        for row in reader:
            if row['period'] != period:
                continue
            row['date'] = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M')
            if row['code'].startswith('#'):
                continue
            signal_list.append(row)

    return signal_list


def write_supplemental_signal(supplemental_signal_path, code, date, command, period, price):
    import csv
    with open(supplemental_signal_path, 'a', newline='') as csvfile:
        fieldnames = ['code', 'name', 'date', 'command', 'period', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # writer.writeheader()
        writer.writerow({'code': code,
                         'date': date.strftime('%Y-%m-%d %H:%M'),
                         'command': command,
                         'period': period,
                         'price': price
                         })


def write_signal_log(direct, code, period, column, n, data, header=False):
    with open(config.signal_log_path, 'a') as f:
        if header:
            f.write('\n\n{0}   {1} {2:12s} {3:10s} {0}\n'.format(
                ('*' * 10), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), direct, '[{}][{}]'.format(n, period)))

        if not numpy.any(data > 0):
            return

        msg = '[{}][{}]\n{}'.format(code, column, data[data > 0])
        f.write(msg)


def get_date_period(date, period, quote_date_index):
    ret = quote_date_index[quote_date_index >= date]
    return quote_date_index[-1] if ret.empty else ret[0]


def compute_signal(code, period, quote, supplemental_signal_path=None):
    file = get_cache_file(code, period)
    if file:
        data = load(code, period)
        return data

    # 基础指标 - 动力系统
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

    # 第二阶段
    quote = second_stage.compute_second_stage(quote, period)

    # enter signal
    signal_list = config.get_signal_list(period)
    for s in signal_list:
        if s not in signal_func:
            continue
        if s == 'stop_loss_signal_exit':
            continue
        if 'market_deviation' in s:
            column = s[:s.index('_signal')]
            quote = signal_func[s](quote, period=period, column=column)
            continue
        quote = signal_func[s](quote, period=period)

    if 'signal_enter' not in quote.columns:
        quote.insert(len(quote.columns), 'signal_enter', numpy.nan)
    if 'signal_exit' not in quote.columns:
        quote.insert(len(quote.columns), 'signal_exit', numpy.nan)

    # 处理系统外交易信号
    supplemental_signal_path = config.supplemental_signal_path
    supplemental_signal = get_supplemental_signal(supplemental_signal_path, period)
    code = str(quote['code'][0])
    for signal_dict in supplemental_signal:
        if code != signal_dict['code']:
            continue
        date = get_date_period(signal_dict['date'], period, quote.index)
        signal_all_column = 'signal_enter' if signal_dict['command'] == 'B' else 'signal_exit'
        quote.loc[date, signal_all_column] = quote.loc[date, 'close']

    quote_copy = quote.copy()

    tmp = quote_copy.index.duplicated()
    if tmp.any():
        quote_copy = quote_copy[~quote_copy.index.duplicated(keep='first')]

    # 合并
    # 处理合并看多信号
    column_list = config.get_signal_enter_list(period)
    # 'macd_bull_market_deviation',
    # 'force_index_bull_market_deviation']

    header = True
    for column in column_list:
        n = 40
        data = quote_copy.iloc[-n:][column]
        direct = 'signal_enter'
        write_signal_log(direct, code, period, column, n, data, header)
        header = False

        quote_copy.loc[:, direct] = quote_copy.apply(
            lambda x: function(x.low, x.signal_enter, eval('x.{}'.format(column)), column), axis=1)

    # 计算止损数据
    if 'stop_loss_signal_exit' in quote_copy.columns:
        quote_copy = quote_copy.drop(['stop_loss_signal_exit'], axis=1)
    if 'stop_loss_signal_exit' in signal_list:
        quote_copy = signal_stop_loss.signal_exit(quote_copy)
    else:
        quote_copy.insert(len(quote_copy.columns), 'stop_loss_signal_exit', numpy.nan)

    # 处理合并看空信号
    column_list = config.get_signal_exit_list(period)
    # 'macd_bear_market_deviation',
    # 'force_index_bear_market_deviation']

    header = True
    # quote_copy = quote  # .copy()
    for column in column_list:
        n = 40
        data = quote_copy.iloc[-n:][column]
        direct = 'signal_exit'
        write_signal_log(direct, code, period, column, n, data, header)
        header = False

        quote_copy.loc[:, 'signal_exit'] = quote_copy.apply(
            lambda x: function(x.high, x.signal_exit, eval('x.{}'.format(column)), column), axis=1)

    # 消除价格与 stop loss 相差不大的 enter 信号
    # quote_copy.loc[:, 'signal_enter'] = quote_copy.apply(
    #     lambda x: function_tune_enter_signal_by_stop_loss(x.signal_enter, x.high, x.low, x.close, x.stop_loss_full),
    #     axis=1)

    positive_all = quote_copy['signal_enter'].copy()
    negative_all = quote_copy['signal_exit'].copy()

    # 合并看多
    for i in range(0, len(positive_all)):
        positive_all.iloc[i] = positive_all.iloc[i] if numpy.isnan(negative_all.iloc[i]) else numpy.nan

    positive = positive_all[positive_all > 0]
    negative = negative_all[negative_all > 0]

    # print('signals before merged')
    # print(positive[-50:])
    # # print(quote_copy[quote_copy.index.isin(positive.index)]['resistance_support_signal_enter'])
    # print(negative[-50:])

    # print('signals after merged')

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
            date_index = negative.index[j]
            quote_copy.loc[date_index, 'stop_loss'] = numpy.nan
            quote_copy.loc[date_index, 'stop_loss_signal_exit'] = numpy.nan

            j += 1
            # next_positive = positive.index[i]
            if j == len(negative):
                break
            next_negative = negative.index[j]
        negative[temp_negative_index] = temp_negative

    deviation_signals = config.get_signal_enter_deviation(period)
    i += 1
    j += 1
    while i < len(positive):
        b = True
        for deviation in deviation_signals:
            column = deviation[:deviation.index('_signal')]
            b &= numpy.isnan(quote_copy.loc[positive.index[i], column])
        if b:
            positive[i] = numpy.nan
        i += 1

    deviation_signals = config.get_signal_exit_deviation(period)
    while j < len(negative):
        b = True
        for deviation in deviation_signals:
            column = deviation[:deviation.index('_signal')]
            b &= numpy.isnan(quote_copy.loc[negative.index[j], column])
        if b:
            negative[j] = numpy.nan
        j += 1

    positive = positive[positive > 0]
    negative = negative[negative > 0]

    # print('signals after merged')
    # print(positive[-50:])
    # # print(quote_copy[quote_copy.index.isin(positive.index)]['resistance_support_signal_enter'])
    # print(negative[-50:])

    # positive = positive.mask(positive > 0, quote['low'])
    # negative = negative.mask(negative > 0, quote['high'])

    quote_copy.loc[:, 'signal_enter'] = positive
    quote_copy.loc[:, 'signal_exit'] = negative

    # 背离
    # 背离是重要的信号，不与其他信号合并
    # column_list = ['force_index_bull_market_deviation_signal_enter',
    #                'macd_bull_market_deviation_signal_enter',
    #                'force_index_bear_market_deviation_signal_exit',
    #                'macd_bear_market_deviation_signal_exit']
    # for column in column_list:
    #     deviation = quote[column]
    #     # deviation = deviation[deviation < 0] if 'bull' in column else deviation[deviation < 0]
    #     if 'bull' in column:
    #         deviation = deviation[deviation > 0]
    #         signal_all_column = 'signal_enter'
    #     else:
    #         deviation = deviation[deviation > 0]
    #         signal_all_column = 'signal_exit'
    #     for i in range(0, len(deviation)):
    #         # quote_copy[signal_all_column][deviation.index[i]] = quote_copy.loc[deviation.index[i], column]
    #         quote_copy.loc[deviation.index[i], signal_all_column] = quote_copy.loc[deviation.index[i], column]

    # # 重新计算止损
    # if 'stop_loss_signal_exit' in quote_copy.columns:
    #     quote_copy = quote_copy.drop(['stop_loss_signal_exit'], axis=1)
    # quote_copy = signal_stop_loss.signal_exit(quote_copy)

    dump(quote_copy, period)

    return quote_copy


def recognize(price_info_df):
    price_info_df_last = price_info_df[-1:]
    # price = price_info_df_last.get_values()
    r = signal_gd.gold_dead(price_info_df)
    if r == 'B':
        # trade_signal_indicator(None, 0)
        # add to bought
        basic.add_bought(price_info_df_last['code'][0])
        basic.add_trading_detail(price_info_df_last['code'][0], 'B', price_info_df_last['close'][0], 100, 'ZXZQ')
    elif r == 'S':
        # trade_signal_indicator(None, 0)
        # add to cleared
        basic.add_cleared(price_info_df_last['code'][0], price_info_df_last['close'][0], 100, 'ZXZQ')
        basic.add_trading_detail(price_info_df_last['code'][0], 'S', price_info_df_last['close'][0], 100, 'ZXZQ')
    else:
        pass


# 交易日14:45执行, 确定需要交易的股票
def check_signal(code):
    price_rt = quote_www.getChinaStockIndividualPriceInfoWy(code)
    # key_list = ['code', 'trading_date', 'open', 'high', 'low', 'close', 'volume', 'amount']
    key_list = ['code', 'open', 'high', 'low', 'close', 'volume', 'amount']

    duration = 60
    price_info_df = quote_db.get_price_info_df_db(code, duration)

    import pandas as pd
    import numpy as np
    dates = pd.date_range(price_rt['trade_date'], periods=1)
    price_info = pd.DataFrame(np.array([[float(price_rt[key]) for key in key_list]]), index=dates, columns=list(key_list))
    price_info_df = price_info_df.append(price_info)

    recognize(price_info_df)


def get_osc_key(name):
    if 'volume_ad' in name:
        return 'adosc'
    if 'macd' in name:
        return 'macd_histogram'
    return name
