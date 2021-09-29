import datetime

from config import config, config as config
from data_structure import trade_data
from server import config as svr_config
from util import mysqlcli, mysqlcli as mysqlcli
from util.log import logger


def query_money(account_id):
    sql = "select date, total, avail from {} where account_id = {} order by date desc limit 1".format(
        config.sql_tab_asset, account_id)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql)
            r = c.fetchone()
        except Exception as e:
            print(e)

    asset = None
    if r:
        asset = trade_data.Asset(r['total'], r['avail'], date=r['date'])

    return asset


def save_money(account_id, money: trade_data.Asset, sync=False):
    if not money:
        return

    keys = ['date', 'period', 'origin', 'total', 'avail', 'market_value', 'position_percent',
            'total_profit', 'total_profit_percent', 'account_id']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    val = (money.date, money.period, money.origin, money.total_money, money.avail_money,
           money.market_value, money.position_percent, money.profit, money.profit_percent, account_id,
           money.total_money, money.avail_money)

    # sql = "insert into {} ({}) values ({})".format(config.sql_tab_asset, key, fmt)
    sql = u"INSERT INTO {} ({}) VALUES ({}) ON DUPLICATE KEY update total = %s, avail = %s".format(config.sql_tab_asset, key, fmt)
    logger.debug(sql)

    with mysqlcli.get_cursor() as c:
        if sync:
            trade_date = money.date
            c.execute("delete from {} where date = %s and account_id = %s".format(config.sql_tab_asset),
                      (trade_date, account_id))
        try:
            c.execute(sql, val)
        except Exception as e:
            print('save money failed -', e)


def new_position(d):
    return trade_data.Position(d['code'], d['total'], d['avail'], d['cost_price'], d['price'], d['total_profit'])


def query_position(account_id, code):
    sql = "select code, total, avail, cost_price, price, total_profit from {} " \
          "where code = %s and account_id = %s order by date desc limit 1".format(config.sql_tab_position)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, (code, account_id))
            r = c.fetchone()
        except Exception as e:
            print(e)

    position = new_position(r)

    return position


def query_current_position(account_id):
    sql = "select code, total, avail, cost_price, price, total_profit from {} " \
          "where account_id = %s and `date` = (select max(`date`) from `position`) order by code".format(
        config.sql_tab_position)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, (account_id, ))
            r = c.fetchall()
        except Exception as e:
            print(e)

    position_list = []
    for row in r:
        position = new_position(row)
        position_list.append(position)

    return position_list


def save_positions(account_id, position_list, sync=False):
    if not position_list:
        return

    keys = ['date', 'code', 'total', 'avail', 'cost_price', 'price', 'cost',
            'market_value', 'total_profit', 'total_profit_percent', 'account_id']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    sql = u"INSERT INTO {} ({}) VALUES ({}) ON DUPLICATE KEY update total = %s, avail = %s".format(
        config.sql_tab_position, key, fmt)
    logger.debug(sql)

    with mysqlcli.get_cursor() as c:
        if sync:
            trade_date = position_list[0].date
            c.execute("delete from {} where account_id = %s and date = %s".format(config.sql_tab_position),
                      (account_id, trade_date))

        for position in position_list:
            val = (position.date, position.code, position.current_position, position.avail_position,
                   position.price_cost, position.price, position.cost, position.market_value,
                   position.profit_total, position.profit_total_percent, account_id,
                   position.current_position, position.avail_position)

            try:
                c.execute(sql, val)
            except Exception as e:
                # executemany failed, not all arguments converted during string formatting
                print('save position failed -', e)


def query_operation_details(account_id, code=None, date: datetime.date = None):
    sql = "select code, time, price, price_trade, price_limited, count from {} where account_id = %s".format(
        config.sql_tab_operation_detail)
    if code:
        sql += " code = '{}'".format(code)
    if date:
        if not sql.endswith('where'):
            sql += ' and'
        sql += " date(time) = '{}'".format(date)
    if sql.endswith('where'):
        sql = sql[:-5]

    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, (account_id, ))
            r = c.fetchall()
        except Exception as e:
            print(e)

    details = []
    for row in r:
        detail = trade_data.OperationDetail(row['time'], row['code'], float(row['price']), float(row['price_trade']),
                                            float(row['price_limited']), int(row['count']))
        details.append(detail)

    return details


def save_operation_details(account_id, details, trade_date=None, sync=False):
    keys = ['time', 'code', 'operation', 'price', 'price_trade', 'price_limited', 'count', 'amount', 'cost', 'account_id']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    val_list = []
    for detail in details:
        val = (detail.trade_time, detail.code, detail.operation, detail.price, detail.price_trade, detail.price_limited,
               detail.count, detail.amount, detail.cost, account_id)
        val_list.append(val)

    sql = "insert ignore into {} ({}) values ({})".format(config.sql_tab_operation_detail, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            if sync:
                sql_delete = "delete from {} where account_id = %s and date(time) = %s".format(config.sql_tab_operation_detail)
                c.execute(sql_delete, (account_id, trade_date))

            if not details:
                return

            c.executemany(sql, val_list)
        except Exception as e:
            logger.info(e)


def update_trade_order_status(account_id, date, code, status):
    sql = "update {} set status = %s " \
          "where account_id = %s and date = %s and code = %s".format(config.sql_tab_trade_order)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, (account_id, date, code, status))
        except Exception as e:
            logger.info(e)


def query_trade_order_map(account_id, code=None, status='ING'):
    with mysqlcli.get_cursor() as c:
        sql = "SELECT date, code, position, open_price, stop_loss, stop_profit FROM {0} " \
              "where account_id = %s and status = '{1}'".format(config.sql_tab_trade_order, status)
        if code:
            sql += " and code = {}".format(code)

        c.execute(sql, (account_id, ))
        ret = c.fetchall()
        order_map = {}
        for row in ret:
            trade_order = trade_data.TradeOrder(row['date'], row['code'], int(row['position']), float(row['open_price']), float(row['stop_loss']), float(row['stop_profit']))
            order_map.update({row['code']: trade_order})

        return order_map


def query_total_risk_amount(account_id):
    total_loss = 0
    with mysqlcli.get_cursor() as c:
        sql = "SELECT code, (position * (open_price - stop_loss)) as loss FROM {0} " \
              "where account_id = %s and status = 'ING'".format(config.sql_tab_trade_order)

        c.execute(sql, (account_id, ))
        ret = c.fetchall()
        for row in ret:
            code, loss = row['code'], float(row['loss'])
            total_loss += loss

        return total_loss


def query_quota_position(account_id, code):
    with mysqlcli.get_cursor() as c:
        # sql = 'SELECT DISTINCT code FROM {0}'.format(config.sql_tab_quote)
        sql = "SELECT `position` FROM {0} " \
              "where account_id = %s and code = '{1}' and status = 'ING' order by date desc limit 1".format(
            config.sql_tab_trade_order, code)
        c.execute(sql, (account_id, ))
        postion = c.fetchone()

        return int(postion['position']) if postion else 0
