import datetime
import unittest

from acquisition import tx
from trade_manager import trade_manager, db_handler


class TradeManagerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sync(self):
        trade_manager.sync()

    def test_withdraw(self):
        # order_list = trade_manager.query_withdraw_order()
        # print(order_list)
        trade_manager.withdraw()

    def test_query_money(self):
        menoy = trade_manager.query_money()
        print(menoy)
        db_handler.save_money(menoy)
        money = db_handler.query_money()
        print(money)

    def test_get_position(self):
        code = '300502'

        pre_position = trade_manager.query_position(code)
        db_handler.save_positions([pre_position])
        position = db_handler.query_position(code)
        print(position)



        # detail = trade_manager.query_operation_detail()
        # print(detail)
        # pre_position = cur_position

    def test_query_operation_detail(self):
        code = '300502'

        detail_list = trade_manager.query_operation_detail()
        # detail_list = trade_manager.query_operation_detail(code)
        print(detail_list)
        db_handler.save_operation_details(detail_list)
        detail_list = db_handler.query_operation_details(code, datetime.date(2021, 6, 8))
        print(detail_list)
        detail_list = db_handler.query_operation_details()
        print(detail_list)

    def test_order(self):
        code = '300502'
        count = 0
        # tradeapi.order('B', code, count, auto=False)
        trade_manager.buy(code, count)

        code = '300501'
        count = 100
        # tradeapi.order('B', code, count, auto=False)
        trade_manager.buy(code, count)

        # trade_manager.buy('300502')
        trade_manager.order('B', '300502', 1500)

    def test_query_order(self):
        code = '300502'
        order_list = trade_manager.query_trade_order_list(code)
        print(order_list[0])

    def test_create_trade_order(self):
        code = '300502'
        trade_manager.create_trade_order(code)

    def test_patrol(self):
        trade_manager.patrol()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TradeManagerTestCase('test_query_order'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
