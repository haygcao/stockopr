import datetime
import unittest

from acquisition import quote_db, tx
from indicator import ad, relative_strength_rating, quantity_relative_ratio, trend_strength
from indicator import boll
from indicator import cci
from indicator import crsi
from indicator import market_deviation_mat
from indicator import momentum
from indicator import relative_price_strength
from indicator import rsi
from indicator import second_stage
from indicator import step
from indicator import vcp


class IndicatorTestCase(unittest.TestCase):
    def setUp(self):
        self.code = '002739'
        self.code = '601633'
        # self.code = '300598'
        self.period = 'm30'
        self.period = 'day'
        count = 250
        # self.quote = tx.get_kline_data_sina(self.code, self.period, count)
        self.quote = quote_db.get_price_info_df_db_day(self.code, days=1000)  # days=250)

    def tearDown(self):
        pass

    def test_trend_strength(self):
        quote = trend_strength.compute_trend_strength(self.quote, self.period)

    def test_quantity_relative_ratio(self):
        from acquisition import tx
        self.quote = tx.get_kline_data_sina(self.code)
        quantity_relative_ratio.quantity_relative_ratio(self.quote, self.period)

    def test_rs_rating(self):
        trade_date = datetime.date(2021, 12, 8)
        # trade_date = None
        import time
        t1 = time.time()
        relative_strength_rating.update_rs_rating(trade_date=trade_date)
        print(time.time() - t1)

    def test_momentum(self):
        momentum.momentum_month(self.quote, self.period)

    def test_crsi(self):
        crsi.crsi(self.quote, self.period)

    def test_vcp(self):
        quote = vcp.vcp(self.quote, self.period)
        print(quote[-10:])

    def test_rsi(self):
        quote = rsi.compute_rsi(self.quote, self.period)
        print(quote[-10:])

    def test_boll(self):
        self.quote['ma20'] = self.quote.close.rolling(20).mean()
        quote = boll.compute_boll(self.quote, self.period)
        diff = quote.boll_u - quote.boll_l
        print(quote[-10:])

    def test_cci(self):
        quote = cci.compute_cci(self.quote, self.period)
        print(quote[-10:])

    def test_ad(self):
        quote = ad.compute_ad(self.quote)
        print(quote[-10:])

    def test_rps(self):
        quote = relative_price_strength.relative_price_strength(self.quote)
        print(quote[-10:])

    def test_step(self):
        quote = step.step(self.quote, self.period, 13, 26)
        print(quote[-10:])

    def test_second_stage(self):
        quote = second_stage.second_stage(self.quote, 'day')
        print(quote[-10:])

    def test_market_deviation_mat(self):
        column = 'macd_bull_market_deviation'
        quote = market_deviation_mat.compute_index(self.quote, 'day', column)
        # quote = market_deviation_mat.market_deviation(self.quote, 'day')
        print(quote.max_period[quote.max_period.notna()])
        print(quote.min_period[quote.min_period.notna()])
        print(quote[-10:])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(IndicatorTestCase('test_ad'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
