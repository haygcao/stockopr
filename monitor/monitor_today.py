# -*- coding: utf-8 -*-
import atexit
import datetime
import multiprocessing
import time

import sys

import numpy

from chart.kline import open_graph
from config.config import period_map
from pointor import signal_triple_screen, signal_market_deviation
from pointor import signal_channel

from acquisition import tx
from toolkit import tradeapi

status_map = {}


@atexit.register
def goodbye():
    print("monitor stopped")


def get_min_data(code, m='m5', count=250):
    try:
        return tx.get_kline_data(code, m, count)
    except Exception as e:
        print('get data error:', e)


def get_day_data(code, period='day', count=250):
    data = tx.get_kline_data(code, period, count)
    return data


def update_status(code, data, period):
    data_index_ = data.index[-1]
    period_status = status_map[code][str(period)]
    if period_status:
        if period.startswith('m') and (data_index_ - period_status[-1]['date']).seconds < int(period[1:])*60:
            print('{} - no new data'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return False

    # deviation signal
    data = signal_market_deviation.signal(data, period, back_days=0)
    for column_name in ['macd_bull_market_deviation', 'macd_bear_market_deviation', 'force_index_bull_market_deviation', 'force_index_bear_market_deviation']:
        n = 1 if period == 'm5' else 1
        data_sub = data[column_name][-n:]
        command = 'B' if 'bull' in column_name else 'S'
        deviation = 'bull deviation' if command == 'B' else 'bear deviation'
        if data_sub.any(skipna=True):
            data_index_ = data_sub[data_sub.notnull()].index[0]
            if not period_status or (data_index_ != period_status[-1]['date'] or period_status[-1]['type'] != deviation):
                period_status.append({'date': data_index_, 'command': command, 'type': deviation, 'last': True})
                return True

    # data_sub = data['macd_bear_market_deviation'][-5:]
    # if data_sub.any(skipna=True):
    #     data_index_ = data_sub[data_sub.notnull()].index[0]
    #     if data_index_ != period_status[-1]['date'] or period_status[-1]['type'] != 'bear deviation':
    #         period_status.append({'date': data_index_, 'command': 'B', 'type': 'bear deviation', 'last': True})
    #         return True

    # triple_screen signal
    data = signal_triple_screen.signal_enter(data, period=period)
    data = signal_triple_screen.signal_exit(data, period=period)

    # if not numpy.isnan(data['triple_screen_signal_enter'][-1]):
    if data['triple_screen_signal_enter'][-1] > 0:
        period_status.append({'date': data_index_, 'command': 'B', 'type': 'triple screen', 'last': True})
        return True

    if not numpy.isnan(data['triple_screen_signal_exit'][-1]):
        period_status.append({'date': data_index_, 'command': 'S', 'type': 'triple screen', 'last': True})
        return True

    data = signal_channel.signal_enter(data, period=period)
    data = signal_channel.signal_exit(data, period=period)

    if not numpy.isnan(data['channel_signal_enter'][-1]):
        period_status.append({'date': data_index_, 'command': 'B', 'type': 'channel', 'last': True})
        return True

    if not numpy.isnan(data['channel_signal_exit'][-1]):
        period_status.append({'date': data_index_, 'command': 'S', 'type': 'channel', 'last': True})
        return True

    # if not status_map[code][str(m)] or data['dlxt'][-1] != status_map[code][str(m)][-1]:
    #     status_map[code][str(m)].append((datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), data['dlxt'][-1]))
    #     return True

    if period_status:
        period_status[-1]['last'] = False

    return False


def check(code, period):
    long_period = period_map[period]['kline_long_period']
    data30 = get_min_data(code, long_period)
    print('{} - now check {} status'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), long_period))
    if update_status(code, data30, long_period):
        return long_period

    data5 = get_min_data(code, period)
    print('{} - now check {} status'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), period))
    if update_status(code, data5, period):
        return period


def order(code, direct, type):
    count = 1500
    print('{} {} {}'.format(direct, code, count))
    try:
        tradeapi.order(direct, code, count, auto=False)
    except Exception as e:
        print('call tradeapi error:', e)
        # import traceback
        # print(traceback.print_exc())


def notify(code, direct, type):

    # log
    command = '买入' if direct == 'B' else '卖出'
    # tts
    from toolkit import tts
    txt = '注意, {1}信号, {2}, {0}'.format(' '.join(code), command, type)
    print('{} - {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), txt))
    tts.say(txt)


def monitor(codes, period):
    while True:
        now = datetime.datetime.now()
        if now.hour == 15:
            return
        if now.hour == 12 or (now.hour == 11 and now.minute > 30):
            time.sleep(60)
            continue

        for code in codes:
            period_signal = check(code, period)
            if period_signal:
                print('{} - {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status_map))
                p = multiprocessing.Process(target=open_graph, args=(code, period_signal,))
                p.start()

                singal_info = status_map[code][period_signal][-1]
                order(code, singal_info['command'], singal_info['type'])
                notify(code, singal_info['command'], singal_info['type'])

                p.join(timeout=1)
        time.sleep(60)


def monitor_today():
    period = 'm1'
    code = '300502'
    codes = [code]
    for code in codes:
        status_map[code] = {}
        status_map[code]['m1'] = []
        status_map[code]['m5'] = []
        status_map[code]['m30'] = []

    print('{} - {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status_map))
    monitor(codes, period)


if __name__ == '__main__':
    monitor_today()
