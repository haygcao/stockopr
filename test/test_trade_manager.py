import datetime
import unittest

import util.qt_util
from server import config as svr_config
from trade_manager import trade_manager, db_handler, trade_truth


class TradeManagerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_trade_truth(self):
        trade_details = trade_truth.trade_truth()

        # data = trade_truth.load_data()
        # trades = trade_truth.compute_trade(data)
        # print(trades)

    def test_sync(self):
        trade_manager.sync()

    def test_withdraw(self):
        # order_list = trade_manager.query_withdraw_order()
        # print(order_list)
        trade_manager.withdraw()

    def test_query_money(self):
        accout_type = svr_config.ACCOUNT_ID_XY
        menoy = trade_manager.query_money(accout_type)
        print(menoy)
        db_handler.save_money(menoy)
        money = db_handler.query_money()
        print(money)

    def test_get_position(self):
        account_id = svr_config.ACCOUNT_ID_XY
        code = '300502'

        pre_position = trade_manager.query_position(code)
        db_handler.save_positions(account_id, [pre_position])
        position = db_handler.query_position(account_id, code)
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

    def test_query_trade_order(self):
        account_id = svr_config.ACCOUNT_ID_XY
        r = db_handler.query_trade_order_map(account_id)
        print(r)

    def test_order(self):
        account_id = svr_config.ACCOUNT_ID_XY
        op_type = svr_config.OP_TYPE_DBP
        # op_type = svr_config.OP_TYPE_RZ
        # op_type = svr_config.OP_TYPE_RQ

        # code = '300502'
        # count = 0
        # # tradeapi.order('B', code, count, auto=False)
        # trade_manager.buy(account_id, op_type, code, count, period='day')
        #
        code = '002739'
        code = '000930'
        count = 100
        # # tradeapi.order('B', code, count, auto=False)
        trade_manager.buy(account_id, op_type, code, count, period='day')
        # trade_manager.sell(account_id, op_type, code, count, period='day')

        # trade_manager.buy('300502')

        # trade_manager.order(account_id, op_type, 'B', '300502', 1500)

    def test_query_order(self):
        account_id = svr_config.ACCOUNT_ID_XY
        code = '300502'
        order_list = trade_manager.db_handler.query_trade_order_map(account_id, code)
        print(order_list)

    def test_create_trade_order(self):
        account_id = svr_config.ACCOUNT_ID_XY
        code = '300502'
        trade_manager.create_trade_order(account_id, code, 0, stop_loss=0, strategy='vcp_breakout_signal_enter')

    def test_patrol(self):
        trade_manager.patrol()

    def test_message_box(self):
        util.qt_util.popup_warning_message_box_mp('hello', print, 'xxx')
        util.qt_util.popup_warning_message_box_mp('hello')
        # trade_manager.popup_warning_message_box('hello')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TradeManagerTestCase('test_query_order'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
