# -*- coding: utf-8 -*-
from acquisition import quote_db
from util import util
from util.macd import ema
from . import super


def base_breakout(quote):
    # 重采样为 周数据
    quote = quote_db.get_price_info_df_db_week(quote, period_type='W')

    s = ema(quote['close'], n=5)['ema'].iloc[-4]
    m = ema(quote['close'], n=10)['ema'].iloc[-4]
    if not util.almost_equal(m, s, 10):
        return False

    if not super.high_angle(quote, back_day=2):
        return False

    return super.strong_breakout(quote, current=-3)
