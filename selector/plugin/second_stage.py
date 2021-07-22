# -*- coding: utf-8 -*-
import numpy

from acquisition import quote_db
from util import macd


def second_stage(quote):
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

    ma10 = macd.ma(quote.close, 10)['ma']
    ma30 = macd.ma(quote.close, 30)['ma']
    ma60 = macd.ma(quote.close, 60)['ma']
    ma150 = macd.ma(quote.close, 150)['ma']
    ma200 = macd.ma(quote.close, 200)['ma']

    if quote.close[-1] <= ma200.iloc[-1]:
        return False

    ma200_shift = ma200.shift(periods=1)
    diff = ma200 > ma200_shift
    if not diff.iloc[-5:].all():
        return False

    if ma200.iloc[-1] >= ma150.iloc[-1]:
        return False

    back_day = 120
    low = quote.close.iloc[-back_day:].min()
    if quote.close[-1]/low - 1 < 0.3:
        return False

    if not (ma150.iloc[-1] < ma60.iloc[-1] < ma30.iloc[-1] < ma10.iloc[-1]):
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
    vol = quote_week.volume[-back_week:]
    vol_shift = vol.shift(periods=1)
    m = vol > vol_shift * 3
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
