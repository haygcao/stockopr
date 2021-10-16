# -*- encoding: utf-8 -*-

import os
import pathlib
import time
import datetime

import numpy
import pandas

from config import config
from config.signal_config import signal_func
from config.signal_mask import signal_mask_column
from config.signal_pair import signal_pair_column
from indicator import dynamical_system, second_stage, ma, macd, dmi
from pointor import mask
from util import util


def gen_cache_path(code, date=None, period='day'):
    date = date if date else datetime.date.today()
    file = '{}-{}-{}.csv'.format(code, date.strftime('%Y%m%d'), period)
    dir_name = util.get_cache_dir()

    return os.path.join(dir_name, file)


# signal 计算需要支持 multiprocessing
def get_cache_file(code, period):
    cache_file = gen_cache_path(code, period=period)
    # dir_name = os.path.dirname(cache_file)

    fname = pathlib.Path(cache_file)
    if not fname.exists():
        return

    # TODO cache 清理
    # if (datetime.datetime.now() - datetime.datetime.fromtimestamp(fname.stat().st_mtime)).seconds > 3 * 60:
    #     os.remove(cache_file)
    #     return

    return cache_file


def dump(data, file):
    if os.path.exists(file):
        os.remove(file)

    if 'date' not in data.columns:
        data.insert(len(data.columns), 'date', data.index)
    data.to_csv(file)


def load(file):
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


def merge_singal(quote_copy, period, header, direct, column):
    code = quote_copy.code[-1]
    n = 40
    data = quote_copy.iloc[-n:][column]
    write_signal_log(direct, code, period, column, n, data, header)

    for column_mask in signal_mask_column.get(column, []):
        quote_copy = mask.mask_signal(quote_copy, column, column_mask)

    for column_pair in signal_pair_column.get(column, []):
        pass

    price_column = 'low' if 'enter' in direct else 'high'
    quote_copy.loc[:, direct] = quote_copy.apply(
        lambda x: function(x[price_column], x[direct], eval('x.{}'.format(column)), column), axis=1)

    return quote_copy


def clean_signal(quote_copy, negative, positive):
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
        positive[temp_positive_index] = temp_positive
        while next_positive > next_negative and j < len(negative):
            negative[j] = numpy.nan
            date_index = negative.index[j]
            quote_copy.loc[date_index, 'stop_loss'] = numpy.nan
            quote_copy.loc[date_index, 'stop_loss_signal_exit'] = numpy.nan

            j += 1
            if j == len(negative):
                break
            next_negative = negative.index[j]
        negative[temp_negative_index] = temp_negative
    i += 1
    j += 1
    while i < len(positive):
        positive[i] = numpy.nan
        i += 1
    while j < len(negative):
        negative[j] = numpy.nan
        j += 1


def compute_signal(code, period, quote, supplemental_signal_path=None):
    file = get_cache_file(code, period)
    compute = True
    if file:
        quote_bk = load(file)
        compute = quote_bk.empty
        if not compute:
            quote = quote_bk
            quote = quote.assign(signal_enter=numpy.nan)
            quote = quote.assign(signal_exit=numpy.nan)
            quote = quote.assign(mask_signal_exit=numpy.nan)

    if compute:
        # 基础指标 - 均线
        # MA5, MA10, MA20, MA30, MA60, MA120, MA150, MA200, MA12, MA26, MA50, MA100
        quote = ma.compute_ma(quote)

        quote = macd.compute_macd(quote)
        quote = dmi.compute_dmi(quote, period)

        # 基础指标 - 动力系统
        quote = dynamical_system.dynamical_system_dual_period(quote, period=period)

        # 第二阶段
        quote = second_stage.second_stage(quote, period)

        # 计算所有信号, 缓存以加速回测分析
        signal_all_list = config.get_all_signal(period)
        for s in signal_all_list:
            if s not in signal_func:
                continue
            if s == 'stop_loss_signal_exit' or s == 'nday_signal_exit':
                continue
            if 'market_deviation' in s or 'breakout' in s:
                column = s[:s.index('_signal')]
                quote = signal_func[s](quote, period=period, column=column)
                continue
            quote = signal_func[s](quote, period=period)

        # 信号 mask
        quote = mask.compute_enter_mask(quote, period)

        if 'mask_signal_exit' not in quote.columns:
            quote.insert(len(quote.columns), 'mask_signal_exit', numpy.nan)
        if 'signal_enter' not in quote.columns:
            quote.insert(len(quote.columns), 'signal_enter', numpy.nan)
        if 'signal_exit' not in quote.columns:
            quote.insert(len(quote.columns), 'signal_exit', numpy.nan)

        file = gen_cache_path(code, period=period)
        dump(quote, file)

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
    # 处理合并看多信号, 只处理启用的信号
    column_list = config.get_signal_enter_list(period)

    header = True
    for column in column_list:
        quote_copy = merge_singal(quote_copy, period, header, 'signal_enter', column)
        header = False

    # 计算止损数据
    for s in ['stop_loss_signal_exit', 'nday_signal_exit']:
        if s in quote_copy.columns:
            quote_copy = quote_copy.drop([s], axis=1)
        if config.enabled_signal(s, period):
            quote_copy = signal_func[s](quote_copy, period=period)
        else:
            quote_copy.insert(len(quote_copy.columns), s, numpy.nan)

    # ----------

    # 处理合并看空信号
    column_list = config.get_signal_exit_list(period)

    header = True
    # quote_copy = quote  # .copy()
    for column in column_list:
        quote_copy = merge_singal(quote_copy, period, header, 'signal_exit', column)
        header = False

    positive_all = quote_copy['signal_enter'].copy()
    negative_all = quote_copy['signal_exit'].copy()

    # 合并看多
    for i in range(0, len(positive_all)):
        positive_all.iloc[i] = positive_all.iloc[i] if numpy.isnan(negative_all.iloc[i]) else numpy.nan

    positive = positive_all[positive_all > 0]
    negative = negative_all[negative_all > 0]

    clean_signal(quote_copy, negative, positive)

    positive = positive[positive > 0]
    negative = negative[negative > 0]

    quote_copy.loc[:, 'signal_enter'] = positive
    quote_copy.loc[:, 'signal_exit'] = negative

    return quote_copy


def get_osc_key(name):
    if 'volume_ad' in name:
        return 'adosc'
    if 'macd' in name:
        return 'macd_histogram'
    return name
