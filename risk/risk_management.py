# -*- coding: utf-8 -*-
import xlrd


def save_account_data(xlsfile):
    data = xlrd.open_workbook(xlsfile)  # 注意这里的workbook首字母是小写

    # 查看文件中包含sheet的名称
    sheets = data.sheet_names()
    sheet = sheets[0]

    # 得到第一个工作表，或者通过索引顺序 或 工作表名称
    table = data.sheets()[0]
    table = data.sheet_by_index(0)
    table = data.sheet_by_name(sheet)

    # if not check_format(table.row_values(1)):
    #     raise Exception('xls format changed...')

    # 获取行数和列数
    # nrows = table.nrows
    # ncols = table.ncols
    # 获取整行和整列的值（数组）
    # 循环行,得到索引的列表
    trade_date = None
    # ['数据更新时间', '12-25 15:15:12', '', '', '', '', '', '', '', '', '', '', '']
    update_day = table.row_values(0)[1].split()[0]
    # if dt == None:
    #     dt = str(datetime.date.today())
    # if dt.find(update_day) < 0:
    #     print(dt, update_day, 'not today\'s quote')
    #     #os.remove(xlsfile)
    #     return

    # trade_date = get_trade_date_from_str(update_day)
    val_many = []
    for rownum in range(table.nrows):
        row = table.row_values(rownum)
        # if not row[0].startswith('s'):
