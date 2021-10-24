import datetime
import unittest

from strategy import momentum


class StrategyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_compute_momentum(self):
        momentum.compute_momentum(datetime.date(2021, 10, 31), '002739')

    def test_momentum(self):
        momentum.momentum_selector(date=datetime.date(2021, 8, 31))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(StrategyTestCase('test_check_quote'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
