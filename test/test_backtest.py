# -*- coding: utf-8 -*-
import datetime
import json
import os
import unittest

from acquisition import basic
from backtest import backtest
from util import util


class BackTestPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.code = '300550'  # vcp
        self.period = 'day'

        self.cash_start = 1000000   # 100W
        self.fromdate = datetime.datetime(2019, 1, 1)
        self.todate = datetime.datetime(2021, 12, 31)

    def tearDown(self):
        pass

    def test_backtest_one(self):
        code = '600199'

        r = backtest.backtest_one(self.cash_start, self.fromdate, self.todate, code)
        if not r:
            return
        code, cash = r
        percent = round((cash / self.cash_start - 1) * 100, 3)

        print(cash, percent)

    def test_show_graph(self):
        code = '300502'
        backtest.show_graph(self.cash_start, self.fromdate, self.todate, code)

    def test_analyse(self):
        cache_path = util.get_cache_dir()
        cache = os.path.join(cache_path, 'backtest_20211012_104712.json')
        with open(cache) as f:
            result = json.load(f)
            backtest.print_profit(result, self.cash_start)

    def test_backtest(self):
        t1 = datetime.datetime.now()
        mp = False
        mp = True

        code_list = basic.get_all_stock_code()
        # code_list = code_list[:100]
        result = backtest.backtest(self.cash_start, self.fromdate, self.todate, code_list, mp=mp)

        t2 = datetime.datetime.now()
        print('backtest [{}] stocks, cost [{}]s'.format(len(code_list), (t2 - t1).seconds))

        backtest.print_profit(result, self.cash_start)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(BackTestPluginTestCase('test_backtest'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
