from datetime import datetime
from typing import List

from .constant import Exchange, Interval
from .object import BarData


def load_bar_data(
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
) -> List[BarData]:
    """
    Load bar data from database.
    """
    from acquisition import quote_db
    quote = quote_db.get_price_info_df_db_day(symbol, 250)  # , end)

    bars = []
    for dates, row in quote.iterrows():
        open, high, low, close = row[1:5]
        vol = row['volume']
        turnover = row['amount']
        bar = BarData('', symbol, exchange, dates, interval, vol, turnover, 0, open, high, low, close)
        bars.append(bar)

    return bars
