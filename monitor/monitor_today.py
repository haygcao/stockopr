# -*- coding: utf-8 -*-
import datetime
import time

import sys
sys.path.append('.')

from selector.plugin import dynamical_system
from acquisition import tx


status_map = {}


def get_min_data(code, m=5, count=250):
    data = tx.get_kline_data(code, 'm{}'.format(m), count)
    return data


def get_day_data(code, period='day', count=250):
    data = tx.get_kline_data(code, period, count)
    return data


def update_status(code, data, m):
    data = dynamical_system.dynamical_system(data)
    if not status_map[code][str(m)] or data['dlxt'][-1] != status_map[code][str(m)][-1]:
        status_map[code][str(m)].append((datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), data['dlxt'][-1]))
        return True
    return False


def check(code):
    data30 = get_min_data(code, 30)
    print('now check 30 min status')
    update_status(code, data30, 30)

    data5 = get_min_data(code, 5)
    print('now check 5 min status')
    if not update_status(code, data5, 5):
        return False
    return True


def notify():
    # log

    # tts
    from toolkit import tts
    tts.say('注意交易信号')


def monitor(codes):
    while True:
        for code in codes:
            if check(code):
                notify()
            print(status_map)
        time.sleep(60)


if __name__ == '__main__':
    notify()
    exit()
    code = '300502'
    code = '600000'

    codes = [code]
    for code in codes:
        status_map[code] = {}
        status_map[code]['1'] = []
        status_map[code]['5'] = []
        status_map[code]['30'] = []

    print(status_map)
    monitor(codes)
