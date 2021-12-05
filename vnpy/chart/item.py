from abc import abstractmethod
from typing import List, Dict, Tuple

import pandas
import pyqtgraph as pg
from PyQt5.QtGui import QPainterPath

from vnpy.trader.ui import QtCore, QtGui, QtWidgets

from .base import BLACK_COLOR, UP_COLOR, DOWN_COLOR, PEN_WIDTH, BAR_WIDTH, LIGHT_GREY_COLOR
from .manager import BarManager


class ChartItem(pg.GraphicsObject):
    """"""

    def __init__(self, manager: BarManager):
        """"""
        super().__init__()

        self._manager: BarManager = manager

        self._bar_picutures: Dict[int, QtGui.QPicture] = {}
        self._item_picuture: QtGui.QPicture = None

        self._black_brush: QtGui.QBrush = pg.mkBrush(color=LIGHT_GREY_COLOR)  # BLACK_COLOR)

        self._up_pen: QtGui.QPen = pg.mkPen(
            color=UP_COLOR, width=PEN_WIDTH
        )
        self._up_brush: QtGui.QBrush = pg.mkBrush(color=UP_COLOR)

        self._down_pen: QtGui.QPen = pg.mkPen(
            color=DOWN_COLOR, width=PEN_WIDTH
        )
        self._down_brush: QtGui.QBrush = pg.mkBrush(color=DOWN_COLOR)

        self._rect_area: Tuple[float, float] = None

        # Very important! Only redraw the visible part and improve speed a lot.
        self.setFlag(self.ItemUsesExtendedStyleOption)

    @abstractmethod
    def _draw_bar_picture(self, ix: int, bar: pandas.Series) -> QtGui.QPicture:
        """
        Draw picture for specific bar.
        """
        pass

    @abstractmethod
    def boundingRect(self) -> QtCore.QRectF:
        """
        Get bounding rectangles for item.
        """
        pass

    @abstractmethod
    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        pass

    @abstractmethod
    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        pass

    def update_history(self, history: pandas.DataFrame) -> pandas.Series:
        """
        Update a list of bar data.
        """
        self._bar_picutures.clear()

        bars = self._manager.get_all_bars()
        for ix in range(len(bars)):
            self._bar_picutures[ix] = None

        self.update()

    def update_bar(self, bar: pandas.Series) -> pandas.Series:
        """
        Update single bar data.
        """
        ix = self._manager.get_index(bar.name)

        self._bar_picutures[ix] = None

        self.update()

    def update(self) -> None:
        """
        Refresh the item.
        """
        if self.scene():
            self.scene().update()

    def paint(
        self,
        painter: QtGui.QPainter,
        opt: QtWidgets.QStyleOptionGraphicsItem,
        w: QtWidgets.QWidget
    ):
        """
        Reimplement the paint method of parent class.

        This function is called by external QGraphicsView.
        """
        rect = opt.exposedRect

        min_ix = int(rect.left())
        max_ix = int(rect.right())
        max_ix = min(max_ix, len(self._bar_picutures))

        rect_area = (min_ix, max_ix)
        if rect_area != self._rect_area or not self._item_picuture:
            self._rect_area = rect_area
            self._draw_item_picture(min_ix, max_ix)

        self._item_picuture.play(painter)

    def _draw_item_picture(self, min_ix: int, max_ix: int) -> None:
        """
        Draw the picture of item in specific range.
        """
        self._item_picuture = QtGui.QPicture()
        painter = QtGui.QPainter(self._item_picuture)

        for ix in range(min_ix, max_ix):
            bar_picture = self._bar_picutures[ix]

            if bar_picture is None:
                bar = self._manager.get_bar(ix)
                bar_picture = self._draw_bar_picture(ix, bar)
                self._bar_picutures[ix] = bar_picture

            bar_picture.play(painter)

        painter.end()

    def clear_all(self) -> None:
        """
        Clear all data in the item.
        """
        self._item_picuture = None
        self._bar_picutures.clear()
        self.update()


class CandleItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager):
        """"""
        super().__init__(manager)

    def _draw_bar_picture(self, ix: int, bar: pandas.Series) -> QtGui.QPicture:
        """"""
        # Create objects
        candle_picture = QtGui.QPicture()
        painter = QtGui.QPainter(candle_picture)

        # Set painter color
        if bar.close >= bar.open:
            painter.setPen(self._up_pen)
            painter.setBrush(self._black_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw candle shadow
        if bar.high > bar.low:
            painter.drawLine(
                QtCore.QPointF(ix, bar.high),
                QtCore.QPointF(ix, bar.low)
            )

        # Draw candle body
        if bar.open == bar.close:
            painter.drawLine(
                QtCore.QPointF(ix - BAR_WIDTH, bar.open),
                QtCore.QPointF(ix + BAR_WIDTH, bar.open),
            )
        else:
            rect = QtCore.QRectF(
                ix - BAR_WIDTH,
                bar.open,
                BAR_WIDTH * 2,
                bar.close - bar.open
            )
            painter.drawRect(rect)

        # Finish
        painter.end()
        return candle_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_price, max_price = self._manager.get_price_range()
        rect = QtCore.QRectF(
            0,
            min_price,
            len(self._bar_picutures),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self._manager.get_bar(ix)

        if isinstance(bar, pandas.Series) and not bar.empty:
            words = [
                "Date",
                bar.name.strftime("%Y-%m-%d"),
                "",
                "Time",
                bar.name.strftime("%H:%M"),
                "",
                "Open",
                str(bar.open),
                "",
                "High",
                str(bar.high),
                "",
                "Low",
                str(bar.low),
                "",
                "Close",
                str(bar.close)
            ]
            text = "\n".join(words)
        else:
            text = ""

        return text


class VolumeItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager, ind: str, col: str, color: str):
        """"""
        super().__init__(manager)
        self.ind = ind
        self.col = col

    def _draw_bar_picture(self, ix: int, bar: pandas.Series) -> QtGui.QPicture:
        """"""
        # Create objects
        volume_picture = QtGui.QPicture()
        painter = QtGui.QPainter(volume_picture)

        # Set painter color
        if bar.close >= bar.open:
            painter.setPen(self._up_pen)
            painter.setBrush(self._black_brush)  # _up_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw volume body
        rect = QtCore.QRectF(
            ix - BAR_WIDTH,
            0,
            BAR_WIDTH * 2,
            bar.volume
        )
        painter.drawRect(rect)

        # Finish
        painter.end()
        return volume_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_volume, max_volume = self._manager.get_volume_range()
        rect = QtCore.QRectF(
            0,
            min_volume,
            len(self._bar_picutures),
            max_volume - min_volume
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_volume, max_volume = self._manager.get_volume_range(min_ix, max_ix)
        return min_volume, max_volume

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self._manager.get_bar(ix)

        if isinstance(bar, pandas.Series) and not bar.empty:
            text = f"Volume {bar.volume}"
        else:
            text = ""

        return text


class CurveItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager, ind: str, col: str, color: Tuple[int, int, int]):
        """"""
        super().__init__(manager)
        self.ind = ind
        self.col = col
        self.style = 'curve'
        self.width = 1
        self.color = color

    def _draw_bar_picture(self, ix: int, bar: pandas.Series) -> QtGui.QPicture:
        """"""
        # Create objects
        curve_picture = QtGui.QPicture()
        painter = QtGui.QPainter(curve_picture)

        ix_prev = self._manager.get_prev_index(ix)
        bar_prev = self._manager.get_bar(ix_prev)

        # Set painter color
        pen = QtGui.QPen = pg.mkPen(color=self.color, width=self.width)
        brush = pg.mkBrush(color=self.color)
        painter.setPen(pen)
        painter.setBrush(brush)

        # Draw curve body
        path = QPainterPath()
        path.moveTo(ix_prev, bar_prev[self.col])
        # path.cubicTo(30, 30, 200, 350, 350, 30)
        path.lineTo(ix, bar[self.col])
        # path.moveTo(ix, bar.close)

        painter.drawPath(path)

        # Finish
        painter.end()
        return curve_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_curve, max_curve = self._manager.get_ind_range(self.ind)
        rect = QtCore.QRectF(
            0,
            min_curve,
            len(self._bar_picutures),
            max_curve - min_curve
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_curve, max_curve = self._manager.get_ind_range(self.ind, min_ix, max_ix)
        return min_curve, max_curve

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self._manager.get_bar(ix)
        if isinstance(bar, pandas.Series) and not bar.empty:
            text = f"{self.col} {round(bar[self.col], 2)}"
        else:
            text = ""

        return text
