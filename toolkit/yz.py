# -*- encoding:utf-8 -*-

import datetime as dt

import xlrd

"""
中信证券
2014-10-21   2015-04-29
2015-10-30   2016-04-11
2016-06-17   2019-12-09
2020-03-17

国金证券
2015-04-23   2016-06-17 (2016-07-28 3.38 的利息)
2019-06-10   重新开始交易

2017-07-03   20181105   万达电影停牌
"""

subscript_zy = 8
subscript_yz = 9

sum_zy = {}
sum_yz = {}

count = {}

xlsx = 'icbc20130706-20210919.xls'
xlsx = 'icbc20130706-20211017.xls'
workbook = xlrd.open_workbook(xlsx)
print("There are {} sheets in the workbook".format(workbook.nsheets))

start_date = dt.date(1986, 12, 12)
end_date = dt.date.today()
#end_date = dt.date(2018, 12, 31)

# 中信证券
start_date = dt.date(2014, 10, 21)
end_date = dt.date(2015, 4, 29)   # -27192.9

start_date = dt.date(2015, 10, 30)
end_date = dt.date(2016, 4, 11)   # 3735.68

start_date = dt.date(2016, 6, 17)
end_date = dt.date(2019, 12, 9)   # -20213.94

start_date = dt.date(2020, 3, 17)   # 资产 4.46
end_date = dt.date(2021, 8, 13)   # 资产 632562.8
zc = 632562.8 - 4.46

start_date = dt.date(1986, 12, 12)
end_date = dt.date(2021, 9, 19)
zc = 252594.95 + 146427.03   # 信用净 + 普通总
end_date = dt.date(2021, 10, 17)
zc = 519313.780
accounts = '中信证券'

# 国金证券
# start_date = dt.date(2015, 4, 23)
# end_date = dt.date(2016, 6, 17)   # -38949.36
# end_date = dt.date(2019, 6, 9)
# zc = 0
#
# start_date = dt.date(2019, 6, 10)
# end_date = dt.date(2021, 8, 13)   # 14524.38
# zc = 45097.23
# accounts = '国金证券'

# ===

# 其他证券
# start_date = dt.date(1986, 12, 12)
# end_date = dt.date.today()

# zc = 0
# accounts = '中信证券 国金证券'

print('日期\t\t证银\t\t银证')
for booksheet in workbook.sheets():
    # print (booksheet.name)
    for row in range(booksheet.nrows):
        # print(booksheet.cell(row, 2).value)
        date = booksheet.cell(row, 0).value
        if type(date) is not str and date > 140:
            print('date {}, continue'.format(date))
            continue
            
        if booksheet.cell(row, 1).value.find('银证') < 0:
            continue
        
        date = dt.datetime.strptime(date.strip(), '%Y-%m-%d').date()
        if date < start_date or date > end_date:
            continue

        date = booksheet.cell(row, 0).value.strip()
        account = booksheet.cell(row, 12).value.strip()
        account = account[:account.index('证券')+2]
        zy = booksheet.cell(row, 8).value.strip()
        yz = booksheet.cell(row, 9).value.strip()
        
        # print('{}\t{}\t\t{}\t\t{}'.format(date, zy, yz, account))
        if account[:4] not in accounts:
            continue

        if account not in sum_zy:
            sum_zy[account] = [0, 0]
        if account not in sum_yz:
            sum_yz[account] = [0, 0]
        if account not in count:
            count[account] = 0

        # if type(zy) is not str: #无值时为str, 有值时为float
        if len(zy) > 0:  # 无值时为str, 有值时为float
            sum_zy[account][0] += float(zy.replace(',', ''))
        if len(yz) > 0:
            sum_zy[account][1] += float(yz.replace(',', ''))

        count[account] += 1

        for col in range(booksheet.ncols):
            pass
            break

            print(xlrd.cellname(row, col))
            print(booksheet.cell(row, col).value)


print('')

all_count = 0
all_zy = [0, 0]

for k, v in sum_zy.items():
    _zc = 0
    all_count += count[k]
    if len(k) == 0:
        continue
    if k.find('中信证券') >= 0:
        # sum_zy[k][0] += sum_zy[''][0]
        # sum_zy[k][1] += sum_zy[''][1]
        # count[k] += count['']
        _zc = zc
    all_zy[0] += sum_zy[k][0]
    all_zy[1] += sum_zy[k][1]

    print('{}\n次数:{}\n银证:{}\n证银:{}\n投入:{}\n盈利:{}'.format(k, count[k], sum_zy[k][0], sum_zy[k][1], round(sum_zy[k][1] - sum_zy[k][0], 2), round(_zc + sum_zy[k][0] - sum_zy[k][1], 2)))
    print('')

print('{}\n次数:{}\n银证:{}\n证银:{}\n投入:{}\n盈利:{}'.format('总计', all_count, round(all_zy[0], 2), round(all_zy[1], 2), round(all_zy[1] - all_zy[0], 2), round(zc + all_zy[0] - all_zy[1], 2)))

exit(0)

'''
'''

import csv

csvfile = 'icbc20130706-20170622.csv'
reader = csv.reader(open(csvfile, 'r'))
i = 0
for line in reader:
    i += 1
    # for unit in line:
    #     print(unit)
    zy = 0
    yz = 0

    for idx in range(len(line)):
        if idx > 0 and line[1].find('银证') >= 0:
            str_zy = line[subscript_zy].strip()  # <class 'str'>
            str_yz = line[subscript_yz].strip()  # .split(' ')[0]
            if len(str_zy) > 0:
                zy = float(str_zy.replace(',', ''))
            if len(str_yz) > 0:
                yz = float(str_yz.replace(',', ''))
            sum_zy += zy
            sum_yz += yz

            count += 1

            break
    #print (line)

    if i == 20:
        pass
        #exit(0)

s = '次数:{0}\t银证:{1}\t证银:{2}\t投入资金:{3}\t盈利:{4}'.format( count, sum_yz, sum_zy, round(sum_yz - sum_zy, 2), round(zc + sum_zy - sum_yz, 2))
print(s)

exit(0)
