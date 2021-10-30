# encoding=utf-8
import datetime
import json

import pandas
import requests

url_tpl = 'http://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYZBAjaxNew?type={}&code={}'


def fetch_finance_stock(code, report_date=None):
    date = datetime.date(2021, 9, 30) if not report_date else report_date

    result = None
    market = 'SH' if code.startswith('600') else 'SZ'
    url = url_tpl.format(2, '{}{}'.format(market, code))

    import os
    cache = 'finance_{}_{}.json'.format(code, date)
    if not os.path.exists(cache):
        r = requests.get(url)
        with open(cache, 'w') as f:
            f.write(r.text)
    with open(cache, 'r') as f:
        data_list = json.load(f)['data']

    for data in data_list:
        if report_date and datetime.datetime.strptime(data['REPORT_DATE'], '%Y-%m-%d %H:%M:%S').date() != report_date:
            # continue
            pass

        j = json.dumps(data)
        df = pandas.DataFrame(data, index=['REPORT_DATE'])

        if not isinstance(result, pandas.DataFrame):
            result = df
        else:
            result = result.append(df)

    return result


def save_finance(report_date):
    pass
