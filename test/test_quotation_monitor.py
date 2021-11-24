import unittest

import quotation_monitor


class QuotationMonitorTestCase(unittest.TestCase):
    def setUp(self):
        quotation_monitor.TradeSignalManager.reload_trade_order()

    def tearDown(self):
        pass

    def test_check(self):
        code = '002739'
        periods = ['day']
        strategy = 'vcp_breakout_signal_enter'
        in_position = True
        r = quotation_monitor.check(code, periods, strategy, in_position)
        print(r)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(QuotationMonitorTestCase('test_check_quote'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
