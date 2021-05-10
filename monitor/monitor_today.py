# -*- coding: utf-8 -*-
import datetime
import time

import sys

from chart.kline import open_graph
from config.config import period_map
from pointor import signal_triple_screen

from selector.plugin import dynamical_system, force_index
from acquisition import tx


status_map = {}


def get_min_data(code, m='m5', count=250):
    data = tx.get_kline_data(code, m, count)
    return data


def get_day_data(code, period='day', count=250):
    data = tx.get_kline_data(code, period, count)
    return data


def update_status(code, data, period):
    # triple_screen signal
    data = signal_triple_screen.signal_enter(data, period=period)
    data = signal_triple_screen.signal_exit(data, period=period)

    if not data['triple_screen_signal_enter'][-1]:
        status_map[code][str(period)].append((data.index[-1], 1))
        return True

    if not data['triple_screen_signal_exit'][-1]:
        status_map[code][str(period)].append((data.index[-1], -1))
        return True

    # if not status_map[code][str(m)] or data['dlxt'][-1] != status_map[code][str(m)][-1]:
    #     status_map[code][str(m)].append((datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), data['dlxt'][-1]))
    #     return True

    return False


def check(code, period):
    long_period = period_map[period]['kline_long_period']
    data30 = get_min_data(code, long_period)
    print('now check {} status'.format(long_period))
    update_status(code, data30, long_period)

    data5 = get_min_data(code, period)
    print('now check {} status'.format(period))
    if not update_status(code, data5, period):
        return False
    return True


def notify():
    # log

    # tts
    from toolkit import tts
    tts.say('注意交易信号')


def monitor(codes, period):
    while True:
        for code in codes:
            if check(code, period):
                notify()
                open_graph(code, period)
            print(status_map)
        time.sleep(60)


if __name__ == '__main__':
    period = 'm5'
    code = '300502'
    codes = [code]
    for code in codes:
        status_map[code] = {}
        status_map[code]['1'] = []
        status_map[code]['5'] = []
        status_map[code]['30'] = []

    print(status_map)
    monitor(codes, period)
