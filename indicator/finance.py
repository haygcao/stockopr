# -*- coding: utf-8 -*-
import pandas

from indicator.decorator import computed
from util import mysqlcli


def query_finance(code_list):
    sql = "select code, report_date, " \
          "totaloperatereve, dedu_parent_profit, totaloperatereve_yoy_ratio, dpnp_yoy_ratio, eps, eps_std_rank " \
          "from finance {} order by report_date"
    where = "where code in ('{}')".format("','".join(code_list)) if code_list else ''
    sql = sql.format(where)

    with mysqlcli.get_connection() as conn:
        df_finance = pandas.read_sql(sql, con=conn, index_col=['report_date'])

    return df_finance


def count_ins_continuous(series, ins_percent):
    series_p = (series > ins_percent)
    series_p_shift = series_p.shift(periods=1)

    # def f(s):
    #     n = 0
    #     for i in range(len(s) - 1, 0, -1):
    #         if not s.iloc[i]:
    #             return n
    #         n += 1
    #     return n
    #
    # window_size = min(20, len(series) - 4)
    # window_size = max(window_size, 1)
    # c = (series_p & series_p_shift).rolling(window_size).agg(f)
    # c = c.mask(series_p, c + 1)

    c = pandas.Series([0 for i in range(len(series))], index=series.index)
    c.iat[0] = 1 if not series_p.empty and series_p.iloc[0] else 0
    for i in range(1, len(series), 1):
        if series_p.empty or not series_p.iloc[i]:
            c.iat[i] = 0
        else:
            c.iat[i] = c.iat[i - 1] + 1

    return c


def compute(df_finance):
    dpnp_yoy_ratio = df_finance['dpnp_yoy_ratio']
    totaloperatereve_yoy_ratio = df_finance['totaloperatereve_yoy_ratio']
    # dedu_parent_profit = df_finance['dedu_parent_profit']
    # totaloperatereve = df_finance['totaloperatereve']

    count_dpnp_yoy_ratio = count_ins_continuous(dpnp_yoy_ratio, 0)
    count_totaloperatereve_yoy_ratio = count_ins_continuous(totaloperatereve_yoy_ratio, 0)

    # A value is trying to be set on a copy of a slice from a DataFrame.
    # Try using .loc[row_indexer,col_indexer] = value instead
    # df_finance['count_dpnp_yoy_ratio'] = count_dpnp_yoy_ratio
    # df_finance.loc[:, 'count_dpnp_yoy_ratio'] = count_dpnp_yoy_ratio
    # df_finance.loc[:, 'count_totaloperatereve_yoy_ratio'] = count_totaloperatereve_yoy_ratio
    # df_finance.loc[:, 'dpnp_yoy_ratio_ins'] = df_finance['dpnp_yoy_ratio'] - df_finance['dpnp_yoy_ratio'].shift(
    #     periods=4)

    df_finance_copy = df_finance.copy()
    df_finance_copy['count_dpnp_yoy_ratio'] = count_dpnp_yoy_ratio
    # df_finance_copy.loc[:, 'count_dpnp_yoy_ratio'] = count_dpnp_yoy_ratio
    df_finance_copy.loc[:, 'count_totaloperatereve_yoy_ratio'] = count_totaloperatereve_yoy_ratio
    df_finance_copy.loc[:, 'dpnp_yoy_ratio_ins'] = df_finance['dpnp_yoy_ratio'] - df_finance['dpnp_yoy_ratio'].shift(periods=4)

    # 收益稳定性
    df_finance_copy['eps_std'] = df_finance['eps'].rolling(9).std()

    return df_finance_copy


def finance(code_list):
    result = pandas.DataFrame()

    df_finance = query_finance(code_list)

    for code in code_list:
        df = df_finance[df_finance['code'] == code]
        if df.empty:
            continue
        df = compute(df)
        result = result.append(df)

    return result


@computed(column_name='finance')
def compute_finance(quote):
    df_finance = finance([quote.code[-1]])
    df_finance_day = df_finance.resample('D').pad()  # 需要考虑报表发布的日期
    df_finance_day = df_finance_day[df_finance_day.index.isin(quote.index)]
    cond1 = df_finance_day['dpnp_yoy_ratio'] > 18
    cond2 = df_finance_day['totaloperatereve_yoy_ratio'] > 25

    v = df_finance_day['dpnp_yoy_ratio_ins']
    quote['dpnp_yoy_ratio'] = df_finance_day['dpnp_yoy_ratio']
    quote['finance'] = v.mask(cond1 & cond2, v)

    return quote
