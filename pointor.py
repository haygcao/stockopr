
import time
import datetime
from config import config as cfg
from acquisition import quote_www as price
# from pointor import rediscli

from config.config import start_time_am
from config.config import start_time_pm

def price_to_percent(price, base):
    return round(100 * (float(price) - float(base)) / float(base), 2)

def init_stock_info(stockInfo):
    code = stockInfo['code']
    stock_info = {'code': code,
                  'high': 0,
                  'low': 0,
                  'last_min': 0,
                  'price': 99,
                  'last': 0,
                  'cur_stage': '',
                  'time_last_record': 0,
                  'time_last_alert': 0,
                  'name': stockInfo['name'],
                  'realtime_up_percent': [],
                  'bought': 0,
                  'trade': {
                      'high': 4,
                      'low': -4,
                      'count': 0,
                      'account': None,
                  }
                  }

    data_db = rediscli.load_data_from_db(stock_info)
    F = True
    if not data_db:
        F = False
    else:
        t = int(data_db['time_last_record'])
        day1 = str(datetime.datetime.fromtimestamp(t)).split()[0]
        day2 = str(datetime.datetime.now()).split()[0]
        print(day1, day2)
        if day1 != day2:
            F = False

    #if not os.path.exists('si_{0}_{1}'.format(code, util.get_today())):
    if not F:
        stock_info['high'] = stockInfo["high"]
        stock_info['low'] = stockInfo["low"]
        stock_info['last_min'] = stockInfo["open"]
        stock_info['last'] = stock_info['price']
        stock_info['price'] = stockInfo['price']
    else:
        #data_db = rediscli.load_data_from_db(code)
        #if not data_db:
        #    stock_info['last_min'] = stockInfo["open"]
        #else:
        #    stock_info['last_min'] = data_db['last_min']
        #    stock_info['cur_stage'] = data_db['cur_stage']
        stock_info['last_min'] = data_db['last_min']
        stock_info['cur_stage'] = data_db['cur_stage']
        stock_info['high'] = stockInfo["high"]
        stock_info['low'] = stockInfo["low"]
        stock_info['last'] = stock_info['price']
        stock_info['price'] = stockInfo['price']

    stock_info['name'] = stockInfo["name"]

    return stock_info

