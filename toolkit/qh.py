#-*- encoding:utf-8 -*-

import xlrd

subscript_zy = 8
subscript_yz = 9

zc = 0
sum_cj = 0
sum_rj = 0

count = 0

#import xlrd
xlsx = 'icbc20130706-20180725.xlsx' # 'C:\\Users\\Kylin\\Desktop\\工商银行.xlsx'
xlsx = 'icbc20130706-20181231.xlsx'
xlsx = 'icbc20130706-20190322.xlsx'
xlsx = 'icbc20130706-20200321.xlsx'
workbook = xlrd.open_workbook(xlsx)
print ("There are {} sheets in the workbook".format(workbook.nsheets))

#
print('日期\t\t出金\t\t入金')
for booksheet in workbook.sheets():
    #print (booksheet.name)
    for row in range(booksheet.nrows):
        #print(booksheet.cell(row, 2).value)
        if type(booksheet.cell(row, 0).value) is not str and booksheet.cell(row, 0).value > 140:
            pass
            #break
        if booksheet.cell(row, 1).value.find('出金') >= 0 or booksheet.cell(row, 1).value.find('入金') >= 0:
            date = booksheet.cell(row, 0).value.strip()
            accout = booksheet.cell(row, 12).value.strip()
            cj = booksheet.cell(row, 8).value.strip()
            rj = booksheet.cell(row, 9).value.strip()
            print('{}\t{}\t\t{}\t\t{}'.format(date, cj, rj, accout))
            #if type(zy) is not str: #无值时为str, 有值时为float
            if len(cj) > 0: #无值时为str, 有值时为float
                sum_cj += float(cj.replace(',', ''))
            #if type(yz) is not str: #无值时为str, 有值时为float
            if len(rj) > 0:
                sum_rj += float(rj.replace(',', ''))
                #sum_yz += booksheet.cell(row, 9).value

            count += 1

            for col in range(booksheet.ncols):
                pass
                break

                print (xlrd.cellname(row, col))
                print (booksheet.cell(row, col).value)

print('')
print('次数:{}\n出金:{}\n入金:{}\n投入:{}\n盈利:{}'.format(count, round(sum_cj, 2), round(sum_rj, 2), round(sum_rj- sum_cj, 2), round(zc + sum_cj - sum_rj, 2)))

exit(0)

import csv

csvfile = 'icbc20130706-20170622.csv'
reader = csv.reader(open(csvfile, 'r'))
i = 0
for line in reader:
    i += 1
    #for unit in line:
    #    print(unit)
    zy = 0
    yz = 0

    for idx in range(len(line)):
        if idx > 0 and (line[1].find('入金') >= 0 or line[1].find('出金') >= 0):
            str_zy = line[subscript_zy].strip() #<class 'str'>
            str_yz = line[subscript_yz].strip() #.split(' ')[0]
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

print('次数:{0}\t入金:{1}\t出金:{2}\t投入资金:{3}'.format( count, sum_yz, sum_zy, round(sum_yz - sum_zy, 2)))

exit(0)
