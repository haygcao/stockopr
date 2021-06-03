import unittest

from trade_manager import tradeapi


class TradeApiTestCase(unittest.TestCase):
    # def setUp(self):
    #     pass
    #
    # def tearDown(self):
    #     pass

    def test_query_position(self):
        code = '300502'
        tradeapi.query_position(code)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TradeApiTestCase('test_query_position'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
