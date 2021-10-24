# -*- coding: utf-8 -*-

"""
ConnorsRSI

ConnorsRSI is calculated by taking the average of its three components.
ConnorsRSI(3,2,100) = (RSI(3) + RSI(Streak,2) + PercentRank(100)) / 3

ConnorsRSI Components
The ConnorsRSI indicator is made up of three components:

Relative Strength Index
The first component is a simple 3-period RSI of price. This component measures price momentum on a scale of 0-100.

Up/Down Streak Length
The second component is a 2-period RSI of the up/down streak length. It measures the duration of the trend.
The up/down streak is essentially the number of days in a row that the security's closing price has been higher (up) or lower (down) than the previous day's close. If a stock closes above its previous close three days in a row, then the up/down streak is +3. If it has closed below its previous close for 2 days, then its streak is -2. If it does not change price between one period and the next, then the streak is reset to 0.
Applying the 2-period RSI to this streak value converts it to a bound oscillator where values must be in the range of 0-100.

Magnitude of Price Change
The third component ranks the most recent period's price change against the price change of the other periods in the specified timeframe (100 periods by default).
Essentially you determine the percentage of previous price changes that are lower than the most recent one.
For example, if you specify a 20-day timeframe, and 7 of those 20 price change values are lower than today's price change, then 7 / 20 = 0.35 = 35%.
Again, defining this as a percentage restricts the component to a scale of 0-100. If today's price change was large and positive, the value of this component will be closer to 100; large negative price changes will result in a value closer to 0.
"""

import bottleneck as bn
import numpy
import pandas

from indicator import rsi
from indicator.decorator import computed


@computed(column_name='crsi')
def compute_crsi(quote, period):
    quote['crsi'] = crsi(quote, period)

    return quote


def count_continuous(arr):
    c = 0
    for i in range(len(arr) - 1, -1, -1):
        if not arr[i]:
            break
        c += 1
    if c == 0:
        return numpy.nan
    return c + 1


def crsi(quote, period):
    # https://github.com/pandas-dev/pandas/issues/9481

    # 1
    series_rsi = rsi.rsi(quote.close, 3)

    # 2
    close = quote.close
    close_yest = close.shift(periods=1)
    mask_up = close > close_yest
    mask_up_shift = mask_up.shift(periods=1)
    mask_up_con = mask_up & mask_up_shift
    series_up_streak_length = mask_up_con.rolling(20).apply(lambda x: count_continuous(x))
    series_up_streak_length = series_up_streak_length.mask(mask_up & series_up_streak_length.isna(), 1)

    mask_down = close < close_yest
    mask_down_shift = mask_down.shift(periods=1)
    mask_down_con = mask_down & mask_down_shift
    series_down_streak_length = mask_down_con.rolling(20).apply(lambda x: count_continuous(x) * -1)
    series_down_streak_length = series_down_streak_length.mask(mask_down & series_down_streak_length.isna(), -1)

    series_streak_length = pandas.Series(0, index=quote.index)
    series_streak_length = series_streak_length.mask(series_up_streak_length.notna(), series_up_streak_length)
    series_streak_length = series_streak_length.mask(series_down_streak_length.notna(), series_down_streak_length)

    series_streak_length_rsi = rsi.rsi(series_streak_length, 2)

    # 3
    n = 100
    norm_rank = pandas.Series(bn.move_rank(quote.close, window=200, min_count=1), index=quote.index)
    denorm = (((norm_rank + 1) / 2) * (n - 1)) + 1
    # descend = (n - denorm) + 1
    # series_pct_rank = df.rolling(n).apply(lambda x: get_sort_value(x)/n)
    # series_pct_rank = descend
    series_pct_rank = denorm

    series_crsi = (series_rsi + series_streak_length_rsi + series_pct_rank) / 3

    return series_crsi
