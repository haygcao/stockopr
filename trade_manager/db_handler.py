import datetime

from config import config
from data_structure import trade_data
from util import mysqlcli


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
    keys = ['date', 'total', 'avail']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    val = (datetime.datetime.now(), money.total_money, money.avail_money)

    sql = "insert into {} ({}) values ({})".format(config.sql_tab_asset, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, val)
        except Exception as e:
            print(e)


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


def save_position(position: trade_data.Position):
    keys = ['date', 'code', 'total', 'avail']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    val = (datetime.datetime.now(), position.code, position.current_position, position.avail_position)

    sql = "insert into {} ({}) values ({})".format(config.sql_tab_position, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, val)
        except Exception as e:
            print(e)


def query_operation_details(code, date: datetime.date = None):
    sql = "select time, price, count from {} where".format(config.sql_tab_operation_detail)
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
        detail = trade_data.OperationDetail(row['time'], code, float(row['price']), int(row['count']))
        details.append(detail)

    return details


def save_operation_details(details: list[trade_data.OperationDetail]):
    keys = ['time', 'code', 'operation', 'price', 'count', 'amount', 'cost']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)

    val_list = []
    for detail in details:
        val = (detail.trade_time, detail.code, detail.operation, detail.price, detail.count, detail.amount, detail.cost)
        val_list.append(val)

    sql = "insert ignore into {} ({}) values ({})".format(config.sql_tab_operation_detail, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            c.executemany(sql, val_list)
        except Exception as e:
            print(e)
