# -*- encoding:utf-8 -*-
import datetime
import sys
import time
import os
from queue import Empty
from multiprocessing import Queue, Process

import pymysql.cursors

sys.path.append(".")

import util.mysqlcli as mysqlcli
import acquisition.basic as basic

db = 'stock'
# csv 文件命名规则: sh#600000.csv sz#000001.csv


def get_file_list(stock_list):
    file_list = []

    for stock in stock_list:
        code_str = stock
        file_csv = 'data/csv/{0}.csv'.format(code_str)
        file_list.append(file_csv)

    return file_list


def get_file_list_orig(stock_list):
    file_list = []

    for stock in stock_list:
        code = int(stock['code'])
        ex = 'sh' if code >= 600000 else 'sz'

        code_str = stock['code']
        file_csv = '{1}#{0}.csv'.format(code_str, ex) # sh#600001
        file_list.append(file_csv)

    return file_list


def get_symbol_from_filename(filename):
    symbol = filename.split('.')[0]
    symbol = symbol.split('/')[-1]

    return symbol


def gen_stock_code(symbol):
    return symbol

    code = int(symbol)
    ex = '0' if code >= 600000 else '1'

    return ex+symbol


def save(csv_queue):
    ok = False
    start_date = datetime.datetime(2010, 1, 1)
    start_date = datetime.datetime(2021, 4, 29)

    while True:
        with mysqlcli.get_cursor() as c:
            try:
                file_csv = csv_queue.get_nowait()
                print(file_csv)

                symbol = get_symbol_from_filename(file_csv)
                code = gen_stock_code(symbol)

                with open(file_csv, 'r', encoding='gbk') as fp:
                    val_many = []

                    # key_list = ['code', 'trade_date', 'close', 'high', 'low', 'open', 'yestclose', 'updown', 'percent', 'hs', 'volume', 'amount', 'tcap', 'mcap']
                    key_list = ['code', 'trade_date', 'close', 'high', 'low', 'open', 'yest_close', 'price_change', 'percent', 'quantity_relative_ratio', 'volume', 'amount', 'amplitude']
                    # 日期, 股票代码, 名称, 收盘价, 最高价, 最低价, 开盘价, 前收盘, 涨跌额, 涨跌幅, 换手率, 成交量, 成交金额, 总市值, 流通市值
                    indice = [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # subscript

                    key = ', '.join(key_list)
                    fmt = ', '.join(['%s' for i in range(len(key_list))])
                    sql_str = 'insert into quote({0}) values ({1})'.format(key, fmt)

                    for row in fp:
                        if row.find('股票') >= 0:
                            continue
                        val_list = [code]
                        row = row.split(',')

                        volume = row[11]
                        if int(volume) <= 0:
                            continue

                        trade_date = datetime.datetime.strptime(row[0], '%Y-%m-%d')
                        if trade_date < start_date:
                            continue

                        for idx in indice:
                            val_list.append(row[idx] if row[idx] != 'None' else 0)
                        if float(row[7]) == 0:
                            val_list.append(0.0)
                        else:
                            val_list.append(round((float(row[4])-float(row[5]))/float(row[7])*100,2))
                        val = tuple(val_list)
                        val_many.append(val)

                    c.executemany(sql_str, val_many)

                #time.sleep(1);
            except pymysql.err.IntegrityError as e:
                pass
            except Empty:
                break
            except Exception as e:
                print(e, file_csv)

def get_stock_list_from_file():
    stock_list = []
    with open('data/stock_list.txt', 'r') as fp:
        for stock in fp:
            print(stock)
            print(tuple(stock))
            exit(0)
        stock_list.append(tuple(stock)[0].strip())
    return stock_list


if __name__ == '__main__':
    csv_queue = Queue()

    #stock_list = get_stock_list_from_file()
    stock_list = basic.get_all_stock_code()
    #stock_list = ['600839']
    file_list = get_file_list(stock_list)
    #print(file_list[0])
    #
    for file_csv in file_list:
        if not os.path.exists(file_csv):
            print(file_csv, 'not exist')
            continue
        csv_queue.put(file_csv)
    #csv_queue.put('data/csv/000001.csv')

    nproc_max = 10
    nproc = nproc_max if csv_queue.qsize() > nproc_max else csv_queue.qsize()
    #nproc = 1
    p_list = [Process(target=save, args=(csv_queue,)) for i in range(nproc)]
    [p.start() for p in p_list]
    [p.join() for p in p_list]
