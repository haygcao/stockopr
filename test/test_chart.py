import unittest

import chart


class ChartTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_open_graph(self):
        code = '300502'
        period = 'day'
        index = 'rps'
        chart.open_graph(code, period, index)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ChartTestCase('test_chart'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
