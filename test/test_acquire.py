import datetime
import os
import unittest

from acquisition import acquire, quote_db, quote_tdx, finance
from acquisition import industry_index
from config import config
from util import dt


class AcquireTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_save_quote(self):
        acquire.save_quote()

    def test_financial(self):
        df = finance.fetch_finance_stock('002739', datetime.date(2021, 9, 30))
        print(df)

    def test_check_quote(self):
        trade_date = dt.get_trade_date()
        trade_date = datetime.date(2021, 6, 17)
        trade_date_prev = dt.get_pre_trade_date(trade_date)

        quote1 = quote_db.query_quote(trade_date)
        quote2 = quote_db.query_quote(trade_date_prev)
        ret = acquire.check_quote(quote1, quote2)
        print(ret)

    def test_save_market_index_trade_info(self):
        acquire.save_market_index_trade_info()

    def test_tdx_basic_info(self):
        market = 'shm.tnf'
        market = 'szm.tnf'
        infos = quote_tdx.basic_info(os.path.join(config.tdx_home, 'T0002/hq_cache/' + market))  # szm.tnf
        for t in infos:
            if '300502' in t[0]:
                print(t)
        print(infos)

    def test_tdx_quote(self):
        import os
        path = os.path.join(config.tdx_home, 'vipdoc/sz/lday')
        file_list = os.listdir(os.path.join(config.tdx_home, 'vipdoc/sz/lday'))
        for i in file_list:
            if i == 'sz300502.day':
                quote = quote_tdx.parse_quote(path + i)
                break
        path = os.path.join(config.tdx_home, 'vipdoc/sz/lday/sz300502.day')
        quote = quote_tdx.parse_quote(path)
        print(quote)

    def test_update_index_quote(self):
        r = industry_index.update_index_quote(datetime.date.today())
        print(r)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(AcquireTestCase('test_check_quote'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
