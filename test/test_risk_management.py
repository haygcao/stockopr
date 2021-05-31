import unittest

from acquisition import tx
from trade_manager import trade_manager


class RiskManagementTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_query_order(self):
        code = '300502'
        order_list = trade_manager.query_trade_order_list(code)
        print(order_list[0])

    def test_create_trade_order(self):
        code = '300502'
        trade_manager.create_trade_order(code)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(RiskManagementTestCase('test_query_order'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
