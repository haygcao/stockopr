# -*- encoding: utf-8 -*-


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
