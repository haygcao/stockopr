# -*- coding: utf-8 -*-

import unittest

from indicator import finance


class FinanceTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_finance(self):
        code_list = ['002739']
        code_list = ['002739', '300502']
        finance.finance(code_list)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(FinanceTestCase('test_fetch_all_code'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
