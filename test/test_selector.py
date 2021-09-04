import datetime
import unittest

from acquisition import quote_db, basic
from selector import selector
from selector.plugin.base_breakout import base_breakout
from selector.plugin.blt import blt
from selector.plugin.second_stage import second_stage
from selector.plugin.super import super
from selector.plugin.vcp import vcp
from util import dt


class SelectorPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.code = '600331'  # vcp
        self.period = 'day'
        count = 1000
        self.quote = quote_db.get_price_info_df_db(self.code, days=count, period_type='D')

    def tearDown(self):
        pass

    def test_second_stage(self):
        ret = second_stage(self.quote)
        print(ret)

    def test_super(self):
        ret = super(self.quote)
        print(ret)

    def test_strong_breakout(self):
        ret = base_breakout(self.quote)
        print(ret)

    def test_blt(self):
        ret = blt(self.quote, self.period)
        print(ret)

    def test_vcp(self):
        ret = vcp(self.quote, self.period)
        print(ret)

    def test_update_candidate_pool(self):
        selector.update_candidate_pool(['super'], 'day')

    def test_get_candidate_pool(self):
        code_list = basic.get_candidate_stock_code(['second_stage'])
        print(code_list)

    def test_select(self):
        code_list = selector.select(['ema_value'], None, ['super'])
        print(code_list)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(SelectorPluginTestCase('test_second_stage'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
