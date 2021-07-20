# coding:utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import random
import datetime
import sys

# http://npm.taobao.org/mirrors/chromedriver

# TODO
# http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=000001&topline=10&year=2019&month=&rt=

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


def query_fund_code():
    code_list = []
    sql_str = 'select code from fund_basic'
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql_str)
            r = c.fetchall()
            for row in r:
                code_list.append(row['code'])
        except Exception as e:
            print(e)
    return code_list


def query_last_date():
    sql_str = 'select max(date) date from fund_basic'
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql_str)
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


def get_info(code, date):
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

    with open('jijin1.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    time.sleep(1)
    file = open('jijin1.html', 'r', encoding='utf-8')
    soup = BeautifulSoup(file, 'lxml')

    try:
        fund = soup.select('#bodydiv > div > div > div.basic-new > div.bs_jz > div.col-left > h4 > a')[0].get_text()
        fund_code = fund.split(' (')[1][:-1]
        fund_name = fund.split(' (')[0]
        scale = soup.select('#bodydiv > div > div.r_cont > div.basic-new > div.bs_gl > p > label > span')[2].get_text().strip().split()[0]
        ind = scale.find('亿元')
        scale = scale[:ind] if ind > 0 else '0'
        fund_date_max = datetime.date(2000, 1, 1)

        table = soup.select('#cctable > div > div > table')
        h4 = soup.select('#cctable > div > div > h4')

        # import pdb; pdb.set_trace()
        data_arr = []
        for i in range(len(table)):
            fund_date_str = h4[i].select('label > font')[0].text
            fund_date = datetime.date.fromisoformat(fund_date_str)
            if fund_date != date:
                continue
            fund_date_max = max(fund_date, fund_date_max)
            trs = table[i].select('tbody > tr')

            for tr in trs:
                code = tr.select('td > a')[0].get_text()
                name = tr.select('td > a')[1].get_text()
                if i == 0:
                    price = tr.select('td > span')[0].get_text()
                    procent = tr.select('td.tor')[2].get_text()
                    num = tr.select('td.tor')[3].get_text()
                    market = tr.select('td.tor')[4].get_text()
                else:
                    price = 0
                    procent = tr.select('td.tor')[0].get_text()
                    num = tr.select('td.tor')[1].get_text()
                    market = tr.select('td.tor')[2].get_text()
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

            if i == 0:
                data = {
                    'fund_code': fund_code,
                    'last_date': fund_date_max,
                    'fund_name': fund_name,
                    'scale': scale
                }
                insert_or_update_into_fund_basic(data)
        insert_into_fund_stock(data_arr)

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

    date_db = query_last_date()
    if not date_db or date_db < date:
        init_fund_code(date)

    code_list = query_fund_code()
    for code in code_list:
        get_info(code, date)
        # time.sleep(random.randint(0, 2))

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
