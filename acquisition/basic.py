# -*- encoding: utf-8 -*-

# from util import get_pid_by_name
import subprocess
import os
import time
from datetime import date
import datetime

import pandas
import pymysql

import util.mysqlcli as mysqlcli
import acquisition.quote_www as price
import config.config as config
from util.log import logger


def upsert_candidate_pool(code_list, status, strategy, ignore_duplicate=True):
    if not code_list:
        return

    with mysqlcli.get_cursor() as cursor:
        sql_str = u"INSERT IGNORE INTO portfolio_history (code, class, status) VALUES (%s, %s, %s)"
        value_list = []
        for code in code_list:
            value_list.append((code, strategy, status))
            # value_list.append((code, strategy, status, strategy, status))

        try:
            if not ignore_duplicate:
                cursor.executemany(sql_str, value_list)
                sql_str = u"delete from portfolio where class = %s"  # and status = %s"
                # cursor.execute(sql_str, (strategy, status))
                cursor.execute(sql_str, (strategy, ))

            sql_str = u"INSERT IGNORE INTO portfolio (code, class, status) VALUES (%s, %s, %s)"
            # not all arguments converted during string formatting
            # sql_str = u"INSERT INTO portfolio (code, class, status) VALUES (%s, %s, %s) "\
            #           "ON DUPLICATE KEY update class = %s, status = %s"

            cursor.executemany(sql_str, value_list)

        except pymysql.err.IntegrityError as e:
            pass
        except Exception as e:
            print(e)


def get_candidate_stock_code(candidate_list, op='AND'):
    class_list = "','".join(candidate_list)

    with mysqlcli.get_cursor() as c:
        # sql = 'SELECT DISTINCT code FROM {0}'.format(config.sql_tab_quote)
        if op == 'OR' or len(candidate_list) == 1:
            sql = "SELECT code FROM portfolio where class in ('%s') order by code"  # status = 'candidate' and
            val = class_list
        else:
            sub_sql = "SELECT code, count(code) c FROM portfolio where class in ('%s') group by code"
            sql = "select code, c from ({}) s where s.c = %s".format(sub_sql)
            val = (class_list, len(candidate_list))

        logger.info(sql % val)
        # c.execute(sql, class_list)
        c.execute(sql % val)
        stock_code_list = c.fetchall()

        return [code['code'] for code in stock_code_list]


def _get_traced_stock_code(strategy_list, status):
    with mysqlcli.get_cursor() as c:
        sql = "SELECT code FROM portfolio where class in (%s) order by code"  # status = %s and
        c.execute(sql, (','.join(strategy_list),))
        stock_code_list = c.fetchall()

        return [code['code'] for code in stock_code_list]


def get_traced_stock_code(strategy_list):
    return _get_traced_stock_code(strategy_list, 'traced')


def get_allowed_to_buy_stock_code(strategy_list):
    return _get_traced_stock_code(strategy_list, 'allow_buy')


def delete_portfolio(status_list, strategy_list):
    with mysqlcli.get_cursor() as c:
        sql = "DELETE FROM portfolio where status in ('%s') and class in ('%s')" % (
            "','".join(status_list), "','".join(strategy_list))
        c.execute(sql)
        c.execute('SELECT ROW_COUNT() as DelRowCount')
        return c.fetchone()['DelRowCount']


def get_all_stock_code():
    with mysqlcli.get_cursor() as c:
        # sql = 'SELECT DISTINCT code FROM {0}'.format(config.sql_tab_quote)
        sql = "SELECT code FROM {0} where type = 'A' order by code".format(config.sql_tab_basic_info)
        c.execute(sql)
        stock_code_list = c.fetchall()

        return [code['code'] for code in stock_code_list]


def get_stock_price_divisor(code):
    with mysqlcli.get_cursor() as c:
        sql = "SELECT date price_divisor_date, yest_close price_divisor_adj_price from {} e, {} q " \
              "where category = 1 and e.code = '{}' and q.code = e.code and e.date = q.trade_date " \
              "order by e.date".format(config.sql_tab_equity, config.sql_tab_quote, code)

        c.execute(sql)
        price_divisor_infos = []
        r = c.fetchall()
        for price_divisor_info in r:
            if not price_divisor_info or not price_divisor_info['price_divisor_date']:
                continue
            price_divisor_infos.append(price_divisor_info)
        return price_divisor_infos


# insert new row
# stock_list[(code, name), ...]
def save_stock_list_into_db(stock_list):
    with mysqlcli.get_cursor() as cursor:
        sql_str = u"INSERT IGNORE INTO basic_info (code, name) VALUES (%s, %s)"
        value_list = []
        for code, name in stock_list:
            value_list.append((code, name))

        try:
            cursor.executemany(sql_str, value_list)
        except pymysql.err.IntegrityError as e:
            pass
        except Exception as e:
            print(e)


