import os
import struct
import datetime


def basic_info(filepath):
    """
    struct TdxSymbolMap {
      char symbol[6];    // 6 digits
      char dummy1[18]
      char name[8];      // 4 characters in GB2312
      char dummy2[218];
    }
    """
    infos = []
    with open(filepath, 'rb') as f:
        # file_object_path = 'D:/new_tdx/quote/sh/' + name +'.csv'
        # file_object = open(file_object_path, 'w+')

        f.seek(50)
        i = 0
        while True:
            line = f.read(314)
            if not line:
                break
            code = line[:6].decode()
            # name = line[23:31]
            name = line[23:55]
            name = name.decode('gbk')
            name = name.strip(b'\x00'.decode())
            i += 1
            print(i, code, name)
            infos.append((code, name))

    return infos


def stock_csv(filepath, name):
    data = []
    with open(filepath, 'rb') as f:
        file_object_path = 'D:/new_tdx/quote/sh/' + name +'.csv'
        file_object = open(file_object_path, 'w+')
        while True:
            stock_date = f.read(4)
            stock_open = f.read(4)
            stock_high = f.read(4)
            stock_low = f.read(4)
            stock_close = f.read(4)
            stock_amount = f.read(4)
            stock_vol = f.read(4)
            stock_reservation = f.read(4)  # date,open,high,low,close,amount,vol,reservation
            if not stock_date:
                break
            # 4字节如20091229
            stock_date = struct.unpack("l", stock_date)
            # 开盘价*100
            stock_open = struct.unpack("l", stock_open)
            # 最高价*100
            stock_high = struct.unpack("l", stock_high)
            # 最低价*100
            stock_low = struct.unpack("l", stock_low)
            # 收盘价*100
            stock_close = struct.unpack("l", stock_close)
            # 成交额
            stock_amount = struct.unpack("f", stock_amount)
            # 成交量
            stock_vol = struct.unpack("l", stock_vol)
            # 保留值
            stock_reservation = struct.unpack("l", stock_reservation)
            # 格式化日期
            date_format = datetime.datetime.strptime(str(stock_date[0]), '%Y%M%d')
            list = date_format.strftime('%Y-%M-%d') + "," + str(stock_open[0] / 100) + "," + str(
                stock_high[0] / 100.0) + "," + str(stock_low[0] / 100.0) + "," + str(
                stock_close[0] / 100.0) + "," + str(stock_vol[0]) + "\r\n"

            file_object.writelines(list)
        file_object.close()


if __name__ == '__main__':
    market = 'shm.tnf'
    market = 'szm.tnf'
    infos = basic_info('C:/new_tdx/T0002/hq_cache/' + market)  # szm.tnf
    for t in infos:
        if '300502' in t[0]:
            print(t)
    print(infos)

    path = 'C:/new_tdx/vipdoc/sh/lday/'
    file_list = os.listdir('C:/new_tdx/vipdoc/sh/lday/')
    for i in file_list:
        if i == 'sh600839.day':
            stock_csv(path+i, i[:-4])
            break
