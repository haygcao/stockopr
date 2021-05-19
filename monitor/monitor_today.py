# -*- coding: utf-8 -*-
import atexit
import datetime
import multiprocessing
import time
from dataclasses import dataclass

import numpy

from chart.kline import open_graph
from config.config import period_map
from pointor import signal_dynamical_system, signal_market_deviation
from pointor import signal_channel

from acquisition import tx
from toolkit import tradeapi


@dataclass
class TradeSignal:
    code: str
    date: datetime.datetime = datetime.datetime.now()
    command: str = ''
    category: str = ''
    period: str = ''
    last: bool = False

    def __init__(self, code: str, date: datetime.datetime, command: str, category: str, period: str, last: bool):
        self.code = code
        self.date = date
        self.command = command
        self.category = category
        self.period = period
        self.last = last


class TradeSignalManager:
    # {
    #     'code': [TradeSignal, ]
    # }
    signal_map = {}

    @classmethod
    def init(cls, code_list):
        for code in code_list:
            cls.signal_map[code] = []

    @classmethod
    def get_trade_signal_list(cls, code):
        return cls.signal_map[code]

    @classmethod
    def get_last_trade_signal(cls, code):
        return cls.signal_map[code][-1] if cls.signal_map[code] else None

    @classmethod
    def append_trade_siganl(cls, trade_signal):
        cls.signal_map[trade_signal.code].append(trade_signal)

    @classmethod
    def need_signal(cls, trade_signal: TradeSignal) -> bool:
        last_signal = cls.get_last_trade_signal(trade_signal.code)
        cls.append_trade_siganl(trade_signal)
        if last_signal and last_signal.command == trade_signal.command:
            return False

        return True

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

    # if period_status:
    #     if period.startswith('m') and (data_index_ - period_status[-1].date).seconds < int(period[1:])*60:
    #         print('{} - no new data'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    #         return False

    # deviation signal
    data = signal_market_deviation.signal(data, period, back_days=0)
    for column_name in ['macd_bull_market_deviation', 'macd_bear_market_deviation', 'force_index_bull_market_deviation', 'force_index_bear_market_deviation']:
        n = 1 if period == 'm5' else 1
        data_sub = data[column_name][-n:]
        command = 'B' if 'bull' in column_name else 'S'
        deviation = 'bull deviation' if command == 'B' else 'bear deviation'
        if data_sub.any(skipna=True):
            data_index_ = data_sub[data_sub.notnull()].index[0]
            return TradeSignal(code, data_index_, command, deviation, period, True)

    # data_sub = data['macd_bear_market_deviation'][-5:]
    # if data_sub.any(skipna=True):
    #     data_index_ = data_sub[data_sub.notnull()].index[0]
    #     if data_index_ != period_status[-1]['date'] or period_status[-1]['type'] != 'bear deviation':
    #         period_status.append({'date': data_index_, 'command': 'B', 'type': 'bear deviation', 'last': True})
    #         return True

    # if not numpy.isnan(data['dynamical_system_signal_enter'][-1]):

    data = signal_channel.signal_enter(data, period=period)
    data = signal_channel.signal_exit(data, period=period)

    if not numpy.isnan(data['channel_signal_enter'][-1]):
        return TradeSignal(code, data_index_, 'B', 'channel', period, True)

    if not numpy.isnan(data['channel_signal_exit'][-1]):
        return TradeSignal(code, data_index_, 'S', 'channel', period, True)

    # dynamical system signal
    data = signal_dynamical_system.signal_enter(data, period=period)
    data = signal_dynamical_system.signal_exit(data, period=period)

    if data['dynamical_system_signal_enter'][-1] > 0:
        return TradeSignal(code, data_index_, 'B', 'dynamical system', period, True)

    if not numpy.isnan(data['dynamical_system_signal_exit'][-1]):
        return TradeSignal(code, data_index_, 'S', 'dynamical system', period, True)
    # if not status_map[code][str(m)] or data['dlxt'][-1] != status_map[code][str(m)][-1]:
    #     status_map[code][str(m)].append((datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), data['dlxt'][-1]))
    #     return True

    return


def check(code, period):
    # long_period = period_map[period]['kline_long_period']
    # data30 = get_min_data(code, long_period)
    # print('{} - now check {} status'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), long_period))
    # trade_signal = update_status(code, data30, long_period)
    # if trade_signal:
    #     return trade_signal
    # return

    data5 = get_min_data(code, period)
    print('{} - now check {} status'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), period))
    trade_signal = update_status(code, data5, period)
    if trade_signal:
        return trade_signal


def order(trade_singal: TradeSignal):
    count = 1500
    print('{} {} {}'.format(trade_singal.command, trade_singal.code, count))
    try:
        tradeapi.order(trade_singal.command, trade_singal.code, count, auto=False)
    except Exception as e:
        print('call tradeapi error:', e)
        # import traceback
        # print(traceback.print_exc())


def notify(trade_singal: TradeSignal):

    # log
    command = '买入' if trade_singal.command == 'B' else '卖出'
    # tts
    from toolkit import tts
    txt = '注意, {1}信号, {2}, {0}'.format(' '.join(trade_singal.code), command, trade_singal.category)
    print('{} - {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), txt))
    tts.say(txt)


def monitor_today():
    period = 'm5'
    code = '300502'
    code_list = [code]

    TradeSignalManager.init(code_list)

    print('{} - {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), TradeSignalManager.signal_map))
    while True:
        now = datetime.datetime.now()
        if now.hour == 15:
            return
        if now.hour == 12 or (now.hour == 11 and now.minute > 30):
            time.sleep(60)
            continue

        for code in code_list:
            trade_signal = check(code, period)
            if not trade_signal:
                continue

            if not TradeSignalManager.need_signal(trade_signal):
                continue

            print('{} - {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), TradeSignalManager.signal_map))
            p = multiprocessing.Process(target=open_graph, args=(code, trade_signal.period,))
            p.start()

            order(trade_signal)
            notify(trade_signal)

            p.join(timeout=1)
        time.sleep(60)


if __name__ == '__main__':
    monitor_today()
