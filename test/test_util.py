import datetime
import unittest

from util import dt


class UtilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_holiday(self):
        day = datetime.date(2021, 10, 1)
        ret = dt.isholiday(day)
        print(ret)

    def test_get_prev_trade_date(self):
        date = dt.get_pre_trade_date()
        print(date)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(UtilTestCase('test_is_holiday'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
