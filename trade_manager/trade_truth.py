# -*- coding: utf-8 -*-
import datetime
import json
import math
import os
import sys

import numpy
import pandas

from matplotlib import pyplot as plt
from matplotlib.widgets import Cursor

from util import util, mysqlcli


root_dir = util.get_root_dir()
truth_dir = os.path.join(root_dir, 'data', 'truth', 'pt')
truth_dir = os.path.join(root_dir, 'data', 'truth', 'xy')

if not os.path.exists(truth_dir):
    os.makedirs(truth_dir)

suffix = '_PT'
suffix = ''

# Glyph 8722 missing from current font
plt.rcParams['axes.unicode_minus'] = False
plt.tight_layout()
dpi = 300


def merge_trade(trade_current_day_map, trade_in_position_map):
    for code_current_day, trade_current_day in trade_current_day_map.items():
        if code_current_day in trade_in_position_map:
            trade_in_position_map[code_current_day]['current_position'] = trade_current_day['current_position']
            trade_in_position_map[code_current_day]['date'].extend(trade_current_day['date'])
        else:
            trade_in_position_map[code_current_day] = trade_current_day


def load_data():
    trade_data_dir = '/home/shuhm/workspace/inv/stat/ZXZQ/PT'
    years = (2014, 2021)

    trade_data_dir = '/home/shuhm/workspace/inv/stat/ZXZQ'
    years = (2021, 2021)

    data = pandas.DataFrame()
    for year in range(years[0], years[1] + 1, 1):
        # ths 导出, wps 编辑 *.xls - ValueError: File is not a recognized excel file
        # wps 另存为 xlsx   pip install openpyxl
        file = os.path.join(trade_data_dir, '{}{}.xlsx'.format(year, suffix))
        df = pandas.read_excel(file, dtype={'证券代码': str})
        data = data.append(df)
    data = data.reset_index(drop=True)
    date = data.apply(lambda x: datetime.datetime.strptime(
        '{} {}'.format(x['发生日期'], x['成交时间']), '%Y%m%d %H:%M:%S'), axis=1)
    data['证券代码'] = data['证券代码'].apply(str)
    data['证券代码'] = data['证券代码'].apply(lambda x: x.zfill(6))
    data['证券代码'] = data['证券代码'].mask(data['证券代码'] == '000nan', numpy.nan)
    data = data.set_index(date)
    data = data.sort_index()
    return data


def compute_trade(data: pandas.DataFrame):
    path = os.path.join(truth_dir, 'trade_date_{}.json'.format(data.index[-1].strftime('%Y%m%d')))

    if os.path.exists(path):
        with open(path) as f:
            trades = json.load(f)
        return trades

    # data_clear = data[data['股价余额'] == 0]
    code_in_position_list = []
    trade_in_position_map = {}
    code_current_day_list = []
    trade_current_day_map = {}
    trade_all = []
    trade_date = datetime.date(2014, 10, 18)
    trade_date_prev = trade_date
    for i in range(len(data)):
        row = data.iloc[i]
        if row['业务名称'] == '股息入帐':
            continue

        code = row['证券代码']
        if not isinstance(code, str) and numpy.isnan(code):
            continue

        index_date = data.index[i]
        trade_date = index_date.date()
        if trade_date > trade_date_prev:
            trade_date_prev = trade_date
            for trade_current_day in trade_current_day_map.values():
                code_current_day = trade_current_day['code']

                if code_current_day not in code_in_position_list:
                    code_in_position_list.append(code_current_day)

                if code_current_day in trade_in_position_map:
                    trade_in_position_map[code_current_day]['current_position'] = trade_current_day['current_position']
                    trade_in_position_map[code_current_day]['date'].extend(trade_current_day['date'])
                else:
                    trade_in_position_map[code_current_day] = trade_current_day

                if trade_current_day['current_position'] <= 0:
                    code_in_position_list.remove(code_current_day)
                    trade_in_position = trade_in_position_map.pop(code_current_day)
                    trade_in_position['clear'] = True
                    trade_all.append(trade_in_position)

            code_current_day_list = []
            trade_current_day_map = {}

        if code in code_current_day_list:
            trade_current_day_map[code]['date'].append(index_date)
        else:
            code_current_day_list.append(code)
            trade_current_day_map[code] = {'code': code, 'clear': False, 'date': [index_date]}
        trade_current_day_map[code]['current_position'] = int(data.iloc[i]['股份余额'])

    merge_trade(trade_current_day_map, trade_in_position_map)
    trade_all.extend(trade_in_position_map.values())

    with open(path, 'w') as f:
        json.dump(trade_all, f, indent=4, cls=util.DateEncoder)
    return trade_all


