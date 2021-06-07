# -*- coding: utf-8 -*-
import json
import os
import random
import re
import time
import datetime
import urllib.request

import pandas
import requests
import xlrd

from acquisition import quote_db
from config import url as url_config
from config.config import period_map

import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.Logger.manager.loggerDict





def init():
    if not os.path.exists('data/xls'):
        os.makedirs('data/xls')


def _parsing_dayprice_json(types=None, page=1):
    """
           处理当日行情分页数据，格式为json
     Parameters
     ------
        pageNum:页码
     return
     -------
        DataFrame 当日所有股票交易数据(DataFrame)
    """

    request = urllib.request.Request(url_config.xl_day_price_url % (types, page))
    text = urllib.request.urlopen(request, timeout=10).read()
    if text == 'null':
        return None
    # reg = re.compile(r'\,(.*?)\:')
    # text = reg.sub(r',"\1":', text.decode('gbk'))
    # text = text.replace('"{symbol', '{"symbol')
    # text = text.replace('{symbol', '{"symbol"')
    # jstr = json.dumps(text)

    df = pandas.read_json(text, orient='records', dtype={'code': object})

    return df


def get_today_all():
    """
        一次性获取最近一个日交易日所有股票的交易数据
    return
    -------
      DataFrame
           属性：代码，名称，涨跌幅，现价，开盘价，最高价，最低价，最日收盘价，成交量，换手率，成交额，市盈率，市净率，总市值，流通市值
    """
    PAGE_NUM = [40, 60, 80, 100]
    df = _parsing_dayprice_json('hs_a', 1)
    if df is not None:
        for i in range(2, PAGE_NUM[1]):
            newdf = _parsing_dayprice_json('hs_a', i)
            df = df.append(newdf, ignore_index=True)
    df = df.append(_parsing_dayprice_json('shfxjs', 1),
                   ignore_index=True)

    df.rename(columns={'trade': 'close'}, inplace=True)
    columns = ['code', 'open', 'close', 'high', 'low', 'volume', 'turnover']
    for column in df.columns:
        if column in columns:
            continue
        df = df.drop(column, axis=1)
    #     df = df.ix[df.volume > 0]
    df = df.assign(turnover=0)
    df = df.assign(date=datetime.date.today())
    df.set_index('date', inplace=True)

    return df


def get_realtime_data_sina(code):
    """
    股票名称、今日开盘价、昨日收盘价、当前价格、今日最高价、今日最低价、竞买价、竞卖价、成交股数、成交金额、买1手、买1报价、买2手、买2报价、…、买5报价、…、卖5报价、日期、时间
    var hq_str_sz300502="新易盛,48.000,47.500,48.210,48.400,47.530,48.210,48.220,4009118,192785421.290,3312,48.210,500,48.140,7500,48.130,2000,48.100,400,48.090,23800,48.220,40900,48.250,200,48.260,3900,48.280,400,48.290,2021-05-31,11:30:03,00";
    """
    url = url_config.xl_realtime_quote_url
    symbol = '{}{}'.format('sh' if code.startswith('6') else 'sz', code)
    url = url.format(code=symbol)
    try:
        ret = requests.get(url)
    except Exception as e:
        return

    data = str(ret.content).split('"')[1]
    data_arr = data.split(',')
    open = float(data_arr[1])
    close = float(data_arr[3])
    high = float(data_arr[4])
    low = float(data_arr[5])
    volume = float(data_arr[8])
    columns = ['code', 'open', 'close', 'high', 'low', 'volume', 'turnover']

    strftime = ''
    today = datetime.date.today()
    for nday in range(0, 100):
        strftime = (today - datetime.timedelta(days=nday)).strftime('%Y-%m-%d')
        if strftime in data_arr:
            break
    index = data_arr.index(strftime)
    df = pandas.DataFrame([[code, open, close, high, low, volume, 0]], columns=columns, index=[
        datetime.datetime.strptime('{} {}'.format(data_arr[index], data_arr[index + 1]), '%Y-%m-%d %H:%M:%S')])

    return df


