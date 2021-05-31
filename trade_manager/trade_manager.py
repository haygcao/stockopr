# -*- coding: utf-8 -*-
import datetime

from acquisition import tx, quote_db
from config import config
from data_structure import trade_data
from indicator import atr, ema
from pointor import signal
from toolkit import tradeapi
from util import mysqlcli, macd


# from util.log import logger


def query_quota_position(code):
    with mysqlcli.get_cursor() as c:
        # sql = 'SELECT DISTINCT code FROM {0}'.format(config.sql_tab_quote)
        sql = "SELECT `position` FROM {0} where code = '{1}'  order by date desc limit 1".format(config.sql_tab_trade_order, code)
        c.execute(sql)
        postion = c.fetchone()

        return int(postion['position'])


def query_trade_order_list(code=None):
    with mysqlcli.get_cursor() as c:
        sql = "SELECT code, position, open_price, stop_loss, stop_profit FROM {0} where status = 'ING'".format(config.sql_tab_trade_order)
        if code:
            sql += " and code = {}".format(code)

        c.execute(sql)
        ret = c.fetchall()
        order_list = []
        for row in ret:
            trade_order = trade_data.TradeOrder(row['code'], int(row['position']), float(row['open_price']), float(row['stop_loss']), float(row['stop_profit']))
            order_list.append(trade_order)

        return order_list


def query_total_risk_amount():
    total_loss = 0
    with mysqlcli.get_cursor() as c:
        sql = "SELECT code, (position * (open_price - stop_loss)) as loss FROM {0} where status = 'ING'".format(config.sql_tab_trade_order)

        c.execute(sql)
        ret = c.fetchall()
        for row in ret:
            code, loss = row['code'], float(row['loss'])
            total_loss += loss

        return total_loss


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
    operation = tradeapi.OperationThs()
    money = operation.get_asset()
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


def buy(code, count=0, price=0):
    position_quota = query_quota_position(code)
    position = query_position(code)
    current_position = position.current_position

    avail_position = position_quota - current_position
    if avail_position < 100:
        return

    trade = config.config.get_trade_config(code)
    if count == 0:
        count = trade['count']
    auto = trade['auto_buy']

    count = min(avail_position, count)
    order('B', code, count, price, auto=auto)


def sell(code, count, price=0):
    position = query_position(code)
    current_position = position.current_position
    avail_position = position.avail_position

    to_position = ((current_position / 2) // 100) * 100
    to_position = min(avail_position, to_position)

    trade = config.config.get_trade_config(code)
    if count == 0:
        count = trade['count']
    auto = trade['auto_sell']

    count = min(to_position, count)
    order('S', code, count, price, auto=auto)


def order(direct, code, count, price=0, auto=False):
    tradeapi.order(direct, code, count, price, auto)


def compute_stop_profit(quote):
    quote = atr.compute_atr(quote)
    quote = ema.compute_ema(quote)
    series_atr = quote['atr']
    series_ema = quote['ema26']   # wrong
    # series_ema = quote['close'].ewm(span=26, adjust=False).mean()
    # series_ema = macd.ema(quote, 26)['ema']
    index = -2 if datetime.date.today().weekday() < 4 else -1
    last_diff = series_atr[index] - series_atr[index - 1]
    stop_profit = series_ema[index] + (series_atr[index] + last_diff) * 3

    return stop_profit


def create_trade_order(code):
    """
    单个股持仓交易风险率 <= 1%
    总持仓风险率 <= 6%
    """
    quote = tx.get_kline_data(code, 'day')
    quote_week = quote_db.get_price_info_df_db_week(quote, period_type=config.period_map['day']['long_period'])

    quote = signal.compute_signal(quote, 'day')
    price = quote['close'].iloc[-1]
    stop_loss = quote['stop_loss_full'].iloc[-1]

    money = query_money()
    total_money = money.total_money

    loss = total_money * 0.01
    total_loss_used = query_total_risk_amount()
    total_loss_remain = total_money * 0.06 - total_loss_used

    loss = min(loss, total_loss_remain)
    position = loss / (price - stop_loss) // 100 * 100
    if position < 100:
        return

    stop_profit = compute_stop_profit(quote_week)

    val = [datetime.date.today(), code, position * price, position, price, stop_loss, stop_profit,
           (position * price) / total_money, (stop_profit - price) / (price - stop_loss), 'ING']

    val = tuple(val)

    keys = ['date', 'code', 'capital_quota', '`position`', 'open_price', 'stop_loss', 'stop_profit', 'risk_rate', 'profitability_ratios', 'status']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)
    sql = "insert into {} ({}) values ({})".format(config.sql_tab_trade_order, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, val)
        except Exception as e:
            print(e)


def handle_excess(code):
    pass
    # logger.warn('{} excess...'.format(code))


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
