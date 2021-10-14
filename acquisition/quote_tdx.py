import os
import struct
import datetime
import subprocess
import time

import pandas

from util import pylinuxauto, util
from util.log import logger


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


def parse_quote(filepath, start_date=None, end_date=None):
    code = os.path.basename(filepath)[2:-4]
    quote = []
    with open(filepath, 'rb') as f:
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

            if start_date and date_format.date() < start_date:
                continue
            if end_date and date_format.date() >= end_date:
                continue

            row = (code, date_format.strftime('%Y-%M-%d'), str(stock_open[0] / 100), str(
                stock_high[0] / 100.0), str(stock_low[0] / 100.0),  str(
                stock_close[0] / 100.0), str(stock_amount[0]), str(stock_vol[0]))
            quote.append(row)

        df = pandas.DataFrame(quote, columns=['code', 'trade_date', 'open', 'high', 'low', 'close', 'amount', 'volume'])
        return df


def download_quote():
    # now = datetime.datetime.now()
    # if now.hour < 15:
    #     return

    if util.get_pid_by_exec('tdxw.exe') < 0:
        logger.info('tdx is stopped, start...')
        subprocess.Popen(['playonlinux', '--run', 'tdxw'])

    tdx_window_name = '通达信金融终端V7.56'
    tdx_version = 'V7.56'
    handle = pylinuxauto.search_window_handle(tdx_window_name)
    if not handle:
        while not handle:
            time.sleep(1)
            handle = pylinuxauto.search_window_handle(tdx_window_name)
        time.sleep(10)
    logger.info('tdx is running')

    name = pylinuxauto.get_window_name(handle)
    if name[-5:] == tdx_version:
        # 登录
        logger.info('tdx login...')
        pylinuxauto.send_key('Return')
        while name[-5:] == tdx_version:
            handle = pylinuxauto.search_window_handle(tdx_window_name)
            name = pylinuxauto.get_window_name(handle)
            time.sleep(1)
        time.sleep(10)
        logger.info('tdx login succeed')

    pylinuxauto.active_window_by_name(tdx_window_name)

    # 方案一
    pylinuxauto.send_key('alt+F4')
    time.sleep(1)
    pylinuxauto.send_key('Return')
    time.sleep(1)
    pylinuxauto.send_key('Return')

    while util.get_pid_by_exec('tdxw.exe') > 0:
        time.sleep(5)

    logger.info('tdx quote is downloaded')

    return

    # 方案二
    # if pylinuxauto.has_popup('tdx'):
    #     pylinuxauto.close_popup()
    #
    # pos_option = ('1562', '19')
    # pos_download = ('1625', '240')
    # pylinuxauto.mouse_move(pos_option)
    # time.sleep(0.3)
    # pylinuxauto.click_left()
    # time.sleep(0.3)
    # pylinuxauto.mouse_move(pos_download)
    # pylinuxauto.click_left()
    # time.sleep(0.3)
    # pylinuxauto.send_key('space')
    # time.sleep(0.3)
    # pylinuxauto.send_key('Return')
    #
    # while pylinuxauto.has_popup('tdx'):
    #     time.sleep(5)
