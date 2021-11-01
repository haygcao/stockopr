# encoding=utf-8

"""
按季度
"""

import datetime
import json
import os
import random
import time

import pandas
import requests
import sqlalchemy

from acquisition import basic
from config import config
from util import util, mysqlcli
from util.log import logger

url_tpl = 'http://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYZBAjaxNew?type={}&code={}'


def clear_finance(report_date):
    with mysqlcli.get_cursor() as c:
        if report_date:
            sql = 'delete from finance where report_date = %s'
            c.execute(sql, (report_date,))
        else:
            sql = 'truncate table finance'
            c.execute(sql)


def get_finance_dir():
    root_dir = util.get_root_dir()
    finance_dir = os.path.join(root_dir, 'data', 'finance')
    if not os.path.exists(finance_dir):
        os.makedirs(finance_dir)
    return finance_dir


def cache_exists(code, report_date):
    finance_dir = get_finance_dir()
    last_report_date = get_last_report_date() if not report_date else report_date
    data_json = os.path.join(finance_dir, last_report_date.strftime('%Y%m%d'), '{}.json'.format(code))
    existed = os.path.exists(data_json)
    return existed


def get_last_report_date():
    # return datetime.date(2021, 9, 30)

    today = datetime.date.today()
    month = today.month
    year = today.year

    # 10月底出三季报
    if month > 10:
        return datetime.date(year, 9, 30)
    # 8月底出半年报
    if month > 8:
        return datetime.date(year, 6, 30)
    # 4月底出一季报和上年报
    if month > 4:
        return datetime.date(year, 3, 31)

    # 上年三季报
    return datetime.date(year - 1, 9, 30)


def fetch_finance_stock_impl(code, report_date):
    result = None
    data_list = []
    last_report_date = get_last_report_date() if not report_date else report_date

    finance_dir = get_finance_dir()
    data_json = os.path.join(finance_dir, last_report_date.strftime('%Y%m%d'), '{}.json'.format(code))
    cache_ = os.path.join(finance_dir, '{}_xxx-{}.json'.format(code, last_report_date.strftime('%Y%m%d')))

    if not os.path.exists(cache_):
        logger.info('{} not cached, requests'.format(code))
        market = 'SH' if code.startswith('6') else 'SZ'
        url = url_tpl.format(2, '{}{}'.format(market, code))
        r = requests.get(url)

        d = json.loads(r.text)
        if 'data' not in d:
            logger.info('{} fetch data error'.format(code))
            return

        data_list = d['data']
        with open(cache_, 'w') as f:
            f.write(r.text)

    # if not os.path.exists(data_json):
        for data in data_list:
            date = datetime.datetime.strptime(data['REPORT_DATE'], '%Y-%m-%d %H:%M:%S').date()
            json_ = os.path.join(finance_dir, date.strftime('%Y%m%d'), '{}.json'.format(code))
            if os.path.exists(json_):
                continue

            dir_ = os.path.dirname(json_)
            if not os.path.exists(dir_):
                os.makedirs(dir_)

            with open(json_, 'w') as f:
                json.dump(data, f, indent=4, cls=util.DateEncoder)

    if report_date:
        # 尚未发过报表
        if not os.path.exists(data_json):
            return

        with open(data_json, 'r') as f:
            data = json.load(f)
            data_list = [data]
    elif not data_list:
        with open(cache_, 'r') as f:
            d = json.load(f)
            if 'data' not in d:
                os.remove(cache_)
                logger.info('{} cache error, remove'.format(code))
                return
            data_list = d['data']



    columns = [
        'SECURITY_CODE', 'REPORT_DATE',
        'EPSJB', 'BPS', 'PER_CAPITAL_RESERVE', 'PER_UNASSIGN_PROFIT', 'PER_NETCASH',
        'TOTALOPERATEREVE', 'GROSS_PROFIT', 'PARENTNETPROFIT', 'DEDU_PARENT_PROFIT',
        'TOTALOPERATEREVETZ', 'PARENTNETPROFITTZ', 'DPNP_YOY_RATIO',
        'ROE_DILUTED', 'JROA', 'NET_PROFIT_RATIO', 'GROSS_PROFIT_RATIO'
    ]
    for data in data_list:
        df = pandas.DataFrame(data, index=[data['REPORT_DATE']], columns=columns)

        if not isinstance(result, pandas.DataFrame):
            result = df
        else:
            result = result.append(df)

    result.rename(columns={
        'SECURITY_CODE': 'CODE',
        'EPSJB': 'EPS',
        'TOTALOPERATEREVETZ': 'TOTALOPERATEREVE_YOY_RATIO',
        'PARENTNETPROFITTZ': 'PARENTNETPROFIT_YOY_RATIO',
    }, inplace=True)

    return result


