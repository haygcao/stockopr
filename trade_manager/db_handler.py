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
