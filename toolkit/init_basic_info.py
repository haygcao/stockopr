#-*- coding: utf-8 -*-
from util import tx
from acquisition import basic

if __name__ == '__main__':
    stock_list = tx.get_stock_list()
    print(stock_list)
    basic.save_stock_list_into_db(stock_list)
