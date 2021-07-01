import unittest

from acquisition import tx, quote_db
from indicator import ad, relative_price_strength


class IndicatorTestCase(unittest.TestCase):
    def setUp(self):
        code = '300502'
        period = 'm30'
        # period = 'day'
        count = 250
        # quote = tx.get_kline_data_sina(code, period, count)
        self.quote = quote_db.get_price_info_df_db_day(code, days=250)

    def tearDown(self):
        pass

    def test_ad(self):
        quote = ad.compute_ad(self.quote)
        print(quote[-10:])

    def test_rps(self):
        quote = relative_price_strength.relative_price_strength(self.quote)
        print(quote[-10:])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(IndicatorTestCase('test_ad'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
