import sys
import tkinter
import unittest

from toolkit import tradeapi
from toolkit.tradeapi import OperationThs


class TradeGUITestCase(unittest.TestCase):
    # def setUp(self):
    #     pass
    #
    # def tearDown(self):
    #     pass

    def test_get_position(self):
        pos_detail = (36, 456)
        pos_asset = (45, 354)
        pos_buy_and_sell = (25, 159)

        operation = OperationThs()
        operation.max_window()

        pre_position = operation.get_position()
        print(pre_position)

        operation.max_window()
        code = '300502'
        # operation.order(code, 'B', 1500)

        operation.refresh()
        cur_position = operation.get_position()
        is_dealt = operation.get_deal(code, pre_position, cur_position)
        print(is_dealt)
        menoy = operation.get_asset()
        print(menoy)

        detail = operation.get_operation_detail()
        print(detail)
        pre_position = cur_position

    def test_order(self):
        code = '300502'
        count = '100'
        tradeapi.order('B', code, count, auto=False)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TradeGUITestCase('test_get_position'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
