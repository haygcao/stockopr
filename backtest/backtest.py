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

功能需要支持, 最终盈亏topN, 最大收益/最大回辙
"""
import functools
import json
import multiprocessing
import os

import numpy
import pandas
import tqdm

from util import util
from selector import util as selector_util
from acquisition import quote_db
from pointor import signal

import datetime
import backtrader as bt


# https://community.backtrader.com/topic/158/how-to-feed-backtrader-alternative-data/8
from util.log import logger


class CustomDataLoader(bt.feeds.PandasData):
    lines = ('TOTAL_SCORE', 'Beta',)
    params = (('Open_Interest', None), ('TOTAL_SCORE', -1), ('Beta', -1))

    datafields = bt.feeds.PandasData.datafields + (['TOTAL_SCORE', 'Beta'])


class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)


class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime.date(0)
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
        time = [btdata.num2date(x) for x in get(btdata.datetime.datetime)]

        return pandas.DataFrame(data=fields, index=time)

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime.date(0)
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


def _backtest_one(cash, fromdate, todate, code):
    period = 'day'
    days = (todate - fromdate).days + 250

    quote = quote_db.get_price_info_df_db(code, days=days, period_type='D')
    if selector_util.filter_quote(quote):
        return
    quote = quote[quote.open.notna()]

    cerebro = bt.Cerebro()
    # cerebro.addstrategy(SmaCrossBackTrader)
    # cerebro.addstrategy(TestStrategyBackTrader)
    # cerebro.addstrategy(StockOprBackTrader)

    # data0 = bt.feeds.YahooFinanceData(dataname='MSFT', fromdate=fromdate, todate=todate)
    data0 = bt.feeds.PandasData(dataname=quote, fromdate=fromdate, todate=todate)
    cerebro.adddata(data0)
    quote = signal.compute_signal(code, period, quote)
    quote = quote.loc[fromdate:todate]
    open_position_date = quote.signal_enter.first_valid_index()
    if open_position_date is None:
        return

    mask_buy = quote.signal_enter.notna()
    mask_sell = quote.signal_exit.notna()
    mask_sell = mask_sell.mask(mask_sell.index <= open_position_date, False)

    size_buy = cash / 2 / quote.close[mask_buy] // 100 * 100
    if numpy.count_nonzero(size_buy <= 0) > 0:
        print('{} - could not buy 100'.format(code))
        return
    signals = quote.signal_enter.mask(mask_buy, size_buy)

    size_sell_list = (-size_buy).to_list()
    # numpy.nan/0/False 都不是 nonzero
    diff = numpy.count_nonzero(mask_buy) - numpy.count_nonzero(mask_sell)
    for i in range(diff):
        size_sell_list.pop()

    if size_sell_list:
        size_sell = pandas.Series(size_sell_list, index=(mask_sell[mask_sell]).index)
        signals = signals.mask(mask_sell, size_sell)
    # signals = signals.fillna(0)
    signals = signals[signals.notna()]
    signals = signals if signals.iloc[0] > 0 else signals.iloc[1:]

    closes = quote.close[quote.index.isin(signals.index)]

    # t - numpy.datetime.datetime64
    # t1 = t.astype(datetime.datetime)   # 1629763200000000000
    # t2 = numpy.datetime.datetime_as_string(t, unit='D')   # 2021-08-24
    # t3 = str(t)   # 2021-08-24T00:00:00.000000000
    orders = zip([numpy.datetime_as_string(t, unit='D') for t in signals.index.values], signals.values,
                 closes.values)
    orders = [(a, b, c) for a, b, c in orders]
    cerebro.add_order_history(orders, notify=True)
    # Set our desired cash start
    cerebro.broker.setcash(cash)

    cerebro.run()

    return cerebro


def backtest_one(cash, fromdate, todate, code):
    # cerebro.plot()
    cerebro = _backtest_one(cash, fromdate, todate, code)
    if not cerebro:
        return

    broker = cerebro.broker
    # cash = broker.getcash()   # 现金
    value = broker.getvalue()   # 总资产
    # position = broker.getposition(data0)   # 持仓 position.adjbase 现价 position.price 成本价
    # positions = [p for k, p in broker.positions.items() if isinstance(k, backtrader.feeds.pandafeed.PandasData)]
    # position = positions[0] if positions else None
    # assert len(positions) <= 1   # 不曾有过持仓时, positions 为空, 比如, 本金不够买一手贵州茅台

    # 回测采用半仓交易
    percent = round((value - broker.startingcash) / (broker.startingcash / 2), 3)

    cash = int(broker.startingcash * (1 + percent))

    return code, cash


def show_graph(cash, fromdate, todate, code):
    cerebro = _backtest_one(cash, fromdate, todate, code)
    if not cerebro:
        return

    cerebro.plot()


def backtest_single(cash_start, fromdate, todate, code_list):
    result = {}
    for code in code_list:
        code_cash = backtest_one(cash_start, fromdate, todate, code)
        if not code_cash:
            continue
        print(code_cash)
        result.update({code_cash[0]: code_cash[1]})

    return result


def backtest_mp(cash_start, fromdate, todate, code_list):
    backtest_func = functools.partial(backtest_one, cash_start, fromdate, todate)

    result = {}
    nproc = multiprocessing.cpu_count()
    with multiprocessing.Pool(nproc) as p:
        for code_cash in tqdm.tqdm(p.imap_unordered(backtest_func, code_list), total=len(code_list), ncols=64):
            if not code_cash:
                continue
            result.update({code_cash[0]: code_cash[1]})

    return result


def backtest(cash_start, fromdate, todate, code_list, mp=True):
    t1 = datetime.datetime.now()
    if mp:
        result = backtest_mp(cash_start, fromdate, todate, code_list)
    else:
        result = backtest_single(cash_start, fromdate, todate, code_list)

    t2 = datetime.datetime.now()
    logger.info('backtest [{}] stocks, cost [{}]s'.format(len(code_list), (t2 - t1).seconds))

    cache_path = util.get_cache_dir()
    cache = os.path.join(cache_path, 'backtest_{}.json'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
    with open(cache, 'w') as f:
        json.dump(result, f)
        
    return result


def print_profit(result, cash_start):
    l = list(result.items())
    np_result = pandas.Series([i[1] for i in l], index=[i[0] for i in l])
    np_result = np_result.sort_values()
    cashs = list(result.values())
    cashs.sort()
    cash_final = sum(result.values())
    cash_start_final = cash_start * len(result)
    profit = cash_final - cash_start_final
    percent = round(profit / cash_start_final * 100, 3)
    print('cash_start: {}\ncash: {}\nprofit: {}[{}%]'.format(cash_start_final, cash_final, profit, percent))
    print('up: {}\ndown: {}'.format(
        list(map(lambda x: x > cash_start, cashs)).count(True),
        list(map(lambda x: x < cash_start, cashs)).count(True)))
    top_earn = cashs[-50:]
    top_earn.sort(reverse=True)
    top_loss = cashs[:50]
    print('top_earn: {}\ntop_loss: {}'.format(
        list(map(lambda x: round((x/cash_start - 1) * 100, 3), top_earn)),
        list(map(lambda x: round((x/cash_start - 1) * 100, 3), top_loss))))


if __name__ == '__main__':
    code = '300502'
    code = '600888'
    # code = '300598'
    # code = '002739'

    cash_start = 100000

    fromdate = datetime.datetime(2020, 8, 31)
    todate = datetime.datetime(2021, 12, 31)

    cash = backtest_one(cash_start, fromdate, todate, code)
    percent = round((cash / cash_start - 1) * 100, 3)

    print(cash, percent)

