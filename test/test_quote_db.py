import datetime
import unittest

from acquisition import quote_db, tx, acquire


class QuoteDBTestCase(unittest.TestCase):
    # def setUp(self):
    #     pass
    #
    # def tearDown(self):
    #     pass

    def test_compute_price_divisor(self):
        code = '300502'
        quote = tx.get_kline_data(code, period='m30', count=250)
        code = '002739'
        quote = tx.get_kline_data(code, period='m30', count=250)
        quote = quote_db.get_price_info_df_db(code)
        divisor_date = datetime.datetime(2021, 6, 8)
        yest_close_adjust = 34.34
        quote = quote_db.compute_price_divisor(quote, divisor_date=divisor_date, yest_close_adjust=yest_close_adjust)
        print(quote)

    def test_compute_martet_avg_close(self):
        trade_date = datetime.date(2021, 6, 28)
        quote = quote_db.query_quote(trade_date)
        quote = acquire.compute_market_avg_quote(quote)
        print(quote)

    def test_add_market_avg_close(self):
        begin_date = datetime.date(2010, 1, 1)
        end_date = datetime.date.today()
        # end_date = datetime.date(2020, 7, 1)
        # end_date = datetime.date(2010, 1, 8)
        quote_db.add_market_avg_quote(begin_date, end_date)

    def test_compute_market(self):
        # in 1979.35s (0:32:59)
        begin_date = datetime.datetime(2020, 1, 1)
        today = datetime.date.today()   # 2021/07/01
        end_date = datetime.datetime(today.year, today.month, today.day)
        # end_date = datetime.date(2020, 7, 1)
        # end_date = datetime.datetime(2020, 1, 8)

        quote_db.compute_market(begin_date, end_date)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(QuoteDBTestCase('test_compute_price_divisor'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