# update old row
# stock_list[(code, name), ...]
def upsert_stock_list_into_db(stock_list, ignore=True):
    with mysqlcli.get_cursor() as cursor:
        # # not all arguments converted during string formatting
        # sql_fmt = u"INSERT INTO basic_info (code, name) VALUES (%s, %s) ON DUPLICATE KEY update name = %s"
        # sql = sql_fmt
        # cursor.executemany(sql, [(code, name, name) for code, name in stock_list])
        # return

        # # too slow
        # sql_fmt = u"INSERT INTO basic_info (code, name) VALUES ('{code}', '{name}') ON DUPLICATE KEY update name = '{name}'"
        # for code, name in stock_list:
        #     try:
        #         sql = sql_fmt.format(code=code, name=name)
        #         cursor.execute(sql, None)
        #     except Exception as e:
        #         print(e)  # (1062, "Duplicate entry '603999' for key 'PRIMARY'")

        # Create a new record
        sql_ins = "INSERT INTO basic_info (code, name) VALUES (%s, %s)"
        sql_sel = 'select code, name from basic_info'
        sql_upd = 'update basic_info set name = (%s) where code = (%s)'

        sql = sql_sel
        cursor.execute(sql, None)
        r = cursor.fetchall()
        # existed_stock_list = [(row['code'], row['name']) for row in r]
        existed_stock_map = {row['code']: row['name'] for row in r}
        new_stock_list = []
        update_stock_list = []
        for t in stock_list:
            code = t[0]
            if code not in existed_stock_map:
                new_stock_list.append(t)
                continue

            name = t[1]
            if name != existed_stock_map[code]:
                update_stock_list.append((t[1], t[0]))

            # for t_ in existed_stock_list:
            #     if t_[0] != t[0]:
            #         continue
            #     if t_[1] != t[1]:
            #         update_stock_list.append((t[1], t[0]))
            #     break
            # else:
            #     new_stock_list.append(t)

        if new_stock_list:
            sql = sql_ins
            cursor.executemany(sql, new_stock_list)
            logger.info('[{}] new stock basic info:\n{}'.format(len(new_stock_list), new_stock_list))

        if update_stock_list:
            sql = sql_upd
            cursor.executemany(sql, update_stock_list)
            logger.info('[{}] update stock basic info'.format(len(update_stock_list), update_stock_list))


def get_selected_stock_code():
    code_list = []
    with mysqlcli.get_cursor() as c:
        sql = 'select code from {0}'.format(config.sql_tab_selected)
        c.execute(sql)
        r = c.fetchall()
        for item in r:
            code_list.append(item['code'])
        return code_list


def sum_trade_date(code):
    with mysqlcli.get_cursor() as c:
        sql = 'select count(code) from {0} where code = "{1}"'.format(config.sql_tab_quote, code)
        c.execute(sql)
        r = c.fetchone()
        return list(r.values())[0]


def save_stock_name():
    stock_code_list = get_all_stock_code()
    val_list = []

    conn = mysqlcli.get_connection()
    c = mysqlcli.get_cursor(conn)
    for i, code in enumerate(stock_code_list):
        if i % 3 ==0:
            stock_info = price.getChinaStockIndividualPriceInfo(code)
        elif i % 3 == 1:
            stock_info = price.getChinaStockIndividualPriceInfoTx(code)
        else:
            stock_info = price.getChinaStockIndividualPriceInfoWy(code)

        if not stock_info:
            print(code)
            continue

        try:
            # val_list.append(tuple([code, stock_info['name']]))
            time.sleep(0.1)
            sql = 'insert into {0} (code, name) values ("%s", "%s")'.format(config.sql_tab_basic_info) % tuple([code, stock_info['name']])
            c.execute(sql)
            conn.commit()
        except Exception as e:
            print(e)

    # for val in val_list:
    #     print(val)
    # sql = 'insert into basic_info (code, name) values (%s, %s)'
    # c.executemany(sql, val_list)
    # conn.commit()
    c.close()
    conn.close()


# 没有调用
def update_stock_name():
    stock_code_list = get_all_stock_code()
    val_list = []

    conn = mysqlcli.get_connection()
    c = mysqlcli.get_cursor(conn)
    for i, code in enumerate(stock_code_list):
        try:
            code_i = int(code)
            if code_i >= 600000:
                continue
            # val_list.append(tuple([code, stock_info['name']]))
            sql = 'update {0} set code = "%s" where code = "%d"'.format(config.sql_tab_basic_info) % tuple([code, code_i])
            c.execute(sql)
            conn.commit()
        except Exception as e:
            print(e)

    # for val in val_list:
    #     print(val)
    # sql = 'insert into basic_info (code, name) values (%s, %s)'
    # c.executemany(sql, val_list)
    # conn.commit()
    c.close()
    conn.close()


def get_stock_code(name):
    with mysqlcli.get_cursor() as c:
        try:
            sql = "select code from {0} where type = 'A' and name like '{1}%'".format(config.sql_tab_basic_info, name)
            c.execute(sql)
            # name = c.fetchall()
            r = c.fetchone()
            return r['code']
        except Exception as e:
            print(e)


def get_stock_name(code):
    with mysqlcli.get_cursor() as c:
        try:
            sql = 'select name from {0} where code = "{1}"'.format(config.sql_tab_basic_info, code)
            c.execute(sql)
            # name = c.fetchall()
            r = c.fetchone()
            return r['name']
        except Exception as e:
            print(e)


def get_future_name(code):
    if code.find('1') > 0:
        code = code[:-4]
    elif code[-1] == '0':
        code = code[:-1]

    with mysqlcli.get_cursor() as c:
        try:
            sql = 'select name from future_variety where code = "{1}"'.format(config.sql_tab_basic_info, code)
            c.execute(sql)
            # name = c.fetchall()
            r = c.fetchone()
            return r['name']
        except Exception as e:
            print(e)


if __name__ == '__main__':
    upsert_stock_list_into_db([('300502', 'ABC')])
    # exit(0)
    # pass
    # add_selected_history('600674')
    # exit(0)
    # print(get_stock_name('600839'))
    # exit(0)
    # add_bought('600839')
    # add_cleared('600839')
    # r = get_to_clear()
    # print(r)
    # add_trade('600839', 'B', 1, 100)
    # print(get_code_list_monitored())
    # print(sum_trading_date('600839'))
    # add_monitor('600839')
    # update_stock_name()