def get_kline_data_sina(code, period='day', count=250):
    """
    新浪返回数据格式:
    [{"day":"2021-05-31 11:00:00","open":"48.310","high":"48.320","low":"47.960","close":"48.290","volume":"305220"}]
    """
    url_temp = url_config.xl_min_quote_url
    symbol = '{}{}'.format('sh' if code.startswith('6') else 'sz', code)
    is_minute_data = period.startswith('m')
    if is_minute_data:
        url = url_temp.format(code=symbol, period=period[1:], count=count)
    else:
        # week 无法复权
        count = count * 5 if period == 'week' else count
        quote = quote_db.get_price_info_df_db(code, count, period_type='D')
        now = datetime.datetime.now()
        if quote.index[-1] == datetime.date.today() or now.hour < 9 or (now.hour == 9 and now.hour < 30):
            return quote
        quote_today = get_realtime_data_sina(code)
        quote = quote.append(quote_today)
        if period == 'week':
            quote = quote_db.get_price_info_df_db_week(quote, period_type=period_map[period]['period'])
        return quote

    try:
        ret = requests.get(url)
    except Exception as e:
        return

    df = pandas.read_json(ret.content, orient='records')
    df = df.assign(code=code)
    df = df.assign(turnover=0)
    df['day'] = pandas.to_datetime(df['day'], format='%Y-%m-%d %H:%M:%S')
    df.set_index('day', inplace=True)
    # df.index = df['day']
    return df


def get_kline_data_tx(code, period='day', count=250):
    """
    {
      "code": 300502,
      "msg": "",
      "data": {
        "sh000300": {
          "m30": [
            [
              "201901021000",
              "3017.07",
              "2977.01",
              "3018.78",
              "2976.94",
              "18749013.00",
              {},
              "0.0000"
            ],
          ]
        }
      }
    }
    """

    symbol = '{}{}'.format('sh' if code.startswith('6') else 'sz', code)
    is_minute_data = period.startswith('m')
    if is_minute_data:
        url = url_config.tx_min_url.format(code=symbol, period=period, count=count)
    else:
        # week 无法复权
        # start_date = datetime.date.today() - datetime.timedelta(count + count//7 * 2 if period == 'day' else count * 7)
        start_date = quote_db.query_date(code, count)
        url = url_config.tx_day_url.format(code=symbol, period=period, start_date=start_date.strftime('%Y-%m-%d'), count=count)

    try:
        print(url)
        ret = requests.get(url)
    except Exception as e:
        return

    import json
    jstr = ret.content.decode()
    jstr = jstr[jstr.index('=')+1:]
    d = json.loads(jstr)

    quote = d['data'][symbol][period if is_minute_data else 'qfq{}'.format(period)]

    d_3m3 = {}

    columns = ['code', 'open', 'close', 'high', 'low', 'volume', 'turnover']
    data = []
    index_list = []
    for row in quote:
        import datetime as dt
        if is_minute_data:
            index_list.append(dt.datetime.strptime(row[0], '%Y%m%d%H%M').strftime('%Y-%m-%d %H:%M'))
            data.append(
                [code, float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[7])])
        else:
            index_list.append(row[0])
            data.append(
                [code, float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), 0])

    d_3m3['index'] = index_list
    d_3m3['columns'] = columns
    d_3m3['data'] = data

    df = pandas.read_json(json.dumps(d_3m3), orient='split')
    return df


def get_kline_data(code, period='day', count=250):
    func_list = [get_kline_data_tx, get_kline_data_sina]
    func_list = [get_kline_data_tx]
    index = random.randint(0, len(func_list) - 1)
    quote = func_list[index](code, period, count)
    if quote is None:
        quote = get_kline_data_sina(code, period, count)
    return quote


def _download_quote_xls():
    _dataUrl = url_config.tx_latest_day_quote_url
    trade_date = str(datetime.date.today())
    _xls = 'data/xls/{0}.xls'.format(trade_date)

    if os.path.exists(_xls):
        return _xls

    try_ = 5
    while try_ > 0:
        try:
            urllib.request.urlretrieve(_dataUrl, _xls)
            break
        except Exception as e:
            try_ -= 1
            if try_ == 0:
                # TODO
                raise e
            time.sleep(1)
            continue

    return _xls


def download_quote_xls():
    init()
    _xls = _download_quote_xls()
    if not _xls:
        return

    # if is_quote_of_today(_xls):
    #     os.remove(_xls)
    #     print('not today, xls removed')
    #     return

    return _xls


def get_trade_date(xls):
    data = xlrd.open_workbook(xls)  # 注意这里的workbook首字母是小写
    sheet = data.sheet_names()[0]
    table = data.sheet_by_name(sheet)
    # ['数据更新时间', '12-25 15:15:12', '', '', '', '', '', '', '', '', '', '', '']
    update_day = table.row_values(0)[1].split()[0]

    return get_trade_date_from_str(update_day)


def get_trade_date_from_str(date_str):
    year = datetime.date.today().year
    trade_date = datetime.datetime.strptime('{}-{}'.format(year, date_str.split(' ')[0]), '%Y-%m-%d')

    return trade_date


