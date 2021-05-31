# -*- coding: utf-8 -*-
from config import config
from toolkit import tradeapi
from util import mysqlcli
from util.log import logger


def query_quota_position(code):
    with mysqlcli.get_cursor() as c:
        # sql = 'SELECT DISTINCT code FROM {0}'.format(config.sql_tab_quote)
        sql = "SELECT `position` FROM {0} where code = '{1}'  order by date desc limit 1".format(config.sql_tab_trade_order, code)
        c.execute(sql)
        postion = c.fetchone()

        return int(postion['position'])


def query_position(code):
    """
    可以卖的股数
    还可以买的股数
    """
    position_list = tradeapi.OperationThs.get_position()
    for position in position_list:
        if position.code != code:
            continue
        return position


def query_money():
    money = tradeapi.OperationThs.get_asset()
    return money[0]


def check_quota(code, direction):
    """
    巡检, 周期巡检超出配额的已有仓位
    """
    current_position = query_position(code)
    quota_position = query_quota_position()
    if current_position.current_position > quota_position:
        return False
    return True


def buy(code, count, price=0):
    position_quota = query_quota_position(code)
    position = query_position(code)
    current_position = position.current_position

    avail_position = position_quota - current_position
    if avail_position < 100:
        return

    count = min(avail_position, count)
    order('B', code, count, price, auto=False)


def sell(code, count, price=0):
    position = query_position(code)
    current_position = position.current_position
    avail_position = position.avail_position

    to_position = ((current_position / 2) // 100) * 100
    to_position = min(avail_position, to_position)

    count = min(to_position, count)
    order('S', code, count, price, auto=False)


def order(direct, code, count, price=0, auto=False):
    tradeapi.order(direct, code, count, price, auto)


def handle_excess(code):
    logger.warn('{} excess...'.format(code))


def patrol():
    operation = tradeapi.OperationThs()
    position_list = operation.get_position()
    for position in position_list:
        quota = query_quota_position(position.code)
        if not quota:
            handle_excess(position.code)
            continue
        if position.current_position > quota:
            handle_excess(position.code)
            continue


if __name__ == '__main__':
    patrol()
