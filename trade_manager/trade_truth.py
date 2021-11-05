# -*- coding: utf-8 -*-
import datetime
import os

import pandas


def trade_truth():
    trade_data_dir = '/home/shuhm/workspace/inv/stat/ZXZQ/PT'
    years = (2014, 2021)

    data = pandas.DataFrame()
    for year in range(years[0], years[1] + 1, 1):
        # ths 导出, wps 编辑 *.xls - ValueError: File is not a recognized excel file
        # wps 另存为 xlsx   pip install openpyxl
        file = os.path.join(trade_data_dir, '{}_PT.xlsx'.format(year))
        df = pandas.read_excel(file)
        data = data.append(df)
    data = data.reset_index(drop=True)
    date = data.apply(lambda x: datetime.datetime.strptime(
        '{} {}'.format(x['发生日期'], x['成交时间']), '%Y%m%d %H:%M:%S'), axis=1)
    data = data.set_index(date)

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