def compute_trade_detail_impl(trade, data):
    df = data[data.index.isin(trade['date']) & (data['证券代码'] == trade['code'])]
    # 发生金额 = 成交金额 + 费用(手续费, 印花税, 过户费等)
    df_group = df.groupby(pandas.Grouper(freq='D'))
    df_group_sum = df_group.sum()
    df_buy = df_group_sum[df_group_sum['发生金额'] < 0]

    profit = round(df['发生金额'].sum(), 3)
    cond = df['业务名称'] == '担保品划出'
    if numpy.any(cond):
        df_ = df[cond]
        profit -= sum(df_['成交数量'] * df_['成交价格'])

    cost = abs(round(df_buy['发生金额'].sum(), 3))  # 去除日内做T的买入金额
    cond = df['业务名称'] == '担保品划入'
    if numpy.any(cond):
        df_ = df[cond]
        in_ = sum(df_['成交数量'] * df_['成交价格'])
        cost += in_
        profit -= in_

    profit_percent = profit / cost
    days = len(df)
    detail = {
        'code': trade['code'],
        'count': days,
        'cost': cost,
        'profit': profit,
        'profit_percent': round(profit_percent * 100, 3),
        'profit_percent_per_day_compound_interest': round(100 * (pow(profit_percent + 1, 1 / days) - 1), 3),
        'profit_percent_per_day_simple_interest': round(100 * profit_percent / days, 3),
        'open_position': df.iloc[0]['股份余额'],
        'open_price': df.iloc[0]['成交价格'],
        'max_position': df['股份余额'].max(),
        'trade_price_high': df['成交价格'].max(),
        'trade_price_low': df['成交价格'].min(),
        'close_price': df.iloc[-1]['成交价格'],
        'open_date': df.index[0],
        'close_date': df.index[-1],
        'day': (df.index[-1] - df.index[0]).days + 1
    }
    sql = 'select max(high) high, min(low) low from quote where code = %s and trade_date >= %s and trade_date <= %s'
    with mysqlcli.get_cursor() as cursor:
        # cursor.execute(sql, (trade['code'], df.index[0], df.index[-1]))
        # r = cursor.fetchone()
        r = {}
        if not r or not r['high'] or not r['low']:
            # raise Exception
            r['high'] = detail['trade_price_high']
            r['low'] = detail['trade_price_low']
        detail.update({
            'high': r['high'],
            'low': r['low'],
            'max_earn_percent':  round(100 * (r['high'] / detail['open_price'] - 1), 3),
            'max_loss_percent': round(100 * (1 - r['low'] / detail['open_price']), 3),
        })
    return pandas.DataFrame(detail, index=[detail['close_date']])


def compute_trade_detail(trade_date_list, data):
    path = os.path.join(truth_dir, 'trade_detail_{}.xlsx'.format(data.index[-1].strftime('%Y%m%d')))
    if os.path.exists(path):
        trade_detail = pandas.read_excel(path, index_col=0)
        return trade_detail

    trade_detail = pandas.DataFrame()
    for trade in trade_date_list:
        if trade['current_position'] > 0:
            print('in position - \n{}'.format(trade))
            continue
        df = compute_trade_detail_impl(trade, data)
        trade_detail = trade_detail.append(df)

    trade_detail = trade_detail.sort_index()
    trade_detail.to_excel(path)

    return trade_detail


