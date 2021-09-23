# -*- coding: utf-8 -*-
"""
1 基金持有的小市值股票
"""
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


def query_one_stock():
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


def query_stocks():
    sort_by = 'fc'  # 'fmvp'
    trade_date = dt.get_pre_trade_date()
    fund_date = '2021-06-30'
    scale = 0  # 10
    nmc = config.SELECTOR_FUND_STOCK_NMC_MAX  # 50
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
        df = df.sort_values(by=[sort_by])
    return df


def query_one_fund():
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


def query_funds():
    fund_date = '2021-06-30'
    scale = 10
    sql_count = "select count(*) " \
                "from fund_basic fb " \
                "where date = %s and scale > %s"

    sql_scale = "select sum(scale) " \
                "from fund_basic fb " \
                "where date = %s and scale > %s"

    sql_market_value = "select sum(fs.market_value) " \
                       "from fund_basic fb, fund_stock fs " \
                       "where fb.code = fs.fund_code and fb.`date` = fund_date " \
                       "and fund_date = %s and fb.scale > %s"

    sql = sql_count
    sql = sql_scale
    scale = 0
    sql = sql_market_value
    val = (fund_date, scale)
    with mysqlcli.get_connection() as c:
        cur = c.cursor()
        cur.execute(sql, val)
        r = cur.fetchone()
        print(r)

    mktcap_total = query_market_value()
    print(mktcap_total)


def query_market_value():
    trade_date = dt.get_pre_trade_date()
    sql = "select sum(mktcap) mktcap from quote where trade_date = %s"
    val = (trade_date,)
    with mysqlcli.get_connection() as c:
        cur = c.cursor()
        cur.execute(sql, val)
        r = cur.fetchone()
        return r['mktcap']
