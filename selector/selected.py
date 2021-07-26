# -*- coding: utf-8 -*-

from util import mysqlcli
from config import config


def add_selected_history(code, cls):
    with mysqlcli.get_cursor() as c:
        sql = 'select added_date, status, class, rank from portfolio_history where code = %s and class = %s order by added_date desc'
        c.execute(sql, (code, cls))
        r = c.fetchone()
        if not r:
            return

        sql = 'insert into portfolio_history (code, added_date, status, class, rank) values(%s, %s, %s, %s, %s)'
        c.execute(sql, (code, str(r['added_date']), r['status'], r['class'], r['rank']))


def remove_selected(code, cls):
    with mysqlcli.get_cursor() as c:
        sql = 'delete from portfolio where code = %s and class = %s'
        c.execute(sql, (code, cls))


def remove_selected_keep_history(code, cls):
    with mysqlcli.get_cursor() as c:
        add_selected_history(code, cls)
        sql = 'delete from portfolio where code = %s and class = %s'
        c.execute(sql, (code, cls))


# HP, 横盘
def add_selected(code, cls='hp', rank=9):
    with mysqlcli.get_cursor() as c:
        sql = 'select added_date from portfolio where code = %s and class = %s order by added_date desc'
        c.execute(sql, (code, cls))
        r = c.fetchone()
        if r:
            import datetime
            # r['added_date'], datetime.date
            #tm = time.strptime(r['added_date'], '%Y-%m-%d')
            #t = time.mktime(tm)
            #d = datetime.date.fromtimestamp(t)
            # datetime.timedelta
            if (datetime.date.today() - r['added_date'].date()).days <= 5:
                return
            remove_selected_keep_history(code, cls)
        sql = 'insert into portfolio (code, added_date, status, class, `rank`) values(%s, current_date(), %s, %s, %s)'
        # code varchar(8), added_date date, class varchar(8), rank integer
        c.execute(sql, (code, 'allow_buy', cls, rank))