def stat_trade_by_month(trade_detail):
    path = os.path.join(truth_dir, 'trade_stat_month_{}.xlsx'.format(trade_detail['close_date'][-1].strftime('%Y%m%d')))
    if os.path.exists(path):
        df_trade_stat = pandas.read_excel(path, index_col=0)
        return df_trade_stat

    df_trade_stat = pandas.DataFrame()

    trade_detail_earn = trade_detail[trade_detail['profit'] > 0]
    trade_detail_loss = trade_detail[trade_detail['profit'] <= 0]
    trade_detail_group = trade_detail.groupby(pandas.Grouper(freq='M'))
    trade_detail_group_earn = trade_detail_earn.groupby(pandas.Grouper(freq='M'))
    trade_detail_group_loss = trade_detail_loss.groupby(pandas.Grouper(freq='M'))

    trade_detail_group_count = trade_detail_group.count()
    trade_detail_group_earn_count = trade_detail_group_earn.count()
    trade_detail_group_sum = trade_detail_group.sum()
    trade_detail_group_earn_sum = trade_detail_group_earn.sum()
    trade_detail_group_loss_sum = trade_detail_group_loss.sum()
    trade_detail_group_earn_max = trade_detail_group_earn.max()
    trade_detail_group_loss_max = trade_detail_group_loss.max()
    trade_detail_group_loss_min = trade_detail_group_loss.min()
    trade_detail_group_earn_mean = trade_detail_group_earn.mean()
    trade_detail_group_loss_mean = trade_detail_group_loss.mean()

    # 平均收益/平均亏损百分比
    df_trade_stat['mean_earn_percent'] = trade_detail_group_earn_mean['profit_percent']
    df_trade_stat['mean_loss_percent'] = trade_detail_group_loss_mean['profit_percent']
    # df_trade_stat['mean_earn_percent'] = trade_detail_group_earn_sum['profit'] / trade_detail_group_earn_sum['cost']
    # df_trade_stat['mean_loss_percent'] = trade_detail_group_loss_sum['profit'] / trade_detail_group_loss_sum['cost']

    df_trade_stat['earn_loss_percent'] = df_trade_stat['mean_earn_percent'] / df_trade_stat['mean_loss_percent'].abs()

    df_trade_stat['earn_trade_count'] = trade_detail_group_earn_count['count']
    # 总交
    df_trade_stat['trade_count'] = trade_detail_group_count['count']
    # 成功百分比
    df_trade_stat['earn_count_percent'] = round(
        (100 * df_trade_stat['earn_trade_count'] / df_trade_stat['trade_count']), 3)

    # 最大收益/最大亏损百分比
    df_trade_stat['max_earn_percent'] = trade_detail_group_earn_max['profit_percent']
    df_trade_stat['max_loss_percent'] = trade_detail_group_loss_min['profit_percent']

    # 收益/亏损交易的平均持仓时间
    df_trade_stat['mean_earn_day'] = trade_detail_group_earn_mean['day']
    df_trade_stat['mean_loss_day'] = trade_detail_group_loss_mean['day']

    # 最大收益/亏损
    df_trade_stat['max_earn'] = trade_detail_group_earn_max['profit']
    df_trade_stat['max_loss'] = trade_detail_group_loss_min['profit']

    # 最长持仓时间
    df_trade_stat['max_earn_day'] = trade_detail_group_earn_max['day']
    df_trade_stat['max_loss_day'] = trade_detail_group_loss_max['day']

    # 可能的最大收益/亏损
    df_trade_stat['max_earn_percent_could'] = trade_detail_group_earn_max['max_earn_percent']
    df_trade_stat['max_loss_percent_could'] = trade_detail_group_loss_max['max_loss_percent']

    # 下单次数
    df_trade_stat['order_count'] = trade_detail_group_sum['count']

    # 盈亏
    df_trade_stat['profit'] = trade_detail_group_sum['profit']

    columns = [
        'mean_earn_percent', 'mean_loss_percent', 'earn_count_percent',
        'earn_loss_percent',
        'trade_count',
        'max_earn_percent', 'max_loss_percent',
        'mean_earn_day', 'mean_loss_day',
        'max_earn', 'max_loss',
        'max_earn_day', 'max_loss_day',
        'max_earn_percent_could', 'max_loss_percent_could',
        'order_count',
        'profit'
    ]
    df_trade_stat = df_trade_stat[columns]

    df_trade_stat.to_excel(path)

    return df_trade_stat


