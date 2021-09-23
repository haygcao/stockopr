# -*- coding: utf-8 -*-
"""
1 基金持有的小市值股票
"""
import datetime

import pandas

from config import config
from util import mysqlcli, dt


def query_one_stock_lite():
    fund_date = '2021-06-30'
    code = '600519'
    sql = "select fund_code from fund_stock where fund_date = %s and code = %s"

    val = (fund_date, code)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['fund_code'])
    return df


def query_stock():
    trade_date = dt.get_pre_trade_date()
    fund_date = '2021-06-30'
    scale = 0  # 10
    nmc = config.SELECTOR_FUND_STOCK_NMC_MAX  # 50
    code = '600519'
    sql = "select fund_code, fs.code, bi.name, q.nmc nmc, q.close " \
          "from fund_basic fb, fund_stock fs, basic_info bi, quote q " \
          "where q.code = bi.code and fb.code = fs.fund_code and bi.code = fs.code and fb.`date` = fund_date " \
          "and q.trade_date = %s and fund_date = %s and fb.`scale` > %s and nmc < %s and q.code = %s" \

    val = (trade_date, fund_date, scale, nmc * 10000, code)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['fund_code'])
    return df


def query_stocks(fund_date):
    sort_by = 'fmvp'
    trade_date = dt.get_pre_trade_date()
    scale = 10
    nmc = config.SELECTOR_FUND_STOCK_NMC_MAX
    # nmc = 50
    sql = "select fs.code, bi.name, count(fs.code) fc, sum(fs.market_value) fmv, q.nmc nmc, q.close " \
          "from fund_basic fb, fund_stock fs, basic_info bi, quote q " \
          "where q.code = bi.code and fb.code = fs.fund_code and bi.code = fs.code and fb.`date` = fund_date " \
          "and q.trade_date = %s and fund_date = %s and fb.`scale` > %s and nmc < %s " \
          "group by fs.code" \
          # "order by q.nmc"
    val = (trade_date, fund_date, scale, nmc * 10000)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['code'])
        df['fmvp'] = 100 * round(df['fmv'] / df['nmc'], 3)
        df = df.sort_values(by=[sort_by], ascending=False)
    return df


def query_stocks_fund_market_value_diff(fund_date_prev, fund_date_next):
    df_prev = query_stocks(fund_date_prev)
    df_next = query_stocks(fund_date_next)
    df_prev.sort_index(inplace=True)
    df_next.sort_index(inplace=True)

    fmvp = df_next['fmvp'] - df_prev['fmvp']
    mask1 = fmvp.isna()
    mask2 = df_next['fmvp'] >= 0
    fmvp = fmvp.mask(mask1 & mask2, df_next['fmvp'])

    mask1 = fmvp.isna()
    mask2 = df_prev['fmvp'] >= 0
    fmvp = fmvp.mask(mask1 & mask2, -df_prev['fmvp'])

    fmvp = fmvp.sort_values(ascending=False)

    df = pandas.DataFrame(fmvp, index=fmvp.index)
    df = df.assign(name=df_next['name'])
    df.name = df.name.mask(df.name.isna(), df_prev.name)
    return df


def query_fund():
    trade_date = dt.get_pre_trade_date()
    fund_date = '2021-06-30'
    fund_code = '001283'
    sql = "select fund_code, fb.scale, fs.code, bi.name, q.nmc nmc, q.close, fs.market_value " \
          "from fund_basic fb, fund_stock fs, basic_info bi, quote q " \
          "where q.code = bi.code and fb.code = fs.fund_code and bi.code = fs.code and fb.`date` = fund_date " \
          "and q.trade_date = %s and fund_date = %s and fb.code = %s" \

    val = (trade_date, fund_date, fund_code)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['fund_code'])
    return df


def query_stat(sql, val):
    with mysqlcli.get_connection() as c:
        cur = c.cursor()
        cur.execute(sql, val)
        r = cur.fetchone()
        return r


def query_funds_count(fund_date):
    scale = 0
    sql_count = "select count(*) count " \
                "from fund_basic fb " \
                "where date = %s and scale > %s"

    val = (fund_date, scale)
    r = query_stat(sql_count, val)
    return r['count']


def query_funds_scale(fund_date):
    scale = 0

    sql_scale = "select sum(scale) scale " \
                "from fund_basic fb " \
                "where date = %s and scale > %s"

    val = (fund_date, scale)
    r = query_stat(sql_scale, val)
    return r['scale']


def query_funds_market_value(fund_date):
    scale = 0

    sql_market_value = "select sum(fs.market_value) market_value " \
                       "from fund_basic fb, fund_stock fs " \
                       "where fb.code = fs.fund_code and fb.`date` = fund_date " \
                       "and fund_date = %s and fb.scale > %s"

    val = (fund_date, scale)
    r = query_stat(sql_market_value, val)
    return r['market_value']


def query_market_value(fund_date):
    trade_date = dt.get_pre_trade_date(fund_date + datetime.timedelta(days=1))
    sql = "select sum(mktcap) mktcap from quote where trade_date = %s"
    val = (trade_date,)
    r = query_stat(sql, val)
    return r['mktcap']


def query_funds(fund_date):
    count = query_funds_count(fund_date)
    scale = query_funds_scale(fund_date)
    market_value = query_funds_market_value(fund_date)
    market_value_total = query_market_value(fund_date)

    return {
        'count': count,
        'scale': scale,
        'market_value': market_value,
        'market_value_total': market_value_total
    }
