import datetime
import multiprocessing
import sys
import unittest

from util import dt, util
from util.singleten import SingleInstance, SingleInstanceException


def f(name):
    import logging
    logger = logging.getLogger("tendo.singleton")
    tmp = logger.level
    logger.setLevel(logging.CRITICAL)  # we do not want to see the warning
    try:
        me2 = SingleInstance(flavor_id=name)  # noqa
    except SingleInstanceException:
        sys.exit(-1)
    logger.setLevel(tmp)
    pass


class UtilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_pid_by_exec(self):
        ret = util.get_pid_by_exec('tdxw.exe')
        print(ret)

    def test_is_holiday(self):
        day = datetime.date(2021, 10, 1)
        ret = dt.isholiday(day)
        print(ret)

    def test_get_prev_trade_date(self):
        date = dt.get_pre_trade_date()
        print(date)

    def test_singleten_1(self):
        me = SingleInstance(flavor_id="test-1")
        del me  # now the lock should be removed
        assert True

    def test_singleten_2(self):
        p = multiprocessing.Process(target=f, args=("test-2",))
        p.start()
        p.join()
        # the called function should succeed
        assert p.exitcode == 0, "%s != 0" % p.exitcode

    def test_singleten_3(self):
        me = SingleInstance(flavor_id="test-3")  # noqa -- me should still kept
        p = multiprocessing.Process(target=f, args=("test-3",))
        p.start()
        p.join()
        # the called function should fail because we already have another
        # instance running
        assert p.exitcode != 0, "%s != 0 (2nd execution)" % p.exitcode
        # note, we return -1 but this translates to 255 meanwhile we'll
        # consider that anything different from 0 is good
        p = multiprocessing.Process(target=f, args=("test-3",))
        p.start()
        p.join()
        # the called function should fail because we already have another
        # instance running
        assert p.exitcode != 0, "%s != 0 (3rd execution)" % p.exitcode

    def test_singleten_4(self):
        lockfile = '/tmp/foo.lock'
        me = SingleInstance(lockfile=lockfile)
        assert me.lockfile == lockfile


def suite():
    suite = unittest.TestSuite()
    suite.addTest(UtilTestCase('test_is_holiday'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