def is_quote_of_today(_xls):
    update_day = get_trade_date(_xls)
    today = datetime.date.today()
    if today <= update_day:
        return False
    return True


# return: [(code, name),]
def get_stock_list_from_quote_xls(_xls):
    stock_list = []

    # 打开excel
    data = xlrd.open_workbook(_xls)  # 注意这里的workbook首字母是小写

    # 查看文件中包含sheet的名称
    sheets = data.sheet_names()
    sheet = sheets[0]

    # 得到第一个工作表，或者通过索引顺序 或 工作表名称
    table = data.sheets()[0]
    table = data.sheet_by_index(0)
    table = data.sheet_by_name(sheet)
    # 获取行数和列数
    # nrows = table.nrows
    # ncols = table.ncols
    # 获取整行和整列的值（数组）
    i = 0
    table.row_values(i)
    table.col_values(i)
    # 循环行,得到索引的列表
    B = False
    for rownum in range(table.nrows):
        row = table.row_values(rownum)
        if not B and not row[i].startswith('s'):
            continue

        code = row[0][2:]
        name = row[1]
        # ex = 1 if code >= 600000 else 2

        # stock_list.append((code, name, ex))
        stock_list.append((code, name))

        continue

        break
    # 单元格
    # cell_A1 = table.cell(0,0).value
    # 分别使用行列索引
    # cell_A1 = table.row(0)[0].value
    # cell_A2 = table.col(1)[0].value

    return stock_list


def check_format(row):
    # if len(row) != 13:
    #    return False
    if row != ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '买入', '卖出', '成交量', '成交额', '今开', '昨收', '最高', '最低']:
        return False
    return True


def get_stock_list(_xls=None):
    if not _xls:
        _xls = download_quote_xls()
    return get_stock_list_from_quote_xls(_xls)


def get_quote(xlsfile, dt=None):
    # 打开excel
    data = xlrd.open_workbook(xlsfile)  # 注意这里的workbook首字母是小写

    # 查看文件中包含sheet的名称
    sheets = data.sheet_names()
    sheet = sheets[0]

    # 得到第一个工作表，或者通过索引顺序 或 工作表名称
    table = data.sheets()[0]
    table = data.sheet_by_index(0)
    table = data.sheet_by_name(sheet)

    if not check_format(table.row_values(1)):
        raise Exception('xls format changed...')

    # 获取行数和列数
    # nrows = table.nrows
    # ncols = table.ncols
    # 获取整行和整列的值（数组）
    # 循环行,得到索引的列表
    trade_date = None
    # ['数据更新时间', '12-25 15:15:12', '', '', '', '', '', '', '', '', '', '', '']
    update_day = table.row_values(0)[1].split()[0]
    # if dt == None:
    #     dt = str(datetime.date.today())
    # if dt.find(update_day) < 0:
    #     print(dt, update_day, 'not today\'s quote')
    #     #os.remove(xlsfile)
    #     return

    trade_date = get_trade_date_from_str(update_day)
    val_many = []
    for rownum in range(table.nrows):
        row = table.row_values(rownum)
        if not row[0].startswith('s'):
            continue

        print(row[0])

        key_xls = ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '买入', '卖出', '成交量', '成交额', '今开', '昨收', '最高', '最低', '日期']
        key_dict = {'代码': 'code', '名称': '', '最新价': 'close', '涨跌幅': '', '涨跌额': '',
                    '买入': '', '卖出': '', '成交量': 'volume', '成交额': 'turnover',
                    '今开': 'open', '昨收': '', '最高': 'high', '最低': 'low',
                    '日期': 'trade_date'}
        row.append(trade_date)
        row[0] = row[0][2:]

        # AttributeError: 'dict' object has no attribute 'iteritems'
        key_list = ['code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        indice = [0, 13, 9, 11, 12, 2, 7, 8]  # subscript
        fmt_list = ['%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s']
        val_list = []
        volume = row[7]
        if int(volume) <= 0:
            # print(row[0], '停牌')
            continue
        row[7] *= 100

        for i, idx in enumerate(indice):
            val_list.append(row[idx])
            if key_list[i] != key_dict[key_xls[idx]]:
                exit(0)
            # print('{0}\t{1}\t{2}'.format(key_list[i], key_xls[idx], row[idx]))

        val = tuple(val_list)
        val_many.append(val)

    # print(sql_str % tuple(val_list))

    return val_many


if __name__ == '__main__':
    _download_quote_xls()
