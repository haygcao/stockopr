# -*- coding: utf-8 -*-

import datetime

import pandas as pd

import util.mysqlcli as mysqlcli
import config.config as config
from data_structure import trade_data


def query_quota_position(code):
    with mysqlcli.get_cursor() as c:
        # sql = 'SELECT DISTINCT code FROM {0}'.format(config.sql_tab_quote)
        sql = "SELECT `position` FROM {0} where code = '{1}'  order by date desc limit 1".format(config.sql_tab_trade_order, code)
        c.execute(sql)
        postion = c.fetchone()

        return int(postion['position'])


def query_trade_order_map(code=None):
    with mysqlcli.get_cursor() as c:
        sql = "SELECT code, position, open_price, stop_loss, stop_profit FROM {0} where status = 'ING'".format(config.sql_tab_trade_order)
        if code:
            sql += " and code = {}".format(code)

        c.execute(sql)
        ret = c.fetchall()
        order_map = {}
        for row in ret:
            trade_order = trade_data.TradeOrder(row['code'], int(row['position']), float(row['open_price']), float(row['stop_loss']), float(row['stop_profit']))
            order_map.update({code: trade_order})

        return order_map


def query_total_risk_amount():
    total_loss = 0
    with mysqlcli.get_cursor() as c:
        sql = "SELECT code, (position * (open_price - stop_loss)) as loss FROM {0} where status = 'ING'".format(config.sql_tab_trade_order)

        c.execute(sql)
        ret = c.fetchall()
        for row in ret:
            code, loss = row['code'], float(row['loss'])
            total_loss += loss

        return total_loss