def _stat_trade_by_time(trade_stat_month, freq):
    if freq not in 'QY':
        return

    path = os.path.join(truth_dir, 'trade_stat_{}_{}.xlsx'.format(freq, trade_stat_month.index[-1].strftime('%Y%m%d')))
    if os.path.exists(path):
        trade_stat_year = pandas.read_excel(path, index_col=0)
        return trade_stat_year

    trade_stat_year = pandas.DataFrame()
    trade_stat_year_group = trade_stat_month.groupby(pandas.Grouper(freq=freq))
    trade_stat_year_mean = trade_stat_year_group.mean()
    trade_stat_year['mean_earn_percent'] = trade_stat_year_mean['mean_earn_percent']
    trade_stat_year['mean_loss_percent'] = trade_stat_year_mean['mean_loss_percent']
    trade_stat_year['earn_count_percent'] = trade_stat_year_mean['earn_count_percent']
    trade_stat_year['erar_loss_percent'] = round(
        trade_stat_year['mean_earn_percent'] / trade_stat_year['mean_loss_percent'].abs(), 3)
    trade_stat_year['erar_loss_percent_adj'] = 0

    trade_stat_year.to_excel(path)

    return trade_stat_year


def stat_trade_by_quarter(trade_stat_month):
    return _stat_trade_by_time(trade_stat_month, 'Q')  # '3M')


def stat_trade_by_year(trade_stat_month):
    return _stat_trade_by_time(trade_stat_month, 'Y')


def stat_trade_by_stock(trade_detail):
    path = os.path.join(truth_dir, 'trade_stat_stock_{}.xlsx'.format(trade_detail.index[-1].strftime('%Y%m%d')))
    if os.path.exists(path):
        stat = pandas.read_excel(path, index_col=0)
        return stat

    group = trade_detail.groupby(['code'])
    group_sum = group.sum()

    stat = pandas.DataFrame()
    stat['profit'] = group_sum['profit']
    stat['day'] = group_sum['day']
    stat['cost'] = group_sum['cost']
    stat['percent'] = round(stat['profit'] / stat['cost'] * 100, 3)

    stat.to_excel(path)

    return stat


def show_profit_by_count(trade_detail):
    # trade_detail = trade_detail.sort_values(by=['profit_percent'])
    x = numpy.ceil(trade_detail['profit_percent']).astype(int).value_counts(sort=False)
    x = x.sort_index()
    x = 100 * x / x.sum()
    # y = trade_detail.groupby(['profit']).count()
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Cursor
    fig, ax = plt.subplots()
    color = ['seagreen' if profit > 0 else 'tomato' for profit in x.index]
    color = x.mask(x.index < -9, 'purple')
    color = color.mask((x.index >= -9) & (x.index <= -6), 'red')
    color = color.mask((x.index > -6) & (x.index <= 0), 'salmon')  # 'tomato')
    color = color.mask((x.index > 0) & (x.index <= 6), 'lightgreen')
    color = color.mask((x.index > 6) & (x.index <= 10), 'limegreen')
    color = color.mask((x.index > 10), 'darkgreen')
    cursor = Cursor(ax, useblit=True, color='grey', linewidth=1)
    ax.bar(x.index, x.values, color=color, tick_label=x.index)
    ax.plot([-9.5, -9.5], [0, max(x.values)], color='purple')
    ax.plot([-5.5, -5.5], [0, max(x.values)], color='red')
    ax.plot([0.5, 0.5], [0, max(x.values)], color='yellow', linewidth=2)
    plt.xticks(numpy.arange(min(x.index), max(x.index), 2))
    plt.yticks(numpy.arange(0, max(x.values), 5))
    plt.grid(True, linestyle='--', alpha=0.2)  # 网格线

    fig.set_size_inches(10.24, 7.68)
    plt.savefig(os.path.join(truth_dir, '{}.png'.format(sys._getframe().f_code.co_name)), dpi=dpi)
    # plt.show()


