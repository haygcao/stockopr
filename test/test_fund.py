import datetime
import unittest

from acquisition import fund
from selector.plugin import fund as fund2


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

    def test_update_fund_market_value(self):
        report_date = datetime.date(2021, 9, 30)
        report_date = datetime.date(2021, 6, 30)
        # report_date = datetime.date(2021, 3, 31)
        # report_date = datetime.date(2020, 12, 31)
        # report_date = datetime.date(2020, 9, 30)
        # report_date = datetime.date(2020, 6, 30)
        # report_date = datetime.date(2020, 3, 31)
        # report_date = datetime.date(2019, 12, 31)
        fund2.update_fund_market_value(report_date)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(FundTestCase('test_fetch_all_code'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
