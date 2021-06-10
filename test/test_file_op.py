import datetime
import unittest

from config import config
from config.config import Policy
from pointor.signal import get_supplemental_signal
from quotation_monitor import TradeSignal, write_supplemental_signal


class FileOpTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_write(self):
        trade_signal = TradeSignal('300502', 34, datetime.datetime.now(), 'B', Policy.DEFAULT, 'day', True)
        write_supplemental_signal(config.supplemental_signal_path, trade_signal)

    def test_read(self):
        period = 'day'
        r = get_supplemental_signal(config.supplemental_signal_path, period)
        print(len(r))
        print(r)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(FileOpTestCase('test_write'))
    suite.addTest(FileOpTestCase('test_read'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
