import datetime
import threading
import time

from acquisition import tx, quote_db
from indicator import trend_strength, ema
from util import dt
from chart.base import LIGHT_GREY_COLOR, GREY_COLOR, BLUE_COLOR
from chart.item import CurveItem
from chart.app import create_qapp, QtCore
from chart import ChartWidget, VolumeItem, CandleItem


if __name__ == "__main__":
    app = create_qapp()

    code = '002739'
    period = 'day'

    quote = quote_db.get_price_info_df_db_day('002739')
    # quote = tx.get_kline_data_sina(code, period)
    quote = trend_strength.compute_trend_strength(quote, period)
    quote = ema.compute_ema(quote)

    widget = ChartWidget()
    widget.setBackground(LIGHT_GREY_COLOR)

    widget.add_plot("candle", hide_x_axis=True)
    widget.add_plot("volume", maximum_height=200)
    widget.add_plot("strength", maximum_height=200)
    widget.add_item("candle", "candle", CandleItem)
    widget.add_item("candle", "ema12", CurveItem, ind="ema", col="ema12", color=GREY_COLOR)
    widget.add_item("candle", "ema26", CurveItem, ind="ema", col="ema26", color=BLUE_COLOR)
    widget.add_item("volume", "volume", VolumeItem, ind="volume", col="volume", color=GREY_COLOR)
    widget.add_item("strength", "strength", CurveItem, ind="trend_strength", col="trend_strength", color=BLUE_COLOR)
    quote['const_h0'] = 0
    quote['const_h50'] = 50
    quote['const_h-50'] = -50
    widget.add_item("strength", "strength1", CurveItem, ind="trend_strength", col="const_h0", color=GREY_COLOR)
    widget.add_item("strength", "strength2", CurveItem, ind="trend_strength", col="const_h50", color=GREY_COLOR)
    widget.add_item("strength", "strength3", CurveItem, ind="trend_strength", col="const_h-50", color=GREY_COLOR)
    widget.add_cursor()

    # plt = widget.get_plot('volume')
    # cu_item = Cu(quote, ['trend_strength'])
    # plt.addItem(cu_item)

    n = len(quote) - 10
    history = quote.iloc[:n]
    new_data = quote.iloc[n:]

    widget.update_history(history)

    ind_update = 0


    def update_bar():
        global ind_update
        if len(new_data) == ind_update:
            return
        bar = new_data.iloc[ind_update]
        ind_update += 1
        # new_data.drop(new_data.index[0], inplace=True)
        # bar.name = bar.name - datetime.timedelta(days=ind_update)
        widget.update_bar(bar)


    timer = QtCore.QTimer()
    timer.timeout.connect(update_bar)
    timer.start(1 * 1000)

    def update_rt_bar():
        global quote
        while dt.istradetime():
            now = datetime.datetime.now()
            if now.hour == 12 or (now.hour == 11 and now.minute >= 30):
                time.sleep(30)
                continue

            if now.minute % 5 != 4:
                time.sleep(30)
                continue

            quote_new = tx.get_kline_data_sina(code, period)
            quote_new = trend_strength.compute_trend_strength(quote_new, period)
            quote_diff = quote_new[quote_new.index >= quote.index[-1]]
            for trade_time, bar in quote_diff.iterrows():
                widget.update_bar(bar)
            quote = quote_new
            time.sleep(4 * 60)

    t = threading.Thread(target=update_rt_bar, args=())
    # t.start()

    widget.show()
    app.exec_()
