# -*- coding: utf-8 -*-
import datetime
import time

#import toolkit.wy_save_history_multiprocess
import util.macd
# import acquisition.wy as wy
import util.qt_util
from trade_manager import trade_manager

from util.log import logger


def test_save_quote():
    import acquisition.acquire as acquire
    acquire.save_quote()


def test_select():
    import selector.selector as selector
    from acquisition import quote_db
    # df = quote_db.get_price_info_df_db('300502', 500, from_file='data/300502.csv')

    import config.config as config
    import util.mysqlcli as mysqlcli
    _conn = mysqlcli.get_connection()
    code = '300502'
    # code = '000625'
    # code = '600588'
    # code = '300312'
    # code = '300946'
    code = '000982'
    df = quote_db.get_price_info_df_db(code, 500, '', 'D', _conn)
    df = df.sort_index()
    ret = selector.is_match(df, 'bull_at_bottom', 'day')
    # ret = selector.is_match(df, 'hot_strong')
    # ret = selector.is_match(df, 'nsbl')
    # ret = selector.is_match(df, 'dlxt_blue')
    # ret = selector.is_match(df, 'qlzs_p')
    print(ret)


def test_select_mp():
    import selector.selector as selector
    import acquisition.basic as basic
    strategy_name_list = ['ema_value']
    strategy_name_list = ['hot_strong', 'ema_value']
    strategy_name_list = ['bull_at_bottom']
    stock_list = selector.select(strategy_name_list, ['second_stage'])
    for code, name in stock_list:
        logger.info(code, name)
    logger.info('+++ {0} +++'.format(len(stock_list)))


def test_trend_recognition():
    import pointor.trend_recognition as tr
    import acquisition.quote_db as quote_db
    code = '600839'
    quote = quote_db.get_price_info_df_db(code, 250)

    trendr = tr.TrendRecognizer(code, quote)
    trendr.trend_recognition()
    trendr.print_result()


def test_signal():
    import pointor.signal as signal
    signal.check_signal('600839')

    # now = time.time()
    # today = datetime.date.today()

    # start_time_am = mktime(datetime.datetime(today.year, today.month, today.day, 9, 30))
    # end_time_pm = mktime(datetime.datetime(today.year, today.month, today.day, 15))

    # duration = 60
    # price_info_df_db = quote_db.get_price_info_df_db(code, duration)
    # price_info_df = copy.copy(price_info_df_db)
    # if now < end_time_pm and now > start_time_am and basic.istradeday(today):


def test():
    return


if __name__ == '__main__':
    test()
    logger.info('{} start scan...'.format(datetime.datetime.now()))

    t1 = time.time()
    # test_save_quote()
    test_select_mp()
    # test_select()
    # test_trend_recognition()
    # test_signal()

    t2 = time.time()
    logger.info('cost: [{}]   {} - {}'.format(round(t2 - t1, 2),
                                      datetime.datetime.fromtimestamp(t1).strftime('%H:%M:%S'),
                                      datetime.datetime.fromtimestamp(t2).strftime('%H:%M:%S')))
