import datetime
import unittest

import sqlalchemy

from acquisition import tx
from config import config

from pointor import signal
from util import mysqlcli


class SignalTestCase(unittest.TestCase):
    def setUp(self):
        code = '300502'
        # code = '000963'
        self.period = 'day'
        count = 250
        # self.quote = get_price_info_df_file_day(code, 250, '2021-5-13', 'data/300502.csv')
        self.quote = tx.get_kline_data(code, self.period, count)

    def tearDown(self):
        pass

    def test_save_into_db(self):
        import pandas as pd
        from sqlalchemy import create_engine

        table_name = "quote"
        # data_frame = pd.DataFrame(data=self.quote)
        data_frame = self.quote
        sql_engine = create_engine('mysql+pymysql://{user}:{password}@127.0.0.1/stock'.format(
            user=config.db_user, password=config.db_passwd), pool_recycle=3600)
        db_connection = sql_engine.connect()

        query_sql = "select trade_date from quote where code = '{}' order by trade_date desc limit 1".format(
            data_frame['code'][0])
        r = db_connection.execute(query_sql)
        trade_date = None
        for row in r:
            trade_date = row[0]

        if trade_date:
            data_frame = data_frame[data_frame.index > trade_date]

        try:
            data_frame.to_sql(table_name, db_connection, index_label='trade_date', if_exists='append')

            # with sql_engine.begin() as cnx:
            #     # cursor = cnx.cursor()
            #     insert_sql = "INSERT IGNORE INTO quote ('code', 'trade_date', 'close', 'high', 'low', 'open', 'volume') values (?, ?, ?, ?, ?, ?, ?)"
            #     cnx.execute_many(insert_sql, val_many)

            # key_list = ['code', 'trade_date', 'close', 'high', 'low', 'open', 'volume']
            # key = ', '.join(key_list)
            # # fmt = ', '.join(fmt_list)
            # fmt = ', '.join(['%s' for i in range(len(key_list))])
            # insert_sql = 'insert into quote({0}) values ({1})'.format(key, fmt)
            #
            # print(insert_sql)
            # val_many = []
            # for row in data_frame.iterrows():
            #     val_list = [row[1]['code'], row[0], row[1]['close'], row[1]['high'], row[1]['low'], row[1]['open'], row[1]['volume']]
            #
            #     val = tuple(val_list)
            #     val_many.append(val)
            # print(val_many)
            # db_connection = mysqlcli.get_connection()
            # cursor = db_connection.cursor()
            # cursor.executemany(insert_sql, val_many)
            #
            # db_connection.commit()
        except ValueError as vx:
            print(vx)
        except Exception as ex:
            print(ex)
        else:
            print("Table %s created successfully." % table_name);
        finally:
            db_connection.close()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(SignalTestCase('test_save_into_db'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())