# -*- encoding: utf-8 -*-

from util import mysqlcli


def save_index_info():
    index_info_list = []
    with open(r"C:\new_tdx\T0002\hq_cache\tdxzs.cfg") as f:
        for line in f:
            index_info_list.append(line.strip().split('|'))

    val_list = [tuple(zs_info) for zs_info in index_info_list]
    with mysqlcli.get_cursor() as c:
        try:
            # 半导体|880491|2|1|1|T1203
            # 半导体|880630|8|1|0|270100
            # 芯片|880952|4|1|0|芯片
            key_list = ['name', 'code', 'type', 'major', 'minor', 'industry']
            fmt_list = ['%s' for _ in key_list]

            key = ', '.join(key_list)
            fmt = ', '.join(fmt_list)
            sql = "insert into index_info ({}) values ({})".format(key, fmt)
            c.executemany(sql, val_list)

        except Exception as e:
            print('save equity', e)


def update_stock_index_info():
    industry_info_list = []
    with open(r"C:\new_tdx\T0002\hq_cache\tdxhy.cfg") as f:
        for line in f:
            industry_info_list.append(line.strip().split('|'))

    with mysqlcli.get_cursor() as cursor:
        # Create a new record
        sql = 'select code from basic_info where industry_tdx is null'
        cursor.execute(sql)
        r = cursor.fetchall()
        code_list_in_db = [row['code'] for row in r if len(row['code']) == 6]
        if not code_list_in_db:
            return

        # 0|300839|T010302|220101|H010302
        # 1|600536|T1205|470302|H140501
        sql = u"update basic_info set industry_tdx = %s, industry_zjh = %s, industry_sw = %s where code = %s"
        val_list = [(i1, i2, i3, code) for _, code, i1, i2, i3 in industry_info_list if code in code_list_in_db]

        try:
            cursor.executemany(sql, val_list)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # save_index_info()
    update_stock_index_info()
