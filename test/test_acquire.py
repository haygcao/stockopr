import unittest

from acquisition import acquire


class AcquireTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_check_quote(self):
        ret = acquire.check_quote()
        print(ret)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(AcquireTestCase('test_check_quote'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())