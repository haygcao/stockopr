import multiprocessing
import os
import threading
import unittest

import util.util
import test_std_signal_child
from util.log import logger


class LogTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_log(self):
        logger.info('abc')
        # logger.debug("debug log %s %s %s", "comma", 'xxx', 100, 1.001)
        # logger.info("info log", 'aaa', 111, 1.01)
        # logger.warning("info log", 'aaa', 111, 1.01)
        # logger.error("info log", 'aaa', 111, 1.01)
        # d = {'a': 1, 'b': 2}
        # logger.info(d)
        multiprocessing.Process(target=test_std_signal_child.f).start()
        threading.Thread(target=test_std_signal_child.f).start()
        # util.util.run_subprocess(os.path.join('test', 'test_std_signal_child.py'))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(LogTestCase('test_log'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
