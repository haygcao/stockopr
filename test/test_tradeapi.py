import unittest

from server import config as svr_config
from trade_manager import tradeapi


class TradeApiTestCase(unittest.TestCase):
    # def setUp(self):
    #     pass
    #
    # def tearDown(self):
    #     pass

    def test_query_position(self):
        code = '300502'
        code = ''
        account_type = svr_config.ACCOUNT_TYPE_XY
        ret = tradeapi.query_position(account_type, code)
        print(ret)

    def test_query_detail(self):
        code = '300502'
        code = ''
        account_type = svr_config.ACCOUNT_TYPE_XY
        ret = tradeapi.query_operation_detail(account_type, code)
        print(ret)

    def test_query_asset(self):
        account_type = svr_config.ACCOUNT_TYPE_XY
        ret = tradeapi.get_asset(account_type)
        print(ret)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TradeApiTestCase('test_query_position'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
