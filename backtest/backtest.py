# -*- coding: utf-8 -*-
"""
pip install backtrader
ImportError: cannot import name 'warnings' from 'matplotlib.dates'
$ pip freeze | grep matplotlib
matplotlib==3.4.1

pip uninstall matplotlib
pip install matplotlib==3.2.2
但会导致其他问题

因为 warnings 属于标准库, 所以直接 import warnings, 问题解决
"""
import numpy
import pandas

from acquisition import quote_db
from pointor import signal

from datetime import datetime
import backtrader as bt


# https://community.backtrader.com/topic/158/how-to-feed-backtrader-alternative-data/8
class CustomDataLoader(bt.feeds.PandasData):
    lines = ('TOTAL_SCORE','Beta',)
    params = (('Open_Interest', None),
        ('TOTAL_SCORE',-1),
        ('Beta',-1)
    )

    datafields = bt.feeds.PandasData.datafields + (['TOTAL_SCORE', 'Beta'])


class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)


class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.order = None

    def notify(self, order):

        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)
        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.dataclose[-1]:
                # current close less than previous close
                if self.dataclose[-1] < self.dataclose[-2]:
                    # previous close less than the previous close
                    # BUY, BUY, BUY!!! (with default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
        else:
            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


class StockOprBackTrader(bt.Strategy):
    """
    尚未走通
    1 extract dataframe from pandas datafeed in backtrader
    2, column code is missing
    """
    def __bt_to_pandas__(self, btdata, len):
        get = lambda mydata: mydata.get(ago=0, size=len)

        fields = {
            'open': get(btdata.open),
            'high': get(btdata.high),
            'low': get(btdata.low),
            'close': get(btdata.close),
            'volume': get(btdata.volume)
        }
        time = [btdata.num2date(x) for x in get(btdata.datetime)]

        return pandas.DataFrame(data=fields, index=time)

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.order = None

        code = self.data.code[-1]
        quote = self.__bt_to_pandas__(self.datas[0], len(self))
        # code 如何获取
        quote = signal.compute_signal(code, 'day', quote)
        self.signal_enter = quote.signal_enter.notna()
        self.signal_exit = quote.signal_exit.notna()

    def notify(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)
        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        index = len(self.dataclose) - 1
        if self.signal_enter[index]:
            self.order = self.buy()
        elif self.signal_enter[index]:
            self.order = self.sell()

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.dataclose[-1]:
                # current close less than previous close
                if self.dataclose[-1] < self.dataclose[-2]:
                    # previous close less than the previous close
                    # BUY, BUY, BUY!!! (with default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
        else:
            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


if __name__ == '__main__':
    code = '300502'
    period = 'day'
    count = 1000
    quote = quote_db.get_price_info_df_db(code, days=count, period_type='D')
    quote = quote[quote.open.notna()]

    cerebro = bt.Cerebro()
    # cerebro.addstrategy(SmaCrossBackTrader)
    # cerebro.addstrategy(TestStrategyBackTrader)
    # cerebro.addstrategy(StockOprBackTrader)

    # data0 = bt.feeds.YahooFinanceData(dataname='MSFT', fromdate=datetime(2011, 1, 1), todate=datetime(2012, 12, 31))
    data0 = bt.feeds.PandasData(dataname=quote, fromdate=datetime(2020, 1, 1), todate=datetime(2021, 12, 31))
    cerebro.adddata(data0)

    quote = signal.compute_signal(code, 'day', quote)
    signals = quote.signal_enter.mask(quote.signal_enter.notna(), 1)
    signals = signals.mask(quote.signal_exit.notna(), -1)
    # signals = signals.fillna(0)
    signals = signals[signals.notna()]
    closes = quote.close[quote.index.isin(signals.index)]

    # t - numpy.datetime64
    # t1 = t.astype(datetime)   # 1629763200000000000
    # t2 = numpy.datetime_as_string(t, unit='D')   # 2021-08-24
    # t3 = str(t)   # 2021-08-24T00:00:00.000000000

    orders = zip([numpy.datetime_as_string(t, unit='D') for t in signals.index.values], signals.values,
                 closes.values)

    cerebro.add_order_history(orders, notify=True)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    cerebro.run()
    cerebro.plot()
