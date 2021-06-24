import unittest

from acquisition import basic


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_stock_code(self):
        name = '长安汽'
        code = basic.get_stock_code(name)
        print(code)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(BasicTestCase('test_check_quote'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
