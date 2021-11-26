# -*- encoding:utf-8 -*-

import datetime
import time

import numpy
import pandas
import socket

from sqlalchemy import create_engine, text

import config.config as config
import util.mysqlcli as mysqlcli
import acquisition.basic as basic
import acquisition.tx as tx
import acquisition.wy as wy
import acquisition.quote_db as quote_db
import acquisition.quote_www as quote_www

# timeout in seconds
from acquisition import industry_index, quote_tdx
from indicator import relative_strength_rating
from util import dt
from util.log import logger
from util import qt_util

timeout = 5
socket.setdefaulttimeout(timeout)


def save_stock_basic_info(xlsfile):
    stock_list = tx.get_stock_list(xlsfile)
    stock_list = sorted(stock_list)
    basic.save_stock_list_into_db(stock_list)


def update_stock_basic_info(xlsfile):
    # http://stock.gtimg.cn/data/get_hs_xls.php?id=ranka&type=1&metric=chr
    stock_list = tx.get_stock_list(xlsfile)
    stock_list = sorted(stock_list)
    basic.upsert_stock_list_into_db(stock_list)


# 指数
def save_market_index_trade_info():
    index_list = [
        '0000001',
        '1399001',
        '1399006',
        '0000688',
    ]
    val_list = []
    for index in index_list:
        val = quote_www.get_price_urllib(index)
        if val:
            val_list.append(val)
        time.sleep(1)

    quote_db.insert_into_quote(val_list, ex=True)


def save_quote_tx(xls):
    _xls = xls if xls else tx.download_quote_xls()
    if _xls:
        trade_date = tx.get_trade_date(_xls)
        db_latest_trade_date = quote_db.get_latest_trade_date()
        if trade_date.day == db_latest_trade_date.day:
            return

        val_list = tx.get_quote(_xls)
        quote_db.insert_into_quote(val_list)
        save_stock_basic_info(_xls)
        today = datetime.date.today()
        if today.day == 1:
            update_stock_basic_info(_xls)


# 网易行情接口
def save_quote_wy():
    df_quote = wy.get_quote()

    # 修改数据库
    '''
    update quote set
    percent=FORMAT(percent*100, 2), hs=FORMAT(hs*100, 2), lb=FORMAT(lb, 2),
    wb=FORMAT(wb*100, 2), zf=FORMAT(zf*100, 2), five_minute=FORMAT(five_minute*100, 2)
    where trade_date >= '2017-04-05 00:00:00';
    '''
    # 部分值转换
    key_list = ['PERCENT', 'HS', 'WB', 'ZF', 'FIVE_MINUTE']
    for key in key_list:
        df_quote[key] = round(df_quote[key]*100, 2)
    key = 'LB'
    df_quote[key] = round(df_quote[key], 2)
    # print(df_quote[df_quote['CODE'] == '600839'])

    with mysqlcli.get_cursor() as c:
        try:
            # clear temp table
            c.execute('truncate table temp_quote')

            # MySql connection in sqlAlchemy
            engine = create_engine(
                'mysql+pymysql://{0}:{1}@127.0.0.1:3306/stock?charset=utf8mb4'.format(config.db_user, config.db_passwd))
            connection = engine.connect()

            # Do not insert the row number (index=False)
            df_quote.to_sql(name='temp_quote', con=engine, if_exists='append', index=False, chunksize=20000)
            # connection.close()

            sql_str = "select code, close, high, low, open, yestclose from quote " \
                      "where code in ('000001', '000002', '000003', '000004', '000005') and " \
                      "trade_date in (select max(trade_date) from quote);"
            c.execute(sql_str)
            r1 = c.fetchall()

            sql_str = "select code, close, high, low, open, yestclose from temp_quote " \
                      "where code in ('000001', '000002', '000003', '000004', '000005') and " \
                      "trade_date in (select max(trade_date) from temp_quote);"
            c.execute(sql_str)
            r2 = c.fetchall()

            r1_sorted = sorted(r1, key=lambda x: x['code'])
            r2_sorted = sorted(r2, key=lambda x: x['code'])
            if r1_sorted != r2_sorted:
                c.execute('insert into quote select * from temp_quote;')
                # c.execute('insert into temp_quote_test select * from temp_quote;')
            else:
                print('not trade day')
        except Exception as e:
            print(e)


