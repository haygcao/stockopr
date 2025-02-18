# -*- coding: utf-8 -*-
"""
1 基金持有的小市值股票
"""
import datetime

import numpy
import pandas

from acquisition import basic
from config import config
from util import mysqlcli, dt
from util.log import logger


def filter_new_stocks(df_data):
    df_stock_days = query_stock_days(df_data.index.to_list())
    series = df_stock_days['count']

    df_data = df_data.sort_index()
    df_data = df_data[series > 250]
    return df_data


def query_one_stock_lite(code, fund_date):
    sql = "select fund_code from fund_stock where fund_date = %s and code = %s"

    val = (fund_date, code)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['fund_code'])
    return df


def query_stocks_percent(code_list):
    val_code = "','".join(code_list)

    today = dt.get_trade_date()
    date_list = [today]

    for date in [7, 15, 30, 91, 183, 365]:
        date_list.append(dt.get_pre_trade_date(today - datetime.timedelta(days=date)))
    val_date = "','".join(map(lambda x: str(x), date_list))
    sql_tpl = "select code, date(trade_date) trade_date, close from quote where code in ('{}') and trade_date in ('{}')"
    sql = sql_tpl.format(val_code, val_date)

    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, index_col=['code'])
    df = df.reset_index()
    df = df.pivot(index='code', columns='trade_date', values='close')
    # df2 = df.unstack('trade_date')

    # print(df.columns, type(df.columns[0]))
    current_close = pandas.DataFrame([[df.loc[j][today] for i in df.columns] for j in df.index],
                                     index=df.index, columns=df.columns)
    df = current_close.div(df) - 1

    return df


def supplement_percent(df):
    df_percent = query_stocks_percent(df.index.to_list())
    df_final = pandas.concat([df, df_percent], axis=1)
    return df_final


def query_stock_by_stock_code_list(code_list, fund_date):
    # trade_date = dt.get_pre_trade_date()
    trade_date = fund_date
    scale = 0  # 10
    nmc = config.SELECTOR_FUND_STOCK_NMC_MAX  # 50
    sql = "select fund_code, fs.code, bi.name, fs.market_value fmv, q.nmc nmc, q.close " \
          "from fund_basic fb, fund_stock fs, basic_info bi, quote q " \
          "where q.code = bi.code and fb.code = fs.fund_code and bi.code = fs.code and fb.`date` = fund_date " \
          "and q.trade_date = %s and fund_date = %s and fb.`scale` > %s and nmc < %s and q.code in ('{}')" \

    sql = sql.format("','".join(code_list))
    val = (trade_date, fund_date, scale, nmc * 10000)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['fund_code'])
    return df


def query_stock(code, fund_date):
    """
    计算股票, 对应的基金个数, 基金持有市值, 以及占流通股的比例
    """
    return query_stock_by_stock_code_list([code], fund_date)


def query_stocks(fund_date, fund_list=None, sort=False):
    """
    统计各股票, 对应的基金个数, 基金持有市值, 以及占流通股的比例
    """
    sort_by = 'fmvp'
    trade_date = dt.get_pre_trade_date(fund_date + datetime.timedelta(days=1))  # dt.get_pre_trade_date()
    scale = 10
    nmc = config.SELECTOR_FUND_STOCK_NMC_MAX
    # nmc = 50
    sql = "select fs.code, bi.name, count(fs.code) fc, sum(fs.market_value) fmv, q.nmc nmc, q.close " \
          "from fund_basic fb, fund_stock fs, basic_info bi, quote q " \
          "where q.code = bi.code and fb.code = fs.fund_code and bi.code = fs.code and fb.`date` = fund_date " \
          "and q.trade_date = %s and fund_date = %s and fb.`scale` > %s and nmc < %s "
    group_by = "group by fs.code "
    order_by = "order by q.nmc "

    if fund_list:
        sql += " and fb.code in ('{}') ".format("','".join(fund_list))
    sql += group_by

    val = (trade_date, fund_date, scale, nmc * 10000)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['code'])
        df['nmc'] = df['nmc'].fillna(-1)
        df['fmvp'] = round(df['fmv'] / df['nmc'], 3)

    df = filter_new_stocks(df)
    if sort:
        df = df.sort_values(by=[sort_by], ascending=False)
    return df


def query_stocks_fund_market_value_diff(fund_date_prev, fund_date_next):
    """

    """
    df_prev = query_stocks(fund_date_prev)
    df_next = query_stocks(fund_date_next)
    df_prev.sort_index(inplace=True)
    df_next.sort_index(inplace=True)

    r = pandas.DataFrame()
    for col in ['fmvp', 'fc']:
        diff = df_next[col] - df_prev[col]
        mask1 = diff.isna()
        mask2 = df_next[col] >= 0
        diff = diff.mask(mask1 & mask2, df_next[col])

        mask1 = diff.isna()
        mask2 = df_prev[col] >= 0
        diff = diff.mask(mask1 & mask2, -df_prev[col])

        diff = diff.sort_values(ascending=False)

        df = pandas.DataFrame(diff, index=diff.index)
        df.insert(0, 'name', df_next['name'])
        # df = df.assign(name=df_next['name'])
        df.name = df.name.mask(df.name.isna(), df_prev.name)
        df = df.rename(columns={col: col + '_diff'})

        if r.empty:
            r = df.copy()
        else:
            r[col + '_diff'] = df[col + '_diff']

    return r


