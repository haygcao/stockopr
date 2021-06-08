import datetime
import unittest

from acquisition import quote_db


class QuoteDBTestCase(unittest.TestCase):
    # def setUp(self):
    #     pass
    #
    # def tearDown(self):
    #     pass

    def test_query_position(self):
        code = '300502'
        quote = quote_db.get_price_info_df_db(code)
        divisor_date = datetime.datetime(2021, 6, 8)
        quote = quote_db.compute_price_divisor(quote, divisor_date=divisor_date)
        print(quote)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(QuoteDBTestCase('test_query_position'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