def show_profit(trade_detail):
    fig, ax = plt.subplots()
    x = trade_detail.index
    y = trade_detail['profit_percent'].cumsum()
    y = (((trade_detail['profit_percent'] + 100) / 100).cumprod() - 1) * 100
    ax.fill_between(x, y, where=(y > 0), color='seagreen', alpha=0.2)
    ax.fill_between(x, y, where=(y <= 0), color='red', alpha=0.2)

    y2 = trade_detail['profit_percent']
    ax.fill_between(x, y2, where=(y2 > 0), color='green', alpha=0.5)
    ax.fill_between(x, y2, where=(y2 <= 0), color='red', alpha=0.5)
    # ax.plot(x, y2)

    ax.plot([min(x.values), max(x.values)], [0, 0], color='grey', linestyle='-.')
    plt.grid(True, linestyle='-.', alpha=0.2)

    days = trade_detail['day']
    ax2 = ax.twinx()
    ax2.bar(x, days)

    fig.set_size_inches(10.24, 7.68)
    plt.savefig(os.path.join(truth_dir, '{}.png'.format(sys._getframe().f_code.co_name)), dpi=dpi)


def show_profit_per_day(trade_detail):
    fig, ax = plt.subplots()
    x = trade_detail.index
    # y = trade_detail['profit_percent_per_day_compound_interest']
    y = trade_detail['profit_percent_per_day_simple_interest']
    ax.fill_between(x, y, where=(y > 0), color='seagreen')
    ax.fill_between(x, y, where=(y <= 0), color='red')
    ax.plot([min(x.values), max(x.values)], [0, 0], color='grey', linestyle='--')
    plt.grid(True, linestyle='--', alpha=0.2)

    fig.set_size_inches(10.24, 7.68)
    plt.savefig(os.path.join(truth_dir, '{}.png'.format(sys._getframe().f_code.co_name)), dpi=dpi)


def show_stat(trade_stat_month, freq):
    fig, ax = plt.subplots()
    x = trade_stat_month.index
    # y = ((trade_detail['profit_percent'] + 100) / 100).cumprod() * 100
    y1 = trade_stat_month['mean_earn_percent']
    y2 = trade_stat_month['mean_loss_percent']

    adj = 1
    earn_loss_p = y1 > y2.abs()
    earn_loss_m = y1 <= y2.abs()
    y3 = y1[earn_loss_p] / y2[earn_loss_p].abs()
    y4 = y2[earn_loss_m] / y1[earn_loss_m]

    alpha = 1
    ax.fill_between(y3.index, y3 * adj, where=(y3 > 2), color='darkgreen', alpha=alpha)
    ax.fill_between(y3.index, y3 * adj, where=((y3 <= 2) & (y3 >= 1)), color='limegreen', alpha=alpha)

    ax.fill_between(y4.index, y4 * adj, where=(y4 < -2), color='purple', alpha=alpha)
    ax.fill_between(y4.index, y4 * adj, where=((y4 >= 2) & (y4 <= -1)), color='red', alpha=alpha)

    alpha = 0.2
    ax.fill_between(x, y1, color='lightgreen', alpha=alpha)
    ax.fill_between(x, y2, color='salmon', alpha=alpha)

    # ax.plot([min(x.values), max(x.values)], [0, 0], color='grey', linestyle='--')
    plt.grid(True, linestyle='--', alpha=0.2)
    # plt.xticks(x.values)

    fig.set_size_inches(10.24, 7.68)
    plt.savefig(os.path.join(truth_dir, '{}_{}.png'.format(sys._getframe().f_code.co_name, freq)), dpi=dpi)


