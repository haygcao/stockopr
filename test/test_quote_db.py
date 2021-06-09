import datetime
import unittest

from acquisition import quote_db, tx


class QuoteDBTestCase(unittest.TestCase):
    # def setUp(self):
    #     pass
    #
    # def tearDown(self):
    #     pass

    def test_compute_price_divisor(self):
        code = '300502'
        # quote = tx.get_kline_data_sina(code, period='m30', count=250)
        quote = quote_db.get_price_info_df_db(code)
        divisor_date = datetime.datetime(2021, 6, 8)
        yest_close_adjust = 34.34
        quote = quote_db.compute_price_divisor(quote, divisor_date=divisor_date, yest_close_adjust=yest_close_adjust)
        print(quote)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(QuoteDBTestCase('test_compute_price_divisor'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
