import datetime

from config import config, config as config
from data_structure import trade_data
from util import mysqlcli, mysqlcli as mysqlcli
from util.log import logger


def query_money():
    sql = "select total, avail from {} order by date desc limit 1".format(config.sql_tab_asset)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql)
            r = c.fetchone()
        except Exception as e:
            print(e)

    asset = trade_data.Asset(r['total'], r['avail'])

    return asset


def save_money(money: trade_data.Asset):
    if not money:
        return

    keys = ['date', 'total', 'avail']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    val = (money.date, money.total_money, money.avail_money, money.total_money, money.avail_money)

    # sql = "insert into {} ({}) values ({})".format(config.sql_tab_asset, key, fmt)
    sql = u"INSERT INTO {} ({}) VALUES ({}) ON DUPLICATE KEY update total = %s, avail = %s".format(config.sql_tab_asset, key, fmt)
    logger.debug(sql)

    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, val)
        except Exception as e:
            print('save money failed -', e)


def query_position(code):
    sql = "select total, avail from {} where code = %s order by date desc limit 1".format(config.sql_tab_position)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, (code,))
            r = c.fetchone()
        except Exception as e:
            print(e)

    position = trade_data.Position(code, r['total'], r['avail'])

    return position


def query_current_position():
    sql = "select code, total, avail from {} where `date` = (select max(`date`) from `position`)".format(config.sql_tab_position)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql)
            r = c.fetchall()
        except Exception as e:
            print(e)

    position_list = []
    for row in r:
        position = trade_data.Position(row['code'], row['total'], row['avail'])
        position_list.append(position)

    return position_list


def save_positions(position_list: list[trade_data.Position]):
    if not position_list:
        return

    keys = ['date', 'code', 'total', 'avail']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    sql = u"INSERT INTO {} ({}) VALUES ({}) ON DUPLICATE KEY update total = %s, avail = %s".format(
        config.sql_tab_position, key, fmt)
    logger.debug(sql)

    with mysqlcli.get_cursor() as c:
        for position in position_list:
            val = (position.date, position.code, position.current_position, position.avail_position,
                   position.current_position, position.avail_position)

            try:
                c.execute(sql, val)
            except Exception as e:
                # executemany failed, not all arguments converted during string formatting
                print('save position failed -', e)


def query_operation_details(code=None, date: datetime.date = None):
    sql = "select code, time, price, price_trade, price_limited, count from {} where".format(config.sql_tab_operation_detail)
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
            c.execute(sql)
            r = c.fetchall()
        except Exception as e:
            print(e)

    details = []
    for row in r:
        detail = trade_data.OperationDetail(row['time'], row['code'], float(row['price']), float(row['price_trade']),
                                            float(row['price_limited']), int(row['count']))
        details.append(detail)

    return details


def save_operation_details(details: list[trade_data.OperationDetail], sync=False):
    if not details:
        return

    keys = ['time', 'code', 'operation', 'price', 'price_trade', 'price_limited', 'count', 'amount', 'cost']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    val_list = []
    for detail in details:
        val = (detail.trade_time, detail.code, detail.operation, detail.price, detail.price_trade, detail.price_limited,
               detail.count, detail.amount, detail.cost)
        val_list.append(val)

    sql = "insert ignore into {} ({}) values ({})".format(config.sql_tab_operation_detail, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            if sync:
                trade_date = details[0].trade_time.date()
                c.execute("delete from {} where date(time) = {}".format(config.sql_tab_operation_detail, trade_date))
            c.executemany(sql, val_list)
        except Exception as e:
            logger.info(e)


def update_trade_order_status(date, code, status):
    sql = "update {} set status = %s where date = %s and code = %s".format(config.sql_tab_trade_order)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, (date, code, status))
        except Exception as e:
            logger.info(e)


def query_trade_order_map(code=None, status='ING'):
    with mysqlcli.get_cursor() as c:
        sql = "SELECT date, code, position, open_price, stop_loss, stop_profit FROM {0} where status = '{1}'".format(config.sql_tab_trade_order, status)
        if code:
            sql += " and code = {}".format(code)

        c.execute(sql)
        ret = c.fetchall()
        order_map = {}
        for row in ret:
            trade_order = trade_data.TradeOrder(row['date'], row['code'], int(row['position']), float(row['open_price']), float(row['stop_loss']), float(row['stop_profit']))
            order_map.update({row['code']: trade_order})

        return order_map


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


def query_quota_position(code):
    with mysqlcli.get_cursor() as c:
        # sql = 'SELECT DISTINCT code FROM {0}'.format(config.sql_tab_quote)
        sql = "SELECT `position` FROM {0} where code = '{1}' and status = 'ING' order by date desc limit 1".format(config.sql_tab_trade_order, code)
        c.execute(sql)
        postion = c.fetchone()

        return int(postion['position']) if postion else 0