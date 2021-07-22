# -*- coding: utf-8 -*-
import numpy
import pandas

from acquisition import quote_db
from indicator.decorator import computed
from util import macd, dt


def second_stage(quote, period):
    """
    股票魔法师 - 第二阶段特点
    1 股票价格在200日(40周)SMA均线以上
    2 200日均线已呈现上涨趋势
    3 150均线在200日均线以上
    4 股票价格有明显上涨趋势, 价格曲线如台阶状上涨
    5 短期移动平均线在长期移动平均线以上
    6 相较于价格萎靡不振时, 价格猛增的日子里股票交易量同样增长明显
    7 交易量较大的同周中, 上涨的交易周数量高于下跌的
    """

    if period != 'day':
        return False

    n = {
        'xxs': 10,
        'xs': 20,
        's': 50,
        'm': 100,
        'l': 100,
        'xl': 150,
        'xxl': 200
    }
    back_day = 120

    # if period == 'day':
    #     quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    #
    # n = {
    #     'xxs': 2,
    #     'xs': 4,
    #     's': 10,
    #     'm': 20,
    #     'l': 20,
    #     'xl': 30,
    #     'xxl': 40
    # }
    # back_day = 24

    ma_xxs = macd.ma(quote.close, n['xxs'])['ma']
    ma_xs = macd.ma(quote.close, n['xs'])['ma']
    ma_s = macd.ma(quote.close, n['s'])['ma']
    # ma_m = macd.ma(quote.close, 100)['ma']
    ma_l = macd.ma(quote.close, n['l'])['ma']   # 20W
    ma_xl = macd.ma(quote.close, n['xl'])['ma']   # 30W
    # ma_xxl = macd.ma(quote.close, 200)['ma']  # 40W

    if quote.close[-1] <= ma_xl.iloc[-1]:
        return False

    ma_xl_shift = ma_xl.shift(periods=1)
    diff = ma_xl > ma_xl_shift
    if not diff.iloc[-5:].all():
        return False

    if ma_xl.iloc[-1] >= ma_l.iloc[-1]:
        return False

    low = quote.close.iloc[-back_day:].min()
    if quote.close[-1]/low - 1 < 0.3:
        return False

    if not (ma_l.iloc[-1] < ma_s.iloc[-1] < ma_xs.iloc[-1] < ma_xxs.iloc[-1]):
        return False

    up_percent = 7
    up_day_mask = quote.percent.iloc[-back_day:] > up_percent
    other_day_mask = quote.percent.iloc[-back_day:] < 2

    up_vol = quote.volume.iloc[-back_day:][up_day_mask]
    other_vol = quote.volume.iloc[-back_day:][other_day_mask]
    up_vol_mean = up_vol.mean()
    other_vol_mean = other_vol.mean()
    if up_vol_mean / other_vol_mean < 2:
        return False

    quote_week = quote_db.get_price_info_df_db_week(quote, period_type='W')
    back_week = 40
    vol_min = quote_week.volume[-back_week:].rolling(5).min()
    vol_max = quote_week.volume[-back_week:].rolling(5).max()
    m = vol_max > vol_min * 10
    match = m[m]
    if len(match) == 0:
        return False

    first = match.index[0]
    # vol_mean1 = vol.loc[:first]
    # vol_mean2 = vol.loc[first:]

    up_week_mask = quote_week.percent[first:] > 0
    # vol_mean = quote_week.volume[-back_week:].mean()
    # up_vol_mask = quote_week.volume[-back_week:] > vol_mean
    if numpy.count_nonzero(up_week_mask) * 2 < len(up_week_mask):
        return False

    return True


@computed(column_name='second_stage')
def compute_second_stage(quote, period='day'):
    mask = pandas.Series(False, index=quote.index)
    size = len(mask)
    back_day = 0 if dt.istradetime() else 120
    # back_day = 0
    for day in range(back_day, 0, -1):
        ret = second_stage(quote[:-day], period)
        mask.iat[size - 1 - day] = ret
    ret = second_stage(quote, period)
    mask.iat[-1] = ret
    quote.insert(len(quote.columns), 'second_stage', mask)

    return quote
