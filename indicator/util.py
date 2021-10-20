# -*- encoding: utf-8 -*-
from config import config


def adjust(df, prices):
    return df

    # n = len(df)
    low = pd.rolling_min(prices['low'], 1)
    fillval = low[-1]
    low.fillna(fillval, inplace=True)
    # low = pd.expanding_min(prices['low'], 5)
    price = prices['close'][-1]
    # pandas 太霸气了 这样运算都可以
    return df / (price - low) * 100 # 换算成比例(涨跌幅度)
    # return (df - low) / (price - low) * 100 # 换算成比例(涨跌幅度)
    # return (df) / (price) * 100 # 换算成比例(涨跌幅度)


def resample_long_to_short(quote_week, quote, long, short_period, column='dyn_sys'):
    period_type_reverse = config.period_map[short_period]['period']

    quote_short_period = quote_week.resample(period_type_reverse).last()
    quote_short_period[column] = quote_week[column].resample(period_type_reverse).pad()
    # print(quote_short_period[-50:])

    # 补齐最后一天的数据
    if short_period in ['m30', 'm5', 'm1']:
        last_row_index = quote_short_period.index[-1]
        pd_loss = quote[last_row_index:]
        quote_short_period = quote_short_period.append(pd_loss, )

        # quote_short_period = quote_short_period.unique()
        # indexs = quote_short_period.index.drop_duplicates()
        # quote_short_period = quote_short_period[quote_short_period.index.isin(indexs)]
        # https://stackoverflow.com/questions/22918212/fastest-way-to-drop-duplicated-index-in-a-pandas-dataframe
        # quote_short_period = quote_short_period.groupby(quote_short_period.index).first()
        quote_short_period = quote_short_period[~quote_short_period.index.duplicated(keep='first')]

        quote_short_period.loc[last_row_index:, column] = quote_short_period.loc[last_row_index][column]

    quote_short_period = quote_short_period[quote_short_period.index.isin(quote.index)]
    return quote_short_period
