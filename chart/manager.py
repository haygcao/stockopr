from enum import Enum
from typing import Dict, Tuple
from datetime import datetime

import pandas

from .base import to_int


class Pos(Enum):
    MAJOR = 0
    MAJOR_REPLACE = 1
    MINOR = 2


class BarManager:
    """"""

    def __init__(self):
        """"""
        self._bars: pandas.DataFrame = pandas.DataFrame()
        # indicator: column_names, e.g. macd: ['macd_line', 'macd_signal', 'macd_hist']
        self._indicator_dict = {
            # 'price': {'main_plot': Pos.MAJOR, 'cols': ['open', 'high', 'low', 'close']},
            'volume': {'main_plot': Pos.MINOR, 'cols': ['volume']},
            'ema': {'main_plot': Pos.MAJOR, 'cols': ['ema12', 'ema26']},
            'trend_strength': {'main_plot': Pos.MINOR, 'cols': ['trend_strength']},
            'macd': {'main_plot': Pos.MINOR, 'cols': ['macd_line', 'macd_signal', 'macd_hist']}
        }

        self._ix_list = []
        self._dt_list = []
        self._datetime_index_map: Dict[datetime, int] = {}
        self._index_datetime_map: Dict[int, datetime] = {}

        self._price_ranges: Dict[Tuple[int, int], Tuple[float, float]] = {}
        self._volume_ranges: Dict[Tuple[int, int], Tuple[float, float]] = {}
        self._ranges: Dict[str, Dict[Tuple[int, int], Tuple[float, float]]] = {}

    def update_history(self, history: pandas.DataFrame) -> None:
        """
        Update a list of bar data.
        """
        # Put all new bars into dict
        self._bars = history

        # Sort bars dict according to bar.datetime
        # self._bars.sort_index(inplace=True)

        # Update map relationiship
        self._ix_list = list(range(len(self._bars)))
        self._dt_list = list(self._bars.index.to_list())

        self._datetime_index_map = dict(zip(self._dt_list, self._ix_list))
        self._index_datetime_map = dict(zip(self._ix_list, self._dt_list))

        # Clear data range cache
        self._clear_cache()

    def update_bar(self, bar: pandas.Series) -> None:
        """
        Update one single bar data.
        """
        dt = bar.name

        if dt not in self._datetime_index_map:
            ix = len(self._bars)
            self._ix_list.append(ix)
            self._dt_list.append(dt)
            self._datetime_index_map[dt] = ix
            self._index_datetime_map[ix] = dt

            self._bars = self._bars.append(bar)
        else:
            self._bars.at[dt] = bar

        self._clear_cache()

    def get_count(self) -> int:
        """
        Get total number of bars.
        """
        return len(self._bars)

    def get_index(self, dt: datetime) -> int:
        """
        Get index with datetime.
        """
        return self._datetime_index_map.get(dt, None)

    def get_prev_index(self, ix: float):
        ix = to_int(ix)
        index = self._ix_list.index(ix)
        if index == 0:
            ix_prev = ix
        else:
            ix_prev = self._ix_list[index - 1]
        return ix_prev

    def get_datetime(self, ix: float) -> datetime:
        """
        Get datetime with index.
        """
        ix = to_int(ix)
        return self._index_datetime_map.get(ix, None)

    def get_bar(self, ix: float) -> pandas.Series:
        """
        Get bar data with index.
        """
        ix = to_int(ix)
        dt = self._index_datetime_map.get(ix, None)
        if not dt:
            return None

        return self._bars.loc[dt]

    def get_prev_bar(self, ix: float) -> pandas.Series:
        """
        Get bar data with index.
        """
        ix = to_int(ix)
        index = self._ix_list.index(ix)
        if index == 0:
            ix_prev = ix
        else:
            ix_prev = self._ix_list[index - 1]
        dt = self._index_datetime_map.get(ix_prev, None)
        if not dt:
            return None

        return self._bars[dt]

    def get_all_bars(self) -> pandas.DataFrame:
        """
        Get all bar data.
        """
        return self._bars

    def get_price_range(self, min_ix: float = None, max_ix: float = None, ignore_ind: bool = False) -> Tuple[float, float]:
        """
        Get price range to show within given index range.
        """
        if self._bars.empty:
            return 0, 1

        if not min_ix:
            min_ix = 0
            max_ix = len(self._bars) - 1
        else:
            min_ix = to_int(min_ix)
            max_ix = to_int(max_ix)
            max_ix = min(max_ix, self.get_count())

        buf = self._price_ranges.get((min_ix, max_ix), None)
        if buf:
            return buf

        bar_list = self._bars.iloc[min_ix:max_ix + 1]
        first_bar = bar_list.iloc[0]
        max_price = first_bar.high
        min_price = first_bar.low

        for dates, bar in bar_list.iloc[1:].iterrows():
            max_price = max(max_price, bar.high)
            min_price = min(min_price, bar.low)

        if ignore_ind:
            self._price_ranges[(min_ix, max_ix)] = (min_price, max_price)
            return min_price, max_price

        for ind, ind_info in self._indicator_dict.items():
            if ind_info['main_plot'] == Pos.MAJOR:
                min_, max_ = self.get_ind_range(ind, min_ix, max_ix, ignore_major=True)
                min_price = min(min_price, min_)
                max_price = max(max_price, max_)

        self._price_ranges[(min_ix, max_ix)] = (min_price, max_price)
        return min_price, max_price

    def get_volume_range(self, min_ix: float = None, max_ix: float = None) -> Tuple[float, float]:
        """
        Get volume range to show within given index range.
        """
        if self._bars.empty:
            return 0, 1

        if not min_ix:
            min_ix = 0
            max_ix = len(self._bars) - 1
        else:
            min_ix = to_int(min_ix)
            max_ix = to_int(max_ix)
            max_ix = min(max_ix, self.get_count())

        buf = self._volume_ranges.get((min_ix, max_ix), None)
        if buf:
            return buf

        bar_list = self._bars.iloc[min_ix:max_ix + 1]

        first_bar = bar_list.iloc[0]
        max_volume = first_bar.volume
        min_volume = 0

        for dates, bar in bar_list.iloc[1:].iterrows():
            max_volume = max(max_volume, bar.volume)

        self._volume_ranges[(min_ix, max_ix)] = (min_volume, max_volume)
        return min_volume, max_volume

    def get_ind_range(self, ind: str, min_ix: float = None, max_ix: float = None, ignore_major=False)\
            -> Tuple[float, float]:
        """
        Get volume range to show within given index range.
        """
        if self._bars.empty:
            return 0, 1

        ind_info = self._indicator_dict.get(ind)
        if not ignore_major and ind_info['main_plot'] == Pos.MAJOR:
            min_price, max_price = self.get_price_range(min_ix, max_ix)
            return min_price, max_price

        if not min_ix:
            min_ix = 0
            max_ix = len(self._bars) - 1
        else:
            min_ix = to_int(min_ix)
            max_ix = to_int(max_ix)
            max_ix = min(max_ix, self.get_count())

        ind_dict = self._ranges.get(ind)
        if ind_dict:
            buf = ind_dict.get((min_ix, max_ix), None)
            if buf:
                return buf
        else:
            self._ranges.update({ind: {}})

        bar_list = self._bars.iloc[min_ix:max_ix + 1]

        min_ = None
        max_ = None
        cols = ind_info.get('cols')
        for col in cols:
            col_max_ = bar_list[col].max()
            col_min_ = bar_list[col].min()

            min_ = col_min_ if min_ is None else min(min_, col_min_)
            max_ = col_max_ if max_ is None else max(max_, col_max_)

        self._ranges[ind][(min_ix, max_ix)] = (min_, max_)
        return min_, max_

    def _clear_cache(self) -> None:
        """
        Clear cached range data.
        """
        self._price_ranges.clear()
        self._volume_ranges.clear()
        self._ranges.clear()

    def clear_all(self) -> None:
        """
        Clear all data in manager.
        """
        self._bars.clear()
        self._ix_list.clear()
        self._dt_list.clear()
        self._datetime_index_map.clear()
        self._index_datetime_map.clear()

        self._clear_cache()
