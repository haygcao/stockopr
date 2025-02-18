import unittest

from acquisition import tx, quote_db
from indicator import compute_indicator
from acquisition.quote_db import get_price_info_df_file_day
from pointor import signal, signal_finance


class SignalTestCase(unittest.TestCase):
    def setUp(self):
        self.code = '300369'
        self.period = 'day'  # 'm1'  # 'day'
        count = 250 * 5
        # self.quote = get_price_info_df_file_day(code, 250, '2021-5-13', 'data/300502.csv')
        # self.quote = tx.get_kline_data(code, self.period, count)
        self.quote = quote_db.get_price_info_df_db(self.code, days=count, period_type='D')

    def tearDown(self):
        pass

    def test_compute_signal(self):
        quote = signal.compute_signal(self.code, self.period, self.quote)
        # print(quote[:50])
        # print(quote[-50:])
        print([column for column in quote.columns if 'signal_e' in column])

    def test_one_signal(self):
        quote = signal_finance.signal_enter(self.quote, period=self.period)
        print(quote)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(SignalTestCase('test_compute_signal'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())