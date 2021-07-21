# coding:utf-8
import os.path

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import random
import datetime
import sys

# http://npm.taobao.org/mirrors/chromedriver

# TODO
# http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=000001&topline=10&year=2019&month=&rt=
import util.util

sys.path.append(".")
import util.mysqlcli as mysqlcli

# coding:utf-8
import requests
from lxml import etree


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
}

# 84.0.4147.30
# 85.0.4183.38


def init_fund_code(date):
    url = 'http://fund.eastmoney.com/allfund.html'
    html = requests.get(url, headers=headers)
    html.encoding = 'gbk'
    document = etree.HTML(html.text)

    info = document.xpath('// *[ @ id = "code_content"] / div / ul / li / div / a[1] /text()')

    code_list = []
    for fund in info:
        str = fund.split('）')[0]
        code = str.split('（')[1]

        code_list.append(code)

    print('{} funds'.format(len(code_list)))

    with open('fund.txt', 'w') as f:
        for code in code_list:
            f.writelines(code)
            f.write('\n')

    insert_fund_code(code_list, date)


def query_fund_code(date):
    code_list = []
    sql_str = 'select code from fund_basic where date = %s and scale is NULL order by code'
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql_str, (date,))
            r = c.fetchall()
            for row in r:
                code_list.append(row['code'])
        except Exception as e:
            print(e)
    return code_list


def query_last_date(date):
    sql_str = 'select max(date) date from fund_basic where date = %s'
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql_str, (date, ))
            r = c.fetchone()
            date = r['date']
        except Exception as e:
            print(e)
    return date


def insert_into_fund_stock(data_arr):
    key_list = ['fund_code', 'fund_date', 'code', 'percent', 'price', 'num', 'market_value', 'fund_url', 'crawl_date']
    fmt_list = ['%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s']
    key = ', '.join(key_list)
    fmt = ', '.join(fmt_list)
    sql_str = 'insert ignore into fund_stock ({0}) values ({1})'.format(key, fmt)
    # val_list = [data[key] for key in key_list]
    val_list_arr = [[data[key] for key in key_list] for data in data_arr]
    with mysqlcli.get_cursor() as c:
        try:
            c.executemany(sql_str, val_list_arr)
        except Exception as e:
            print(e)


def insert_fund_code(code_list, date):
    sql_str = 'insert ignore into fund_basic (code, date) values (%s, %s)'
    val_list = [(code, date) for code in code_list]
    with mysqlcli.get_cursor() as c:
        try:
            c.executemany(sql_str, val_list)
        except Exception as e:
            print(e)


def insert_or_update_into_fund_basic(data):
    # sql_str = 'insert ignore into fund_basic (code, name, scale) values (%s, %s, %s)'
    sql_str = 'insert ignore into fund_basic (code, name, scale, date) values (%s, %s, %s, %s) as alias ON DUPLICATE KEY UPDATE scale=alias.scale, name=alias.name'
    key_list = ['fund_code', 'fund_name', 'scale', 'last_date']
    val_list = [data[key] for key in key_list]
    with mysqlcli.get_cursor() as c:
        try:
            c.executemany(sql_str, [val_list])
        except Exception as e:
            print(e)


def exists_fund_stock(fund_code, date):
    sql_str = 'select count(1) count from fund_stock where fund_code = %s and fund_date = %s'
    sql_str = 'select scale count from fund_basic where code = %s and date = %s'
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql_str, (fund_code, date))
            r = c.fetchone()

            return r['count']
        except Exception as e:
            print(e)


