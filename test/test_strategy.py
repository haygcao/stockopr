import datetime
import unittest

from strategy import momentum, relative_strength


class StrategyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_compute_momentum(self):
        momentum.compute_momentum(datetime.date(2021, 10, 31), '002739')

    def test_momentum(self):
        momentum.compute_momentums(date=datetime.date(2021, 8, 31))

    def test_rps_select_pioneer(self):
        relative_strength.select_pioneer(date=datetime.date(2021, 8, 31), m=0.1, n=100, dump=True, mp=True)

    def test_select_pioneer(self):
        momentum.select_pioneer(date=datetime.date(2021, 8, 31), m=0.1, n=100, dump=True)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(StrategyTestCase('test_check_quote'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
