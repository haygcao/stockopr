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


def query_position():
    pass


def save_position():
    pass
