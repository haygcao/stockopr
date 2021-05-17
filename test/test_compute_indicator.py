import unittest

from indicator import compute_indicator
from acquisition.quote_db import get_price_info_df_file_day


class IndicatorTestCase(unittest.TestCase):
    def setUp(self):
        code = '300502'
        self.quote = get_price_info_df_file_day(code, 250, '2021-5-13', 'data/300502.csv')

    def tearDown(self):
        pass

    def test_compute_indicator(self):
        quote = compute_indicator.compute_indicator(self.quote, period='day')
        print(quote.columns)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(IndicatorTestCase('test_compute_indicator'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())