# -*- coding: utf-8 -*-

import config.config as config
import selector.util as util
from acquisition import quote_db
from util import util
from util.macd import bbands


def step_ma_one_day(quote, mas, almost, back_day):
    one_day_ma_val_list = [v[-back_day - 1] for k, v in mas.items()]
    l = min(one_day_ma_val_list)
    m = max(one_day_ma_val_list)
    if util.almost_equal(l, m, almost):
        # print('{0}\t{1}\t{2}'.format(l, m, (m-l)*100/l))
        return True


# boll 曲线中线也许更好一些
# r 表示取前n个ma
def step_ma(quote, mas, almost, back_days):
    """检查交易日begin-duration到交易日begin期间,
    每一天的一组MA值的最大差值是否约等
    """
    periods = list(mas.keys())
    periods.sort()

    slowest_period = periods[-1]
    slowest_ma = mas[slowest_period]
    mid_period = periods[len(periods)//2]
    mid_ma = mas[mid_period]
    for back_day in range(back_days):
        current = -back_day - 1
        up_percent = (slowest_ma[current] / slowest_ma[current - slowest_period] - 1) * 100
        if up_percent < slowest_period//10 * 5:
            continue

        if not util.almost_equal(mid_ma[current], mid_ma[current - mid_period], 3):
            continue

        if step_ma_one_day(quote, mas, almost, back_day):
            # print('{0}\t{1}\t{2}'.format(l, m, (m-l)*100/l))
            return back_day
    return


def step_boll(quote, b=config.STEP_BOLL_BACK, d=config.STEP_BOLL_DURATION):
    r = bbands(quote)

    # l = min(r['middleband'][(b+d)*-1+1:(b+int(d/2))*-1+1])
    # m = max(r['middleband'][(b+d)*-1+1:(b+int(d/2))*-1+1])
    # if not util.almost_equal(l, m, 3):
    #     return False
    # l = min(r['middleband'][(b+int(d/2))*-1+1:b*-1+1])
    # m = max(r['middleband'][(b+int(d/2))*-1+1:b*-1+1])
    # if not util.almost_equal(l, m, 3):
    #    return False
    for i in range(5, b):
        l = min(r['middleband'][(i+d)*-1+1:i*-1+1])
        m = max(r['middleband'][(i+d)*-1+1:i*-1+1])
        if util.almost_equal(l, m, 5):
            return True
    return False


# 横盘也很多表现形式
def step(quote, period, periods=None, almost=1, back_days=20):
    if period == 'week':
        quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    if periods is None:
        periods = [5, 10, 20, 30]

    mas = {}
    for p in periods:
        mas.update({p: quote.close.rolling(p).mean()})
    if not step_ma(quote, mas, almost, back_days):
        return False

    return True


def step_p(quote, period, periods=None, almost=1, back_days=20):
    if period == 'week':
        quote = quote_db.get_price_info_df_db_week(quote, period_type='W')
    if periods is None:
        periods = [5, 10, 20, 30]
    if not step(quote, periods, almost, back_days):
        return False
    if not step_boll(quote):
        return False

    return True

    # day_list = [250, 120, 80, 60, 40, 30, 20, 10, 5]
    # day_list = [80, 60, 40, 30, 20, 10, 5] #5, 横盘中, 突破由监控程序处理
    # day_list = [60, 40, 30, 20, 10, 5] #5, 横盘中, 突破由监控程序处理
    # day_list = [40, 30, 20, 10, 5] #5, 横盘中, 突破由监控程序处理
    # day_list = [30, 20, 10, 5] #5, 横盘中, 突破由监控程序处理
    # val_list = []
    # for day in day_list:
    #     val_list.append(price.get_price_stat_db(code, 'p', day, 'avg'))
    # val_max = max(val_list)
    # val_min = min(val_list)
    # diff = abs(val_max - val_min) * 100 / val_min
    # # 长期横盘
    # if diff < 50:
    #     # 加入监控列表
    #     print(code)
    #     #basic.add_selected(code)