# quote
# insert ignore into
def insert_into_quote(val_list):
    key_list = ['code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
    fmt_list = ['%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s']
    key = ', '.join(key_list)
    fmt = ', '.join(fmt_list)
    sql_str = 'insert ignore into quote ({0}) values ({1})'.format(key, fmt)
    # print(sql_str % tuple(val_list))

    with mysqlcli.get_cursor() as c:
        try:
            c.executemany(sql_str, val_list)
        except Exception as e:
            print(e)


def get_price_info_db(code, trade_date = None):
    with mysqlcli.get_cursor() as c:
        key_list = ['code', 'name', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        key_list = ['name', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        table = [config.sql_tab_basic_info, config.sql_tab_quote]
        where = 'quote.code = {0} and trade_date = "{1}"'.format(code, trade_date)
        where = 'quote.code = {0} and trade_date = "{1}" and quote.code = basic_info.code'.format(code, trade_date)
        where = 'quote.code = basic_info.code'.format(code, trade_date)
        on = 'quote.code = basic_info.code'.format(code, trade_date)
        if not trade_date:
            where = 'basic_info.code = "{0}" order by trade_date desc limit 1'.format(code)
        else:
            if type(trade_date) == int:
                where = 'basic_info.code = "{0}" order by trade_date desc limit {1},1'.format(code, trade_date)
            else:
                where = 'basic_info.code = {0} and trade_date = "{1}"'.format(code, trade_date)
        sql = 'SELECT {0} FROM {1} inner join {4} on {2} WHERE {5}'.format(', '.join(key_list), table[1], on, 'name', table[0], where)
        #print(sql)
        c.execute(sql)
        r = c.fetchone()
        if not r:
            return None

        r.update({'code':code})
        #print(r['trade_date'], r['close'])

        return r


def get_price_info_list_db(code, trade_date = 1):
    with mysqlcli.get_cursor() as c:
        key_list = ['code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        table = [config.sql_tab_basic_info, config.sql_tab_quote]
        on = 'quote.code = basic_info.code'.format(code, trade_date)
        where = 'quote.code = "{0}" order by trade_date desc limit {1}'.format(code, trade_date)
        sql = 'SELECT {0} FROM {1} WHERE {5}'.format(', '.join(key_list), table[1], on, 'name', table[0], where)
        #print(sql)
        c.execute(sql)
        r = c.fetchall()
        if not r:
            return None
        r = sorted(r, key=lambda x: x['trade_date']) #, reverse=True)

        return r

'''
http://legacy.python.org/dev/peps/pep-0249/
The read_sql docs say this params argument can be a list, tuple or dict (see docs).
To pass the values in the sql query, there are different syntaxes possible: ?, :1, :name, %s, %(name)s

with argument:
df = psql.read_sql(('select "Timestamp","Value" from "MyTable" '
                     'where "Timestamp" BETWEEN %s AND %s'),
                   db,params=[datetime(2014,6,24,16,0),datetime(2014,6,24,17,0)],
                   index_col=['Timestamp'])
df = psql.read_sql(('select "Timestamp","Value" from "MyTable" '
                     'where "Timestamp" BETWEEN %(dstart)s AND %(dfinish)s'),
                   db,params={"dstart":datetime(2014,6,24,16,0),"dfinish":datetime(2014,6,24,17,0)},
                   index_col=['Timestamp'])
'''


def get_price_info_df_db(code, days=0, end_date=None, period_type='D', conn=None, from_file=None):
    if days == 0:
        days = 1 if period_type == 'D' else 500

    if from_file:
        df = get_price_info_df_file_day(code, days, end_date, from_file)
    else:
        df = get_price_info_df_db_day(code, days, end_date, conn)
    if period_type == 'D':
        return df

    return get_price_info_df_db_week(df)


def get_price_info_df_file_day(code, days, end_date, path):
    labels = ['close', 'high', 'low', 'open', 'volume', 'turnover']
    # df = pd.read_csv(path, nrows=days, index_col='日期', usecols=['开盘价', '最高价', '最低价', '收盘价', '成交量', '成交金额'],
    #                  names=None)
    # df = pd.read_csv(path, nrows=days, index_col='日期', usecols=['开盘价', '最高价', '最低价', '收盘价', '成交量', '成交金额'])
    df = pd.read_csv(path, nrows=days, index_col=0, usecols=[0, 6, 3, 4, 5, 11, 12], encoding='gbk')
    df.columns = labels

    df = df.sort_index()
    df = df.assign(code=code)

    return df


def get_price_info_df_db_day(code, days=1, end_date=None, conn=None):
    end_date = end_date if end_date and len(end_date) > 0 else datetime.date.today()

    if conn == None:
        _conn = mysqlcli.get_connection()
    else:
        _conn = conn

    #if type(code) == list:
    #    _code = '"' + '","'.join(code)
    #    _code = _code[:-2]
    #else:
    #    _code = code
    _code = code
    key_list = ['code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'turnover', 'lb', 'wb', 'zf']
    table = [config.sql_tab_basic_info, config.sql_tab_quote]
    on = '{0}.code = basic_info.code'.format(table[1])
    where = '{3}.code = "{0}" and trade_date <= "{1}" order by trade_date desc limit {2}'.format(_code, end_date, days, table[1])
    sql = 'SELECT {0} FROM {1} WHERE {5}'.format(', '.join(key_list), table[1], on, 'name', table[0], where)

    df = pd.read_sql(sql, con=_conn, index_col=['trade_date'])
    # df = pd.read_sql(sql, con=conn)
    # df.index.names = ['date']
    # df = pd.read_sql(sql, con=conn)

    if conn == None:
        _conn.close()

    # df = df.reset_index('trade_date') # no
    # df = df.reindex(df['trade_date']) # ok, but no value, because new index not eq old index
    # print(df.index.name)
    # print(df)
    # exit(0)

    # df = df.set_index('trade_date')
    # df.set_index('trade_date', inplace=True)
    #  sort() sort_index() sort_values()
    # df.sort(ascending=True, inplace=True) # FutureWarning: sort(....) is deprecated, use sort_index(.....)
    df.sort_index(ascending=True, inplace=True)

    return df


def get_price_info_df_db_week(df, period_type='W'):
    # W M Q 12D 30min
    df.index = pd.to_datetime(df.index)
    # print(p.columns)

    # p.set_index('trade_date', inplace=True)
    period_data = df.resample(period_type).last()
    # period_data['change'] = p['change'].resample(period_type, how=lambda x:(x+1.0).prod() - 1.0, axis=0);
    period_data['open'] = df['open'].resample(period_type).first()
    period_data['high'] = df['high'].resample(period_type).max()
    period_data['low'] = df['low'].resample(period_type).min()
    period_data['close'] = df['close'].resample(period_type).last()
    period_data['volume'] = df['volume'].resample(period_type).sum()
    period_data['turnover'] = df['turnover'].resample(period_type).sum()

    # period_data.set_index('trade_date', inplace=True)
    period_data = period_data[period_data['code'].notnull()]

    return period_data


# w: avg, max, min...
def get_price_stat_db(code, pv, day, w):
    with mysqlcli.get_cursor() as c:
        if pv == 'p':
            pv = 'close'
        else:
            pv = 'volume'
        sql = 'select {4}({3}) as avg{3} from (select close from {0} where code = "{1}" order by trade_date desc limit {3}) as tmp'.format(config.sql_tab_quote, code, pv, day, w)
        c.execute(sql)
        r = c.fetchone()
        return list(r.values())[0]


def get_latest_trade_date():
    with mysqlcli.get_cursor() as c:
        sql = 'select max(trade_date) from quote'
        c.execute(sql)
        r = c.fetchone()
        return list(r.values())[0]
