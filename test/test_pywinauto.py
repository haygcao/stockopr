import unittest

import win32api


class PyWinAutoTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pywinauto(self):
        # print(pywinauto.win32structures.RECT.width())
        # print(pywinauto.win32structures.RECT.height())
        print(win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
        # print(client_rect.left, client_rect.top, client_rect.right, client_rect.bottom)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(PyWinAutoTestCase('test_pywinauto'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
