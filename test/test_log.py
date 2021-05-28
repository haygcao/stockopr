import unittest

from util.log import logger


class LogTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_log(self):
        logger.debug("debug log %s", "comma", 'xxx')
        logger.info("info log")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(LogTestCase('test_log'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
