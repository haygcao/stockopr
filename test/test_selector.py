import datetime
import unittest

from acquisition import quote_db
from selector import selector
from selector.plugin.second_stage import second_stage
from util import dt


class SelectorPluginTestCase(unittest.TestCase):
    def setUp(self):
        self.code = '300502'
        self.code = '600483'
        self.period = 'day'
        count = 250
        self.quote = quote_db.get_price_info_df_db(self.code, days=count, period_type='D')

    def tearDown(self):
        pass

    def test_second_stage(self):
        ret = second_stage(self.quote)
        print(ret)

    def test_update_candidate_pool(self):
        selector.update_candidate_pool()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(SelectorPluginTestCase('test_second_stage'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
