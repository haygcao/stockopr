from datetime import datetime

from vnpy.chart.item import CurveItem
from vnpy.trader.ui import create_qapp, QtCore
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader import database
from vnpy.chart import ChartWidget, VolumeItem, CandleItem


if __name__ == "__main__":
    app = create_qapp()

    bars = database.load_bar_data(
        "002739",
        Exchange.CFFEX,
        interval=Interval.MINUTE,
        start=datetime(2019, 7, 1),
        end=datetime(2019, 7, 17)
    )

    widget = ChartWidget()
    widget.add_plot("candle", hide_x_axis=True)
    widget.add_plot("volume", maximum_height=200)
    widget.add_item(CandleItem, "candle", "candle")
    # widget.add_item(VolumeItem, "volume", "volume")
    widget.add_item(CurveItem, "volume", "volume")
    widget.add_cursor()

    n = 100
    history = bars[:n]
    new_data = bars[n:]

    widget.update_history(history)

    def update_bar():
        if len(new_data) == 0:
            return
        bar = new_data.pop(0)
        widget.update_bar(bar)

    timer = QtCore.QTimer()
    timer.timeout.connect(update_bar)
    timer.start(3 * 1000)

    widget.show()
    app.exec_()