def trade_truth():
    data = load_data()
    trade_date_list = compute_trade(data)
    trade_detail = compute_trade_detail(trade_date_list, data)
    trade_stat_month = stat_trade_by_month(trade_detail)
    trade_stat_quarter = stat_trade_by_quarter(trade_stat_month)
    trade_stat_year = stat_trade_by_year(trade_stat_month)

    show_profit_by_count(trade_detail)
    show_profit(trade_detail)
    show_stat(trade_stat_month, 'M')
    show_stat(trade_stat_quarter, 'Q')
    show_stat(trade_stat_year, 'Y')

    trade_stat_stock = stat_trade_by_stock(trade_detail)

    return trade_stat_month

    charge = data['手续费'].sum() + data['印花税'].sum() + data['过户费'].sum()
    date1 = datetime.datetime(2014, 10, 18)
    date2 = datetime.datetime(2015, 4, 30)

    # ===
    date1 = datetime.datetime(2015, 10, 30)
    date2 = datetime.datetime(2015, 12, 31)

    date1 = datetime.datetime(2016, 1, 15)
    date2 = datetime.datetime(2016, 1, 19)

    date1 = datetime.datetime(2016, 6, 17)
    date2 = datetime.datetime(2016, 8, 31)

    date1 = datetime.datetime(2016, 11, 15)
    date2 = datetime.datetime(2016, 12, 30)

    # ===
    date1 = datetime.datetime(2017, 1, 3)
    date2 = datetime.datetime(2017, 9, 11)   # 截至当前, 只剩下 万达电影 1100股
    date2 = datetime.datetime(2018, 3, 7)   # 2017/9/11-2018/3/7 没有进行任何交易 # 2018/8/7 分红 550股, 持仓1650股
    date2 = datetime.datetime(2018, 11, 19)   # 清仓了除万达电影以外的所有股票(2018/3/7-), 加仓万达电影2000股, 现持仓3650股

    date2 = datetime.datetime(2019, 1, 31)   # 2018/11/19-2019/1/30, 没有进行任何交易  2019/1/31开始对万达电影做T
    date2 = datetime.datetime(2019, 3, 7)   # 1/31-3/7 只操作了万达电影, 当前持仓 1650, 减持了期间增加的仓位

    date2 = datetime.datetime(2019, 3, 8)   # 开始交易其他股票
    date2 = datetime.datetime(2019, 3, 20)   # 再次清仓其他股票, 加仓万达电影到 7450股
    date2 = datetime.datetime(2019, 3, 22)   # 清仓所有股票

    # ===
    date1 = datetime.datetime(2019, 3, 26)   # 建仓万达电影 2000
    # date2 = datetime.datetime(2019, 6, 3)  # 加仓万达电影 500股至 2500股   4-5两月没有进行任何交易
    date2 = datetime.datetime(2019, 6, 12)   # 开始交易其他股票
    date2 = datetime.datetime(2019, 12, 6)

    date1 = datetime.datetime(2020, 3, 17)
    date2 = datetime.datetime(2021, 11, 5)

    date1 = datetime.datetime(2014, 10, 18)
    date2 = datetime.datetime(2021, 11, 5)

    data1 = data[(data.index >= date1) & (data.index < date2 + datetime.timedelta(days=1))]
    count = data1['成交数量'].sum()
    data_ = data1[data1['业务名称'] == '股息入帐']
    count_ = data_['成交数量'].sum()

    r = data1.groupby('证券代码').sum()  # '成交数量')
    print(data)
