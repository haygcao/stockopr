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
from indicator import momentum


def compute_momentum(date, code):
    quote = quote_db.get_price_info_df_db_day(code, 750)
    if len(quote) < 250:
        return

    quote = momentum.momentum_month(quote, 'day')
    datetime_ = datetime.datetime.combine(date, datetime.datetime.min.time())
    index = quote.index[quote.index <= datetime_][-1]
    _ = quote.loc[index, ['code', 'momentum', 'fip', 'mktcap']]
    return _


def compute_momentums(date, mp=True):
    date = date if date else datetime.date.today()
    date = datetime.date(date.year, date.month, calendar.monthrange(date.year, date.month)[1])

    df = pandas.DataFrame(columns=['code', 'momentum', 'fip', 'mktcap'])

    code_list = basic.get_all_stock_code()
    # code_list = code_list[:100]

    if not mp:
        for code in code_list:
            quote = quote_db.get_price_info_df_db_day(code, 750)
            quote = momentum.momentum_month(quote, 'day')
            _ = quote.loc[quote.index[-1], ['code', 'momentum', 'fip', 'mktcap']]
            if not isinstance(_, pandas.Series):
                continue
            df = df.append(_)
    else:
        compute_momentum_func = functools.partial(compute_momentum, date)
        nproc = multiprocessing.cpu_count()
        with multiprocessing.Pool(nproc) as p:
            for _ in tqdm.tqdm(p.imap_unordered(compute_momentum_func, code_list), total=len(code_list), ncols=64):
                if not isinstance(_, pandas.Series):
                    continue
                df = df.append(_)

    df = df.sort_values(by=['momentum'], ascending=False)

    return df


def select_pioneer(date, m, n, dump=False, mp=True):
    df = compute_momentums(date, mp)

    df_pioneer = df[:int(len(df) * m)].sort_values(by=['fip'])
    df_pioneer = df_pioneer[:n]

    if dump:
        cache_dir = util.get_cache_dir()
        df_pioneer.to_csv(os.path.join(cache_dir, 'momentum_{}.csv'.format(
            datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))))

    return df_pioneer.code.to_list()