def query_stocks_fund_theme_specified(fund_date, fund_name):
    df = query_funds(fund_date, fund_name)
    # fund_list = df.index.drop_duplicates().to_list()
    # df1 = query_stocks(fund_date, fund_list, sort=True)
    # return df1

    df_group = df.groupby(['code'])

    df = df.reset_index(drop=True)
    df = df.set_index('code')

    df_stock = df[['name', 'nmc', 'close']]
    df_stock = df_stock.drop_duplicates()
    df_stock = df_stock.sort_index()

    df_mkt = df_group['market_value'].sum()
    df_mkt = df_mkt.sort_index()
    df_final = pandas.concat([df_stock, df_mkt], axis=1)
    df_final['fmvp'] = round(df_final['market_value'] / df_final['nmc'], 3)
    df_final = df_final.sort_values(by=['fmvp'], ascending=False)
    return df_final


def query_fund(fund_name=None):
    trade_date = dt.get_pre_trade_date()
    fund_date = '2021-06-30'
    fund_code = '001283'
    sql = "select fund_code, fb.scale, fs.code, bi.name, q.nmc nmc, q.close, fs.market_value " \
          "from fund_basic fb, fund_stock fs, basic_info bi, quote q " \
          "where q.code = bi.code and fb.code = fs.fund_code and bi.code = fs.code and fb.`date` = fund_date " \
          "and q.trade_date = %s and fund_date = %s and fb.code = %s "
    val = [trade_date, fund_date, fund_code]
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, params=val, index_col=['fund_code'])
    return df


def query_funds(fund_date, fund_name=None):
    scale = 10
    trade_date = dt.get_pre_trade_date()
    sql = "select fund_code, fb.scale, fs.code, bi.name, q.nmc nmc, q.close, fs.market_value " \
          "from fund_basic fb, fund_stock fs, basic_info bi, quote q " \
          "where q.code = bi.code and fb.code = fs.fund_code and bi.code = fs.code and fb.`date` = fund_date " \
          "and q.trade_date = %s and fund_date = %s and fb.scale > %s "
    val = [trade_date, fund_date, scale]
    if fund_name:
        sql += "and fb.name like %s "
        val.append('%{}%'.format(fund_name))
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


def query_latest_date():
    sql = "select max(date) date from fund_basic"
    val = None
    r = query_stat(sql, val)
    return r['date']


def query_stock_days(code_list):
    sql_tmp = "select code, count(*) count from quote where code in ('{}') group by code"
    val_code_list = "','".join(code_list)
    sql = sql_tmp.format(val_code_list)
    with mysqlcli.get_connection() as c:
        df = pandas.read_sql(sql, c, index_col=['code'])
    return df


def query_fund_stat(fund_date):
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


def update_fund_market_value(fund_date):
    code_list = basic.get_all_stock_code()

    logger.info('compute fund market value percent')
    val_list = []

    df = query_stock_by_stock_code_list(code_list, fund_date)
    logger.info('query position of fund [{}][{}]'.format(fund_date, len(df)))

    group = df.groupby('code')
    group_sum = group.sum()
    group_one = group.first()
    code = group_one.index
    date = pandas.Series(fund_date, index=code)
    nmc = group_one['nmc']
    fmv = group_sum['fmv']
    fmvp = round(100 * fmv / nmc, 3)
    val_list = zip(nmc, fmv, fmvp, code, date)

    # for code in code_list:
    #     df1 = df[df.code == code]
    #     if df1.empty:
    #         continue
    #
    #     nmc = df1.nmc[-1]
    #     fmv = df1.fmv.sum()
    #     fmvp = round(100 * fmv / nmc, 3)
    #
    #     val_list.append((nmc, fmv, fmvp, code, fund_date))

    logger.info('compute fund market value percent finished')

    with mysqlcli.get_cursor() as c:
        c.execute('select count(code) c from finance where report_date = %s', (fund_date, ))
        r = c.fetchone()
        if r['c'] > 2000:
            # 需要依赖 finance 数据先更新, 不然会导致 finance 数据更新失败
            sql = 'insert into finance(nmc, fmv, fmvp, code, report_date) values(%s, %s, %s, %s, %s) ' \
                  'on duplicate key update nmc = values(nmc), fmv = values(fmv), fmvp = values(fmvp)'
        else:
            sql = 'update finance set nmc = %s, fmv = %s, fmvp = %s where code = %s and report_date = %s'

        logger.info(sql)
        c.executemany(sql, val_list)

    logger.info('update fund market value percent finished')


def fund(quote, period, backdays):
    code = quote.code[-1]
    fmvp = query_fmvp(code)

    # df1 = query_stock(code, fund_date)
    # if df1.empty:
    #     return False
    #
    # fmvp = 100 * df1.fmv.sum() / df1.nmc[-1]

    return fmvp > 1


def query_fmvp(code):
    fund_date = query_latest_date()
    with mysqlcli.get_cursor() as c:
        c.execute('select fmvp from finance where code = %s and report_date = %s', (code, fund_date))
        r = c.fetchone()

        # 退市股在 finance表中没有记录 没有基金持有则 fmvp字段为 NULL
        if r and r['fmvp']:
            fmvp = r['fmvp']
        else:
            fmvp = 0
    return fmvp
