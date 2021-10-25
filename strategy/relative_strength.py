# -*- coding: utf-8 -*-
import calendar
import datetime
import functools
import multiprocessing
import os.path

import pandas
import tqdm

from util import util
from acquisition import basic, quote_db
from indicator import relative_price_strength


def compute_stock_rs(date, code):
    quote = quote_db.get_price_info_df_db_day(code, 750)
    if len(quote) < 250:
        return

    rps_column = 'rpsmaq'
    quote = relative_price_strength.relative_price_strength(quote, 'day')
    quote['rps20'] = quote[rps_column].rolling(20).mean()
    quote['rps60'] = quote[rps_column].rolling(60).mean()
    quote['rps120'] = quote[rps_column].rolling(120).mean()
    quote['rps250'] = quote[rps_column].rolling(250).mean()
    datetime_ = datetime.datetime.combine(date, datetime.datetime.min.time())
    index = quote.index[quote.index <= datetime_][-1]
    _ = quote.loc[index, ['code', rps_column, 'rps20', 'rps60', 'rps120', 'rps250', 'mktcap']]
    return _


def compute_rs(date, mp=True):
    date = date if date else datetime.date.today()
    # date = datetime.date(date.year, date.month, calendar.monthrange(date.year, date.month)[1])

    column_list = ['code', 'rpsmaq', 'rps20', 'rps60', 'rps120', 'rps250', 'mktcap']
    df = pandas.DataFrame(columns=column_list)

    code_list = basic.get_all_stock_code()
    # code_list = code_list[:100]

    if not mp:
        for code in code_list:
            _ = compute_stock_rs(date, code)
            if not isinstance(_, pandas.Series):
                continue
            df = df.append(_)
    else:
        compute_momentum_func = functools.partial(compute_stock_rs, date)
        nproc = multiprocessing.cpu_count()
        with multiprocessing.Pool(nproc) as p:
            for _ in tqdm.tqdm(p.imap_unordered(compute_momentum_func, code_list), total=len(code_list), ncols=64):
                if not isinstance(_, pandas.Series):
                    continue
                df = df.append(_)

    sort_by = 'rps250'
    df = df.sort_values(by=[sort_by], ascending=False)

    return df


def select_pioneer(date, m, n, dump=False, mp=True):
    df = compute_rs(date, mp)

    sort_by = 'rps20'
    df_pioneer = df[:int(len(df) * m)].sort_values(by=[sort_by], ascending=False)
    df_pioneer = df_pioneer[:n]

    if dump:
        cache_dir = util.get_cache_dir()
        df_pioneer.to_csv(os.path.join(cache_dir, 'rps_{}.csv'.format(
            datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))))

    return df_pioneer.code.to_list()