def compute_market_avg_quote(quote):
    close = round(quote.close.mean(), 3)
    open = quote.open.mean()
    high = quote.high.mean()
    low = quote.low.mean()
    volume = quote.volume.mean()
    yest_close = quote.yest_close.mean()
    price_change = close - yest_close
    percent = round(100 * price_change / yest_close, 3)
    turnover_ratio = quote.turnover_ratio.mean()

    quote = quote.append([{
        'trade_date': quote['trade_date'][0],
        'code': 'maq',
        'close': close,
        'open': open,
        'high': high,
        'low': low,
        'volume': volume,
        'yest_close': yest_close,
        'price_change': price_change,
        'percent': percent,
        'turnover_ratio': turnover_ratio
    }], ignore_index=True)

    return quote


def save_quote_xl(ignore=True):
    t1 = datetime.datetime.now()
    same_day = True
    df_quote = tx.get_today_all()
    t2 = datetime.datetime.now()
    logger.info('fetch data cost: [{}]s'.format((t2 - t1).seconds))

    df_quote = df_quote[df_quote.volume > 0]
    # # define values
    # values = [value1, value2, value3, ...]
    #
    # # drop rows that contain any value in the list
    # df = df[df.column_name.isin(values) == False]

    try:
        # MySql connection in sqlAlchemy
        engine = create_engine(
            'mysql+pymysql://{0}:{1}@127.0.0.1:3306/stock?charset=utf8mb4'.format(config.db_user, config.db_passwd))
        with engine.connect() as con:
            prev_trade_date = dt.get_pre_trade_date(dt.get_trade_date())
            data = []
            for i in range(10):
                data.append({"code": df_quote.iloc[i]['code'], 'trade_date': prev_trade_date})

            statement = text("SELECT close, high, low, open FROM quote WHERE code = :code AND trade_date = :trade_date")

            for idx, line in enumerate(data):
                r = con.execute(statement, **line)
                key_list = ['close', 'open', 'high', 'low']
                for row in r:
                    for key in key_list:
                        if row[key] != df_quote.iloc[idx][key]:
                            same_day = False
                            break
                    else:
                        continue
                    break
                if not same_day:
                    break

        if same_day:
            logger.info('quote is same with prev trade date [{}], not updated...'.format(prev_trade_date))
            raise Exception('fetch data - no data')

        df_quote.loc[:, 'trade_date'] = df_quote.index

        tmp = df_quote['code'].duplicated()
        if tmp.any():
            logger.info('duplicated...')
            df_quote = df_quote[~df_quote['code'].duplicated(keep='first')]

        # df_basic = df_quote.loc[:, ['code', 'name']]
        stock_list = list(zip(df_quote['code'], df_quote['name']))
        # basic.save_stock_list_into_db(stock_list)
        # stock_list = stock_list[:10]

        df_quote = df_quote.drop('name', axis=1)

        trade_date_prev = dt.get_pre_trade_date()
        quote2 = quote_db.query_quote(trade_date_prev)

        if not check_quote(df_quote, quote2):
            if not ignore:
                return

        t3 = datetime.datetime.now()
        basic.upsert_stock_list_into_db(stock_list)
        t4 = datetime.datetime.now()
        logger.info('update basic cost: [{}]s'.format((t4 - t3).seconds))

        df_quote = compute_market_avg_quote(df_quote)

        # Do not insert the row number (index=False)
        df_quote.to_sql(name='quote', con=engine, if_exists='append', index=False, chunksize=20000)
        t5 = datetime.datetime.now()
        logger.info('save quote cost: [{}]s'.format((t5 - t4).seconds))

        # df_quote.to_csv('2021-06-07.csv')
    except Exception as e:
        logger.error(e)
        raise e


