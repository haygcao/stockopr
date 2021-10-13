import unittest

from util import pylinuxauto


class PyLinuxAutoTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pywinauto(self):
        handle = pylinuxauto.get_active_window()
        print('+', handle, '+')

        # pylinuxauto.active_window_by_name("通达信金融终端V7.56")
        # pylinuxauto.send_key('alt+F4')
        pylinuxauto.send_key('Return')
        return

        handle = '117440526'
        name = pylinuxauto.get_window_name(handle)
        print('+', name, '+')

        name = '通达信金融终端V7.56'
        handle = pylinuxauto.search_window_handle(name)
        print('+', handle, '+')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(PyLinuxAutoTestCase('test_pywinauto'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
