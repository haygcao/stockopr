import datetime
import unittest

from util.dt import isholiday


class UtilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_holiday(self):
        day = datetime.date(2021, 10, 1)
        ret = isholiday(day)
        print(ret)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(UtilTestCase('test_is_holiday'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