def save_quote_tx_one_day(trade_day):
    code_list = basic.get_all_stock_code()
    # code_list = code_list[:5]

    retry_code_list = []
    empty_code_list = []
    df_quote = pandas.DataFrame()
    for n in range(5):
        for code in code_list:
            df = tx.get_kline_data_tx(code, count=1, start_date=trade_day, end_date=trade_day)
            if isinstance(df, pandas.DataFrame):
                if df.empty:
                    empty_code_list.append(code)
                    print('{} no data'.format(code))
                    continue
                if df.index[-1] != trade_day:
                    continue
                df_quote = df_quote.append(df)
            else:
                retry_code_list.append(code)
        # time.sleep(0.5)
        if not retry_code_list:
            break
        code_list = retry_code_list
        print('retry [{}] -\n'.format(len(retry_code_list), str(retry_code_list)))
        print('empty [{}] -\n'.format(len(empty_code_list), str(empty_code_list)))

    try:
        # MySql connection in sqlAlchemy
        engine = create_engine('mysql+pymysql://{0}:{1}@127.0.0.1:3306/stock?charset=utf8mb4'.format(config.db_user, config.db_passwd))

        df_quote.loc[:, 'trade_date'] = df_quote.index

        # Do not insert the row number (index=False)
        df_quote.to_sql(name='quote', con=engine, if_exists='append', index=False, chunksize=20000)
    except Exception as e:
        logger.error(e)


def save_quote_impl(trade_date=None, xls=None):
    try:
        # save_quote_tx(xls)
        # quote_tdx.download_quote()
        save_quote_xl()
        # save_quote_wy()
    except Exception as e:
        logger.error(e)
        raise e


def save_quote():
    logger.info('update quote')
    if not dt.istradeday():
        pass
        # exit(0)
    xls = None
    # xls = 'data/xls/2021-05-24.xls'
    # t1 = datetime.datetime.now()
    # save_quote_impl(xls)
    # t2 = datetime.datetime.now()
    # logger.info('save quote cost [{}]s'.format((t2 - t1).seconds))
    #
    today = datetime.date.today()  # 2021/07/01
    # today_datetime = datetime.datetime(today.year, today.month, today.day)
    # quote_db.compute_market(today_datetime, today_datetime, include_end=True)
    #
    # t3 = datetime.datetime.now()
    # logger.info('calculate and save market cost [{}]s'.format((t3 - t2).seconds))

    save_market_index_trade_info()
    logger.info('save market index quote')

    # industry_index.update_index_quote(start_date=today)
    # logger.info('save industry index quote')

    relative_strength_rating.update_rs_rating(trade_date=today, update_db=True)
    logger.info('update rs rating')

    trade_date = dt.get_trade_date()
    count = quote_db.get_quote_count(trade_date)
    qt_util.popup_info_message_box_mp('[{}] [{}] rows updated'.format(trade_date, count))


def check_quote(quote1, quote2):
    return True

    logger.info('begin check quote')

    # quote1 = quote1.loc[quote1.index.intersection(quote2.index)]
    # quote2 = quote2.loc[quote2.index.intersection(quote1.index)]

    quote1 = quote1.loc[quote1.code.isin(quote2.code)]
    quote2 = quote2.loc[quote2.code.isin(quote1.code)]

    r = (quote1 == quote2).all(axis=1)
    same = r[r]
    logger.info('[{}] stocks - two trade day with same quote: \n{}'.format(len(quote1), same.index))
    return not numpy.any(r)

    same = []
    code_list = basic.get_all_stock_code()
    for code in code_list:
        quote = quote_db.get_price_info_df_db_day(code, days=2)
        if len(quote) < 2:
            logger.info('{} - length of quote [{}]'.format(code, len(quote)))
            continue
        if numpy.all(quote.iloc[0] == quote.iloc[1]):
            same.append(code)
    logger.info('[{}] stocks, quote of two trade day are same'.format(len(same)))

    if not same or len(same) / len(code_list) < 0.001:
        if same:
            logger.info('stocks two trade day with same quote: \n{}'.format(same))
        return True
    return False


if __name__ == '__main__':
    save_quote()
    pass
    # trade_date = datetime.date(2021, 6, 4)
    # # trade_date = datetime.date.today()
    # save_quote_tx_one_day(trade_date)
