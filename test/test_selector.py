import datetime
import unittest

import pandas

from acquisition import quote_db, basic
from selector import selector
from selector.plugin import fund, volume_dry_up
from selector.plugin.base_breakout import base_breakout
from selector.plugin.blt import blt
from selector.plugin.second_stage import second_stage
from selector.plugin.step import step
from selector.plugin.super import super
from selector.plugin.vcp import vcp


class SelectorPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.code = '300598'  # vcp
        self.period = 'day'
        count = 1000
        self.quote = quote_db.get_price_info_df_db(self.code, days=count, period_type='D')

    def tearDown(self):
        pass

    def test_query_fund(self):
        df = fund.query_fund()
        print(df)

    def test_query_funds(self):
        fund_date = datetime.date(2021, 6, 30)
        fund_name = '能源'
        df = fund.query_funds(fund_date, fund_name)
        print(df)

    def test_query_stocks_fund_theme_specified(self):
        fund_date = datetime.date(2021, 6, 30)
        fund_name = '能源'
        df = fund.query_stocks_fund_theme_specified(fund_date, fund_name)
        df = fund.supplement_percent(df)
        print(df)

    def test_query_fund_stat(self):
        fund_date = datetime.date(2021, 6, 30)
        r = fund.query_fund_stat(fund_date)
        print(r)

    def test_query_stocks(self):
        fund_date = '2021-06-30'
        df = fund.query_stocks(fund_date)
        print(df)

    def test_query_stocks_fund_market_value_diff(self):
        fund_date_prev = '2021-03-31'
        fund_date_next = '2021-06-30'
        df_diff = fund.query_stocks_fund_market_value_diff(fund_date_prev, fund_date_next)
        df_diff = fund.supplement_percent(df_diff)
        print(df_diff)

    def test_query_stocks_percent(self):
        code_list = ['002739', '300502']
        df = fund.query_stocks_percent(code_list)
        print(df)

    def test_query_stock(self):
        fund_date = fund.query_latest_date()  # '2021-06-30'
        code = '600519'
        df = fund.query_one_stock_lite(code, fund_date)
        df1 = fund.query_stock(code, fund_date)
        fmvp = df1.fmv.sum() / df1.nmc[-1]

        intersection = df.index.intersection(df1.index)
        print(df.index[~df.index.isin(intersection)])
        print(df1.index[~df1.index.isin(intersection)])

    def test_second_stage(self):
        ret = second_stage(self.quote, self.period)
        print(ret)

    def test_super(self):
        ret = super(self.quote, self.period)
        print(ret)

    def test_strong_breakout(self):
        ret = base_breakout(self.quote, self.period)
        print(ret)

    def test_blt(self):
        ret = blt(self.quote, self.period)
        print(ret)

    def test_vcp(self):
        ret = vcp(self.quote, self.period)
        print(ret)

    def test_step(self):
        ret = step(self.quote, self.period)
        print(ret)

    def test_volume_dry_up(self):
        ret = volume_dry_up.volume_dry_up(self.quote, self.period)
        print(ret)

    def test_update_candidate_pool(self):
        strategy_list = ['second_stage']   # super
        strategy_list = ['finance']
        strategy_list = ['fund']
        # strategy_list = ['bottom']
        # strategy_list = ['volume_dry_up']
        selector.update_candidate_pool(strategy_list, 'day')

    def test_get_candidate_pool(self):
        code_list = basic.get_candidate_stock_code(['second_stage'])
        print(code_list)

    def test_select(self):
        # code_list = selector.select(['value_return'], ['second_stage'], period='day')
        # code_list = selector.select(['vcp'], ['second_stage'])
        # code_list = selector.select(['step'], ['second_stage'], period='day')
        # code_list = selector.select(['step'], ['dyn_sys_green'], period='day')
        # code_list = selector.select(['step_breakout'], ['second_stage'], period='week')
        # code_list = selector.select(['vcp'], ['second_stage', 'super'], period='day')
        code_list = selector.select(['vcp_breakout'], ['second_stage', 'finance', 'vcp'], period='day')
        print(code_list)

    def test_update_candidate_pool_using_signal_config(self):
        strategy_list = ['trend_up']
        selector.update_candidate_pool(strategy_list, 'day')

    def test_select_using_signal_config(self):
        code_list = selector.select(['signal_config'], ['trend_up'], period='day')
        print(code_list)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(SelectorPluginTestCase('test_second_stage'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
