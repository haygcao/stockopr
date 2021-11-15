# -*- coding: utf-8 -*-
"""
https://boards.fool.com/i-think-i-read-somewhere-that-ibd-rs-formula-is-12506717.aspx

I think I read somewhere that IBD RS formula is something like 1/4 * 13wk + 1/4 *26 wk + 1/4 *39 wk + 1/4 * 52 wk. Is this correct?

The formula is
2/5 * 13wk + 1/5 *26 wk + 1/5 *39 wk + 1/5 * 52 wk.

In particular I wanted to know what is the vulnerability of this formula on a particular day's price swing when the prices points
are taken? Or is it more sophisticated and takes care of one day swings at measuring points?

The formula is simple, and that's its beauty. Yes, its value can change if a stock moves 10% in a day, but daily moves are usually not much compared to the 52 week return.

Also, after the formula is calculated for all stocks they are ranked by percentiles. You can think of each percentile bucket as a range. For example, all stocks where the formula produces a number between 150 and 170 might be in the 98th percentile bucket. A price move of a few percent is not likely to move it out of the bucket. Overall, the IBD-RS rankings are surprisingly stable over time.

I don't remember the underlying formula for the EPS rankings.

Elan
"""

import datetime
import multiprocessing
import os
import time

import numpy
import pandas
import tqdm

from acquisition import quote_db, basic
from util import mysqlcli, util, dt
from util.log import logger


def compute_strength(quote):
    q1 = 0.4 * quote.close / quote.close.shift(periods=63)
    q2 = 0.2 * quote.close / quote.close.shift(periods=63 * 2)
    q3 = 0.2 * quote.close / quote.close.shift(periods=63 * 3)
    q4 = 0.2 * quote.close / quote.close.shift(periods=63 * 4)

    rate = q1 + q2 + q3 + q4
    _ = pandas.DataFrame({'strength': rate, 'qtr_x1': q1, 'qtr_x2': q2, 'qtr_x3': q3, 'qtr_x4': q4}, index=quote.index)
    return _


def compute_rs_rating(code_list, trade_date, begin_trade_date, mp):
    t1 = time.time()
    if not trade_date:
        trade_date = datetime.date.today()

    if not begin_trade_date:
        begin_trade_date = trade_date - datetime.timedelta(days=380)
    var_code_list = code_list if len(code_list) < 10 else None
    quote_all = quote_db.query_quote(trade_date, begin_trade_date=begin_trade_date, code_list=var_code_list)
    quote_all['strength'] = numpy.nan
    quote_all['qtr_x1'] = numpy.nan
    quote_all['qtr_x2'] = numpy.nan
    quote_all['qtr_x3'] = numpy.nan
    quote_all['qtr_x4'] = numpy.nan

    quote_all['rs_rating'] = numpy.nan

    t2 = time.time()
    logger.info('fetch quote finished, cost [{}s]'.format(int(t2 - t1)))
    t1 = t2

    quote_all = quote_all.set_index([quote_all['trade_date'], quote_all['code']], drop=False)

    if mp:
        nproc = multiprocessing.cpu_count()
        with multiprocessing.Pool(nproc) as p:
            arg = [quote_all.loc[quote_all.index.get_level_values(1) == code] for code in code_list]
            t2 = time.time()
            logger.info('generate args finished, cost [{}s]'.format(int(t2 - t1)))
            t1 = t2
            for _ in tqdm.tqdm(p.imap_unordered(compute_strength, arg), total=len(code_list), ncols=64):
                if not isinstance(_, pandas.DataFrame):
                    continue
                quote_all.at[_.index, 'strength'] = _['strength']
    else:
        for code in code_list:
            quote = quote_all[quote_all.index.get_level_values(1) == code]
            _ = compute_strength(quote)
            if not isinstance(_, pandas.DataFrame):
                continue

            quote_all.at[_.index, 'strength'] = _['strength']
            quote_all.at[_.index, 'qtr_x1'] = _['qtr_x1']
            quote_all.at[_.index, 'qtr_x2'] = _['qtr_x2']
            quote_all.at[_.index, 'qtr_x3'] = _['qtr_x3']
            quote_all.at[_.index, 'qtr_x4'] = _['qtr_x4']

    t2 = time.time()
    logger.info('compute strength finished, cost [{}s]'.format(int(t2 - t1)))
    t1 = t2

    trade_days = set(quote_all.index.get_level_values(0).to_list())

    for trade_day in trade_days:
        quote_day = quote_all[quote_all.index.get_level_values(0) == trade_day]
        rs_rating = quote_day['strength'].rank(pct=True)

        quote_all.at[quote_day.index, 'rs_rating'] = round(rs_rating * 100, 3)

    t2 = time.time()
    logger.info('compute rs rating finished, cost [{}s]'.format(int(t2 - t1)))

    return quote_all


