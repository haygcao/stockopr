import unittest

from log4python.log4python import Log


class LogTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_log(self):
        logger = Log("LogTest", filename='D:\\log.txt')
        logger.debug("debug log")
        logger.info("info log")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(LogTestCase('test_log'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
