import datetime
import unittest

from acquisition import fund


class FundTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fetch_all_code(self):
        date = datetime.date(2021, 3, 31)
        date_db = fund.query_last_date()
        print(date_db)

        fund.init_fund_code(date)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(FundTestCase('test_fetch_all_code'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