def update_rs_rating(trade_date=None, update_db=True):
    cache_dir = util.get_cache_dir()
    path = os.path.join(cache_dir, 'rs_rating_{}.csv'.format(datetime.date.today().strftime('%Y%m%d')))

    cached = os.path.exists(path)
    compute = True

    if trade_date:
        one_trade_date = True
    else:
        one_trade_date = False
        trade_date = dt.get_trade_date()

    # code_list = ['002739', '300502']
    if cached:
        df = pandas.read_csv(path)
        df['trade_date'] = pandas.to_datetime(df['trade_date'])
        df = df.set_index([df['trade_date'], df['code']], drop=False)

        if trade_date in df.index.get_level_values(0).date:
            compute = False

    if not compute:
        return

    code_list = basic.get_all_stock_code()

    weeks = 53 if one_trade_date else 53 * 2
    begin_trade_date = trade_date - datetime.timedelta(weeks=weeks)
    df = compute_rs_rating(code_list, trade_date=trade_date, begin_trade_date=begin_trade_date, mp=True)
    df = df[df['rs_rating'].notna()]
    df['code'] = df['code'].apply(lambda x: str(x).zfill(6))

    val = zip(df['rs_rating'], df['code'], df['trade_date'])  # update
    val_list = val
    # val_list = [(round(100 * t[0], 3), str(t[1]).zfill(6), t[2]) for t in val]

    if one_trade_date:
        trade_dates = df.index.get_level_values(0)
        df = df[trade_dates.date == trade_date]
        if df.empty:
            logger.warning('{} no data'.format(trade_date))
            return

    t1 = time.time()
    logger.info('next to export to csv')
    mode = 'a' if cached else 'w'
    df.to_csv(path, columns=['trade_date', 'code', 'rs_rating',
                             'strength', 'qtr_x1', 'qtr_x2', 'qtr_x3', 'qtr_x4'], index=False, mode=mode)
    t2 = time.time()
    logger.info('export to csv finished, cost [{}s]'.format(int(t2 - t1)))

    if not update_db:
        logger.info('rs rating updated')
        return

    logger.info('next to update table[quote], [{}] rows'.format(len(df)))

    # update executemany 实际是单条执行 self.rowcount = sum(self.execute(query, arg) for arg in args)
    # sql = "update quote set rs_rating = %s where code = %s and trade_date = %s"
    sql = "insert into quote (rs_rating, code, trade_date) values (%s, %s, %s) " \
          "on duplicate key update rs_rating = values(rs_rating)"
    with mysqlcli.get_cursor() as c:
        try:
            c.executemany(sql, val_list)
        except Exception as e:
            logger.error(e)

        # batch = 10000
        # for i in range(len(val_list) // batch):
        #     end = batch * (i + 1)
        #     end = end if end < len(val_list) else None
        #     v = val_list[batch * i: end]
        #     c.executemany(sql, v)

    t2 = time.time()
    logger.info('update table[quote] finished, cost [{}s]'.format(int(t2 - t1)))
    logger.info('rs rating updated')
