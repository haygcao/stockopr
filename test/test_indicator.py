import unittest

from acquisition import tx, quote_db
from indicator import ad


class IndicatorTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_holiday(self):
        code = '300502'
        period = 'm30'
        # period = 'day'
        count = 250
        # quote = tx.get_kline_data_sina(code, period, count)
        quote = quote_db.get_price_info_df_db_day(code,  days=250)

        quote = ad.compute_ad(quote)
        print(quote[-10:])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(IndicatorTestCase('test_is_holiday'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())