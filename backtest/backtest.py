# -*- coding: utf-8 -*-
"""
pip install backtesting
cd venv/lib/python3.7/site-packages/backtesting/
find . -name "*.py" | xargs -i sed -i 's/Close/close/' {}
find . -name "*.py" | xargs -i sed -i 's/High/high/' {}
find . -name "*.py" | xargs -i sed -i 's/Low/low/' {}
find . -name "*.py" | xargs -i sed -i 's/Open/open/' {}
find . -name "*.py" | xargs -i sed -i 's/Volume/volume/' {}
"""

from acquisition import quote_db
from pointor import signal

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


class StockOpr(Strategy):
    def init(self):
        code = self.data.code[-1]
        quote = signal.compute_signal(code, 'day', self.data.df)
        self.signal_enter = quote.signal_enter.notna()
        self.signal_exit = quote.signal_exit.notna()

    def next(self):
        index = len(self.data.close) - 1
        if self.signal_enter[index]:
            self.buy()
        elif self.signal_enter[index]:
            self.sell()
        # else:
        #     print('no trade signal')


if __name__ == '__main__':
    code = '300502'
    period = 'day'
    count = 1000
    quote = quote_db.get_price_info_df_db(code, days=count, period_type='D')
    quote = quote[quote.open.notna()]

    # bt = Backtest(quote, SmaCross, cash=10000, commission=.002, exclusive_orders=True)
    bt = Backtest(quote, StockOpr, cash=10000, commission=.002, exclusive_orders=True)

    output = bt.run()
    print(output)
    bt.plot()
