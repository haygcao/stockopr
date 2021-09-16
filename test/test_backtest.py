# -*- coding: utf-8 -*-
import datetime
import unittest

from acquisition import basic
from backtest import backtest


class SelectorPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.code = '300550'  # vcp
        self.period = 'day'

        self.cash_start = 100000
        self.fromdate = datetime.datetime(2020, 8, 31)
        self.todate = datetime.datetime(2021, 12, 31)

    def tearDown(self):
        pass

    def test_backtest_one(self):
        code = '300502'
        code = '600888'
        # code = '300598'
        # code = '002739'

        r = backtest.backtest_one(self.cash_start, self.fromdate, self.todate, code)
        if not r:
            return
        code, cash = r
        percent = round((cash / self.cash_start - 1) * 100, 3)

        print(cash, percent)

    def test_show_graph(self):
        code = '600519'
        backtest.show_graph(code, self.fromdate, self.todate)

    def test_backtest(self):
        t1 = datetime.datetime.now()
        mp = False
        mp = True

        code_list = basic.get_all_stock_code()
        result = backtest.backtest(self.cash_start, self.fromdate, self.todate, code_list, mp=mp)

        t2 = datetime.datetime.now()
        print('backtest [{}] stocks, cost [{}]s'.format(len(code_list), (t2 - t1).seconds))

        backtest.print_profit(result, self.cash_start)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(SelectorPluginTestCase('test_second_stage'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
