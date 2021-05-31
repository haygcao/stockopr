import unittest

from acquisition import tx


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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(FetchQuoteTestCase('test_fetch_quote_sina'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