def fetch_finance_stock(code, report_date):
    try:
        return fetch_finance_stock_impl(code, report_date)
    except Exception as e:
        finance_dir = get_finance_dir()
        log = 'exception_xxx-{}.log'.format((report_date if report_date else get_last_report_date()).strftime('%Y%m%d'))
        with open(os.path.join(finance_dir, log), 'a') as f:
            f.writelines('{} - {}_{}: {}\n'.format(datetime.datetime.now(), code, report_date, e))


def save_finance_from_csv(csv):
    result = pandas.read_csv(csv, index_col=0, dtype={'CODE': str})
    engine = sqlalchemy.create_engine(
        'mysql+pymysql://{0}:{1}@127.0.0.1:3306/stock?charset=utf8mb4'.format(config.db_user, config.db_passwd))
    result.to_sql(name='finance', con=engine, if_exists='append', index=False, chunksize=20000)
    return


def repair(report_date):
    result = pandas.DataFrame()
    finance_dir = get_finance_dir()
    with open(os.path.join(finance_dir, 'not_issue_{}'.format(report_date.strftime('%Y%m%d')))) as f:
        for code in f:
            code = code.strip()
            cache_ = os.path.join(finance_dir, '{}_xxx-{}.json'.format(code, report_date.strftime('%Y%m%d')))
            if os.path.exists(cache_):
                os.remove(cache_)

            df = fetch_finance_stock(code, report_date)
            if not isinstance(df, pandas.DataFrame):
                logger.info('{} no report'.format(code))
                continue

            result = result.append(df)

    engine = sqlalchemy.create_engine(
        'mysql+pymysql://{0}:{1}@127.0.0.1:3306/stock?charset=utf8mb4'.format(config.db_user, config.db_passwd))
    result.to_sql(name='finance', con=engine, if_exists='append', index=False, chunksize=20000)


def save_finance(report_date):
    finance_dir = get_finance_dir()
    date = report_date if report_date else get_last_report_date()
    date_str = date.strftime('%Y%m%d')
    date_in_filename = date_str if report_date else 'xxx-{}'.format(date_str)

    clear_finance(report_date)

    # report_date = get_last_report_date() if not report_date else report_date

    result = None
    code_list = basic.get_all_stock_code()
    # code_list = ['301091']
    for code in code_list:
        if code[0] not in '036':
            logger.info('{} not A'.format(code))
            continue
        existed = cache_exists(code, report_date)
        if not existed:
            logger.info('{} current season not cached'.format(code))
            time.sleep(random.randint(0, 3))

        df = fetch_finance_stock(code, report_date)
        if not isinstance(df, pandas.DataFrame):
            logger.info('{} no report'.format(code))
            continue
        if not isinstance(result, pandas.DataFrame):
            result = df
        else:
            result = result.append(df)

        existed = cache_exists(code, report_date)
        if not existed:
            name = basic.get_stock_name(code)
            logger.info('{} {}, no current season report'.format(code, name))

            log = os.path.join(finance_dir, 'not_issue_{}'.format(date_str))
            if not name.startswith('退市') and not name.endswith('退'):
                with open(log, 'a') as f:
                    f.writelines('{}\n'.format(code))

    csv = '{}.csv'.format(date_in_filename)
    result['CODE'] = result['CODE'].astype(str)
    result.to_csv(os.path.join(finance_dir, csv), )

    engine = sqlalchemy.create_engine(
        'mysql+pymysql://{0}:{1}@127.0.0.1:3306/stock?charset=utf8mb4'.format(config.db_user, config.db_passwd))
    result.to_sql(name='finance', con=engine, if_exists='append', index=False, chunksize=20000)