# real time, 分时行情
def monitor_rt(code):
    import pointor.trend_recognition as tr
    import acquisition.quote_db as quote_db
    # quote = quote_db.get_price_info_df_db(code, 250)
    quote = None

    trendr = tr.TrendRecognizer(code, quote)

    stock_info = {}

    curUpPercent = 0

    global start_time_am
    global start_time_pm

    tm_today = time.localtime()
    start_time_am = time.mktime((tm_today.tm_year, tm_today.tm_mon, tm_today.tm_mday, 9, 30, 0, 0, 0, 0))
    end_time_am = time.mktime((tm_today.tm_year, tm_today.tm_mon, tm_today.tm_mday, 11, 30, 0, 0, 0, 0))
    start_time_pm = time.mktime((tm_today.tm_year, tm_today.tm_mon, tm_today.tm_mday, 13, 0, 0, 0, 0, 0))
    end_time_pm = time.mktime((tm_today.tm_year, tm_today.tm_mon, tm_today.tm_mday, 15, 0, 0, 0, 0, 0))

    # for testing
    start_time_am = start_time_pm = time.time()
    end_time_am = end_time_pm = start_time_am + 3600

    # rediscli.set_day(tm_today.tm_yday)
    if cfg.emulate:
        time_begin = int(time.time())
        start_time_am = time_begin
        # rediscli.del_all_stages()

    to_trade = False
    to_open_graph = False
    to_save_db = False

    while(True):
        if not cfg.monitoring:
            time.sleep(1)
            continue

        now = int(time.time())

        if not cfg.emulate:
            if now > end_time_pm:
                break
            if now < start_time_am:
                time.sleep(cfg.wait_time_m)
                continue
            elif now > end_time_am and now < start_time_pm:
                time.sleep(cfg.wait_time_m)
                continue

        if now % 2 == 0:
            stockInfo = price.getChinaStockIndividualPriceInfo(code)
            if stockInfo == None:
                continue

            key_str = ["name", "code", "yestclose", "open", "price", "high", "low", "updown", "percent"]
            for key in key_str:
                if key == "open" or key ==  "price" or key == "high" or key == "low":
                    stockInfo[key] = price_to_percent(stockInfo[key], stockInfo['yestclose'])

            #统计, 转向, 突破
            curUpPercent = stockInfo["price"]

            #模拟行情
            if cfg.emulate:
                global emu_input, idx_emu_input
                if idx_emu_input == len(emu_input):
                    idx_emu_input = 0
                    #exit(0)
                curUpPercent = emu_input[idx_emu_input]
                print('debug: curUpPercent:', curUpPercent)
                idx_emu_input += 1

                time.sleep(3)

            if curUpPercent > 10 or curUpPercent < -10:
                #print('not start', code, stockInfo["名称"], curUpPercent)
                continue

            #初始化
            if not stock_info:
                stock_info = init_stock_info(stockInfo)
                if curUpPercent > 0:
                    stock_info['cur_stage'] = '3'
                else:
                    stock_info['cur_stage'] = '4'

                #保存到数据库
                stock_info['time_last_record'] = now
                # 不能等到最后才保存
                # rediscli.save_cur_stage(stock_info)
                # rediscli.save_stage_info(stock_info, stock_info['cur_stage'], (curUpPercent, curUpPercent))

            #首先记录数据
            if now - stock_info['time_last_record'] >= 60:
                stock_info['last_min'] = curUpPercent
                stock_info['time_last_record'] = now

                #保存到数据库
                to_save_db = True


            #自动止盈止损
            if cfg.emulate or now > start_time_am and now < end_time_pm:
                if curUpPercent >= stock_info['trade']['high']:
                    to_trade = True
                    bs = 1
                elif curUpPercent <= stock_info['trade']['low']:
                    to_trade = True
                    bs = 3

                if cfg.emulate:
                    to_trade = True
                    bs = 3

            #新高新低
            flag_up_down = 1 #1上升, 2下降, 3破新高, 4破新低
            if curUpPercent > stock_info['high']:
                stock_info['high'] = curUpPercent
                to_open_graph = True
                flag_up_down = 3

                #保存到数据库
                to_save_db = True

            if curUpPercent < stock_info['low']:
                stock_info['low'] = curUpPercent
                to_open_graph = True
                flag_up_down = 4

                #保存到数据库
                to_save_db = True

            #异动
            if (curUpPercent - stock_info['last']) >= cfg.indicator['yd_up']:
                #打开异动个股
                to_open_graph = True
                flag_up_down = 1

            if curUpPercent - stock_info['last'] <= cfg.indicator['yd_down']:
                #打开异动个股
                to_open_graph = True
                flag_up_down = 2

            stock_info['last'] = stock_info['price']
            stock_info['price'] = curUpPercent

            if to_trade and now - stock_info['time_last_alert'] > cfg.alert_interval_time:
                stock_info['time_last_alert'] = now
                # trade_signal_lm(stock_info, bs)
            if to_open_graph and (cfg.emulate or (cfg.emulate or now - start_time_am > cfg.alert_startup_time) and now - stock_info['time_last_alert'] > cfg.alert_interval_time):
                stock_info['time_last_alert'] = now
                # alert(stock_info, flag_up_down)

            # if to_save_db:
            #     rediscli.save_to_db(stock_info)

            #draw_simplified_realtime_graph(stock_info)
            #input('')
            trendr.trend_recognition(now, stock_info['price'])

            #print_stock_info(code)
            time.sleep(cfg.wait_time_s)


if __name__ == '__main__':
    code = '600839'
    monitor_rt(code)
