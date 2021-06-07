import datetime
import unittest

from acquisition import tx, acquire


class FetchQuoteTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fetch_quote_sina(self):
        code = '300502'
        period = 'm30'
        count = 250
        quote = tx.get_kline_data_sina(code, period, count)
        print(quote)

    def test_fetch_today_all_quote_sina(self):
        quote = tx.get_today_all()
        print(quote)

    def test_fetch_one_day_quote(self):
        trade_date = datetime.date(2021, 6, 4)
        quote = acquire.save_quote_tx_one_day(trade_date)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(FetchQuoteTestCase('test_fetch_quote_sina'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