def get_info(code, date):
    root_dir = util.util.get_root_dir()
    html_path = os.path.join(root_dir, 'data', 'html', '{}.html'.format(code))

    if not os.path.exists(html_path):
        url = 'http://fundf10.eastmoney.com/ccmx_%s.html' % code
        print(url)
        opt = webdriver.ChromeOptions()
        opt.set_headless()
        driver = webdriver.Chrome(options=opt)
        driver.maximize_window()
        driver.get(url)
        driver.implicitly_wait(5)
        day = datetime.date.today()
        today = '%s' % day

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
            f.flush()

    file = open(html_path, 'r', encoding='utf-8')
    soup = BeautifulSoup(file, 'lxml')

    try:
        fund = soup.select('#bodydiv > div > div > div.basic-new > div.bs_jz > div.col-left > h4 > a')[0].get_text()
        fund_code = fund.split(' (')[1][:-1]
        fund_name = fund.split(' (')[0]
        scale_date = soup.select('#bodydiv > div > div.r_cont > div.basic-new > div.bs_gl > p > label > span')[2].get_text().strip().split()
        scale = scale_date[0]
        ind = scale.find('亿元')
        scale = scale[:ind] if ind > 0 else '0'

        import re
        date_str = re.match('.*([0-9]{4}-[0-9]{2}-[0-9]{2}).*', scale_date[1]).group(1)
        # fund_date_max = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        fund_date_max = datetime.date.fromisoformat(date_str)
        if fund_date_max < date:
            with open('fund_not_updated.txt', 'a+') as f:
                f.write(url + '\n')
            return

        table = soup.select('#cctable > div > div > table')
        h4 = soup.select('#cctable > div > div > h4')

        # import pdb; pdb.set_trace()
        data_arr = []
        for i in range(len(table)):
            fund_date_str = h4[i].select('label > font')[0].text
            fund_date = datetime.date.fromisoformat(fund_date_str)
            if fund_date != date:
                continue
            trs = table[i].select('tbody > tr')

            for tr in trs:
                td_code_name = tr.select('td > a')
                if not td_code_name:
                    td_code_name = tr.select('td > span')
                if td_code_name:
                    code = td_code_name[0].get_text()
                    name = td_code_name[1].get_text()
                else:
                    continue

                if i == 0:
                    index = [2, 3, 4]
                    price = tr.select('td > span')[0].get_text()
                    item = tr.select('td.tor')
                    if not item:
                        item = tr.select('td.toc')
                        index = [4, 5, 6]
                    procent = item[index[0]].get_text()
                    num = item[index[1]].get_text()
                    market = item[index[2]].get_text()
                else:
                    index = [0, 1, 2]
                    price = 0
                    item = tr.select('td.tor')
                    if not item:
                        item = tr.select('td.toc')
                        index = [2, 3, 4]
                    procent = item[index[0]].get_text()
                    num = item[index[1]].get_text()
                    market = item[index[2]].get_text()
                try:
                    round(float(price), 2)
                except ValueError:
                    price = 0

                data = {
                    'crawl_date': today,
                    'fund_code': fund_code,
                    'fund_date': fund_date,
                    'fund_name': fund_name,
                    'scale': scale,
                    'code': code,
                    'percent': procent[:-1],
                    'name': name,
                    'price': str(round(float(price), 2)),
                    'num': str(round(float(num.replace(',', '')), 2)),
                    'market_value': str(round(float(market.replace(',', '')), 2)),
                    'fund_url': url
                }
                data_arr.append(data)

        if len(data_arr) == 0:
            return

        insert_into_fund_stock(data_arr)
        data = {
            'fund_code': fund_code,
            'last_date': date,
            'fund_name': fund_name,
            'scale': scale
        }
        insert_or_update_into_fund_basic(data)

    except IndexError as e:
        import traceback
        traceback.print_stack()
        print(e)
        with open('fund_code_no_stock.txt', 'a+') as f:
            f.write(url + '\n')


if __name__ == "__main__":
    # get_info('http://fundf10.eastmoney.com/ccmx_000001.html')
    # exit(0)

    date = datetime.date(2021, 3, 31)
    date = datetime.date(2021, 6, 30)

    date_db = query_last_date(date)
    if not date_db or date_db < date:
        init_fund_code(date)

    # with open('fund_code_no_stock_in.txt') as f:
    #     import re
    #     for line in f:
    #         r = re.match('http://fundf10.eastmoney.com/ccmx_([0-9]{6}).html', line)
    #         code = r.group(1)
    #         get_info(code, date)
    # exit(0)

    code_list = query_fund_code(date)
    # code_list = ['000001']
    for code in code_list:
        # if exists_fund_stock(code, date):
        #     continue
        get_info(code, date)
        time.sleep(random.randint(0, 2))

    # begin = False
    # with open('fund.txt', 'r') as f:
    #     i = 0
    #     for code in f.readlines():
    #         if code.startswith('BEGIN'):
    #             begin = True
    #             continue
    #
    #         if not begin:
    #             continue
    #
    #         get_info(code, date)
    #         time.sleep(random.randint(0, 2))
    #         i = i + 1
    #     print('run times:', i)
