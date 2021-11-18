# -*- coding: utf-8 -*-
from acquisition import basic
from indicator import finance
from util import mysqlcli


def update_finance():
    code_list = basic.get_all_stock_code()
    # code_list = code_list[:10]

    df = finance.finance(code_list)
    df = df.set_index([df.index, df['code']], drop=False)
    report_dates = set(df.index.get_level_values(0).to_list())
    for date in report_dates:
        # rank
        df_ = df[df.index.get_level_values(0) == date]
        # df_ = df_[(df_['dpnp_yoy_ratio'] < 18) | (df_['totaloperatereve_yoy_ratio'] < 25)]
        df.at[df_.index, 'eps_std_rank'] = round(100 * df_['eps_std'].rank(pct=True), 0)

    df = df[df['eps_std_rank'].notna()]
    val_list = zip(df['eps_std_rank'], df['code'], df.index.get_level_values(0))
    with mysqlcli.get_cursor() as c:
        sql = 'insert into finance (eps_std_rank, code, report_date) values (%s, %s, %s) ' \
              'on duplicate key update eps_std_rank = values(eps_std_rank)'
        c.executemany(sql, val_list)


if __name__ == '__main__':
    update_finance()
