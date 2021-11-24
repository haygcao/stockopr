# -*- coding: utf-8 -*-
import numpy
import pandas

from acquisition import quote_db
from indicator import ma
from indicator.decorator import computed
from util import dt


@computed(column_name='second_stage')
def second_stage(quote, period):
    """
    股票魔法师 P66
    股票魔法师II P84
    """
    close = quote['close']
    ytd_close = quote['close'].shift(periods=1)

    # Compute SMA & high/low
    quote = ma.compute_ma(quote)
    mov_avg_50 = quote['ma50']
    mov_avg_150 = quote['ma150']
    mov_avg_200 = quote['ma200']
    mov_avg_200_shift = mov_avg_200.shift(periods=1)  # SMA 200 1 month before (for calculating trending condition)
    low_of_52week = close.rolling(250).min()  # min(quote['close'][-250:])
    high_of_52week = close.rolling(250).max()  # max(quote['close'][-250:])

    # Condition checks
    # Condition 1: Current Price > 50 SMA > 150 SMA > 200 SMA
    condit_1 = (close > mov_avg_50) & (mov_avg_50 > mov_avg_150) & (mov_avg_150 > mov_avg_200)

    # Condition 2: 200 SMA trending up for at least 1 month (ideally 4-5 months)
    condit_2 = ((mov_avg_200 > mov_avg_200_shift).rolling(20).min() == 1)

    # Condition 3: Current Price is at least 30% above 52 week low
    # Many of the best are up 100-300% before coming out of consolidation
    condit_3 = (close >= (1.3 * low_of_52week))

    # Condition 4: Current Price is within 25% of 52 week high, and at 10 days ago
    condit_4 = (close >= 0.75 * high_of_52week)

    condit = condit_1 & condit_2 & condit_3 & condit_4

    if period == 'day':
        # Condition 5: IBD RS ratings of the stock > 70
        condit_5 = ma.ma(quote.rs_rating, 5) >= 70
        condit &= condit_5

    quote['second_stage'] = numpy.nan

    quote['second_stage'] = quote['second_stage'].mask(condit, quote.low)

    return quote


@computed(column_name='second_stage')
def second_stage_(quote, period):
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
        return quote

    n = {
        'xxs': 10,
        'xs': 20,
        's': 30,
        'm': 60,
        'l': 120,
        'xl': 150,
        'xxl': 200
    }

    quote = ma.compute_ma(quote)

    ma_xxs = quote['ma{}'.format(n['xxs'])]
    ma_xs = quote['ma{}'.format(n['xs'])]
    ma_s = quote['ma{}'.format(n['s'])]
    ma_m = quote['ma{}'.format(n['m'])]
    ma_l = quote['ma{}'.format(n['l'])]
    ma_xl = quote['ma{}'.format(n['xl'])]
    ma_xxl = quote['ma{}'.format(n['xxl'])]

    mask1 = quote.close > ma_xxl

    ma_xxl_shift = ma_xxl.shift(periods=1)
    mask2 = ma_xxl > ma_xxl_shift

    mask3 = ma_xxl < ma_xl

    # close up
    mask4 = ma_xxs/ma_xxl - 1 > 0.2

    mask5 = (ma_xl < ma_l) & (ma_l < ma_m)  # & (ma_m < ma_s) & (ma_s < ma_xs) & (ma_xs < ma_xxs)

    mask = mask1 & mask2 & mask3 & mask4 & mask5

    quote.insert(len(quote.columns), 'second_stage', mask)

    return quote

    up_percent = 7
    up_day_mask = quote.percent > up_percent
    other_day_mask = quote.percent < 2

    up_vol = quote.volume.mask(~up_day_mask, numpy.nan)
    other_vol = quote.volume.mask(~other_day_mask, numpy.nan)

    up_vol_mean = up_vol.rolling(20, min_periods=1).mean()
    other_vol_mean = other_vol.rolling(20, min_periods=1).mean()
    mask6 = up_vol_mean < (other_vol_mean * 1.5)
    mask = mask.mask(mask6, False)

    vol_mean = quote.volume.rolling(20).mean()
    mask_vol = quote.volume > (vol_mean * 1.5)
    vol = quote.percent.mask(~mask_vol, numpy.nan)
    mask_percent = quote.percent > 0
    mask_vol_percent = mask_vol & mask_percent
    percent = quote.percent.mask(~mask_vol_percent, numpy.nan)

    vol_count = vol.rolling(20, min_periods=1).count()
    percent_count = percent.rolling(20, min_periods=1).count()

    mask7 = (percent_count * 2) < vol_count
    mask = mask.mask(mask7, False)

    quote.insert(len(quote.columns), 'second_stage', mask)

    return quote


def second_stage_ex(quote, period):
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
    vol_times = 4

    # if period == 'day':
    #     quote = quote_db.resample_quote(quote, period_type='W')
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

    ma_xxs = ma.ma(quote.close, n['xxs'])['ma']
    ma_xs = ma.ma(quote.close, n['xs'])['ma']
    ma_s = ma.ma(quote.close, n['s'])['ma']
    # ma_m = ma.ma(quote.close, 100)['ma']
    ma_l = ma.ma(quote.close, n['l'])['ma']   # 20W
    ma_xl = ma.ma(quote.close, n['xl'])['ma']   # 30W
    # ma_xxl = ma.ma(quote.close, 200)['ma']  # 40W

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

    quote_week = quote_db.resample_quote(quote, period_type='W')
    back_week = 40
    # vol_min = quote_week.volume[-back_week:].rolling(5).min()
    vol_min = quote_week.volume[-back_week:].rolling(5).mean()
    vol_min = vol_min.shift(periods=1)
    vol_max = quote_week.volume[-back_week:].rolling(5).max()
    m = vol_max > vol_min * vol_times
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
        ret = second_stage_ex(quote[:-day], period)
        mask.iat[size - 1 - day] = ret
    ret = second_stage_ex(quote, period)
    mask.iat[-1] = ret
    quote.insert(len(quote.columns), 'second_stage', mask)

    return quote
