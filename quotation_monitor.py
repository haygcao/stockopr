# -*- coding: utf-8 -*-
import atexit
import datetime
import multiprocessing
import random
import time
from dataclasses import dataclass

import numpy
import pandas

from chart import open_graph
from config import config
from config.config import period_map, signal_deviation, Policy, signal_enter_deviation, signal_exit_deviation
from data_structure import trade_data
from pointor import signal_dynamical_system, signal_market_deviation, signal
from pointor import signal_channel

from acquisition import tx, quote_db
from trade_manager import trade_manager
from util.log import logger


@dataclass
class TradeSignal:
    code: str
    price: float
    date: datetime.datetime = datetime.datetime.now()
    command: str = ''
    policy: Policy = Policy.DEFAULT
    period: str = ''
    last: bool = False

    def __init__(self, code: str, price: float, date: datetime.datetime, command: str, category: Policy, period: str, last: bool):
        self.code = code
        self.price = price
        self.date = date
        self.command = command
        self.policy = category
        self.period = period
        self.last = last


class TradeSignalManager:
    # {
    #     'code': [TradeSignal, ]
    # }
    signal_map = {}
    # {
    #     'code': data_structure.trade_data.TradeOrder
    # }
    trade_order_map: dict[str, trade_data.TradeOrder]

    @classmethod
    def reload_trade_order(cls):
        cls.trade_order_map = quote_db.query_trade_order_map()
        for code in cls.trade_order_map.keys():
            if code in cls.signal_map:
                continue
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

    @classmethod
    def get_stop_loss(cls, code):
        if code in cls.trade_order_map:
            return cls.trade_order_map[code].stop_loss
        return -1


@atexit.register
def goodbye():
    logger.info("monitor stopped")


def get_min_data(code, m='m5', count=250):
    try:
        data = tx.get_kline_data(code, m, count)
        return data
    except Exception as e:
        logger.info('get data error:', e)


def get_day_data(code, period='day', count=250):
    data = tx.get_kline_data(code, period, count)
    return data


def write_supplemental_signal(supplemental_signal_path, trade_signal: TradeSignal):
    import csv
    with open(supplemental_signal_path, 'a', newline='') as csvfile:
        fieldnames = ['code', 'name', 'date', 'command', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # writer.writeheader()
        writer.writerow({'code': trade_signal.code,
                         'date': trade_signal.date.strftime('%Y-%m-%d %H:%M'),
                         'command': trade_signal.command,
                         'price': trade_signal.price
                         })


def update_status_old(code, data, period):
    data_index_ = data.index[-1]
    price = data['close'][-1]

    # if period_status:
    #     if period.startswith('m') and (data_index_ - period_status[-1].date).seconds < int(period[1:])*60:
    #         logger.info('no new data')
    #         return False

    # deviation signal
    data = signal_market_deviation.signal_enter(data, period, back_days=0)
    data = signal_market_deviation.signal_exit(data, period, back_days=0)
    for column_name in ['macd_bull_market_deviation',
                        'macd_bear_market_deviation',
                        'force_index_bull_market_deviation',
                        'force_index_bear_market_deviation']:
        n = 1 if period == 'm5' else 1
        data_sub = data[column_name][-n:]
        command = 'B' if 'bull' in column_name else 'S'
        if data_sub.any(skipna=True):
            data_index_ = data_sub[data_sub.notnull()].index[0]
            return TradeSignal(code, price, data_index_, command, Policy.DEVIATION, period, True)

    data = signal_channel.signal_enter(data, period=period)
    data = signal_channel.signal_exit(data, period=period)

    if not numpy.isnan(data['channel_signal_enter'][-1]):
        return TradeSignal(code, price, data_index_, 'B', Policy.CHANNEL, period, True)

    if not numpy.isnan(data['channel_signal_exit'][-1]):
        return TradeSignal(code, price, data_index_, 'S', Policy.CHANNEL, period, True)

    # long period do not check dynamical system signal
    if period in ['m30']:
        return

    # dynamical system signal
    data = signal_dynamical_system.signal_enter(data, period=period)
    data = signal_dynamical_system.signal_exit(data, period=period)

    if data['dynamical_system_signal_enter'][-1] > 0:
        return TradeSignal(code, price, data_index_, 'B', Policy.DYNAMICAL_SYSTEM, period, True)

    if not numpy.isnan(data['dynamical_system_signal_exit'][-1]):
        return TradeSignal(code, price, data_index_, 'S', Policy.DYNAMICAL_SYSTEM, period, True)
    # if not status_map[code][str(m)] or data['dlxt'][-1] != status_map[code][str(m)][-1]:
    #     status_map[code][str(m)].append((datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), data['dlxt'][-1]))
    #     return True

    return


def check_trade_order_stop_loss(code, data):
    # stop_loss = TradeSignalManager.get_stop_loss(code)
    # return data['close'].iloc[-1] <= stop_loss
    return False


def update_status(code, data, period):
    data_index_: datetime.datetime = data.index[-1]
    price = data['close'][-1]

    if check_trade_order_stop_loss(code, data):
        return TradeSignal(code, price, data_index_, 'S', Policy.STOP_LOSS, period, True)

    data = signal.compute_signal(data, period)

    minute = 0 if period == 'day' else int(period[1:])
    # 周期最 3 分钟
    if period == 'day' or data_index_.minute % minute >= minute - 3:
        if not numpy.isnan(data['stop_loss_signal_exit'][-1]):
            return TradeSignal(code, price, data_index_, 'S', Policy.STOP_LOSS, period, True)

        for deviation in signal_exit_deviation:
            if not numpy.isnan(data[deviation][-2]):
                direct = 'S'
                return TradeSignal(code, price, data_index_, direct, Policy.DEVIATION, period, True)

        for deviation in signal_enter_deviation:
            if not numpy.isnan(data[deviation][-2]):
                direct = 'B'
                return TradeSignal(code, price, data_index_, direct, Policy.DEVIATION, period, True)

    if not numpy.isnan(data['signal_exit'][-1]):
        return TradeSignal(code, price, data_index_, 'S', Policy.DEFAULT, period, True)

    if not numpy.isnan(data['signal_enter'][-1]):
        return TradeSignal(code, price, data_index_, 'B', Policy.DEFAULT, period, True)


def check(code, period):
    data_day = get_min_data(code, 'day')
    if not isinstance(data_day, pandas.DataFrame) or data_day.empty:
        return
    logger.debug('now check {} {} status'.format(code, 'day'))
    trade_signal = update_status(code, data_day, 'day')
    if trade_signal:
        return trade_signal

    long_period = period_map[period]['kline_long_period']
    data30 = get_min_data(code, long_period)
    if not isinstance(data30, pandas.DataFrame) or data30.empty:
        return
    logger.debug('now check {} {} status'.format(code, long_period))
    trade_signal = update_status(code, data30, long_period)
    if trade_signal:
        return trade_signal

    data5 = get_min_data(code, period)
    if not isinstance(data5, pandas.DataFrame) or data5.empty:
        return
    logger.debug('now check {} {} status'.format(code, period))
    trade_signal = update_status(code, data5, period)
    if trade_signal:
        return trade_signal


def order(trade_singal: TradeSignal):
    logger.info('{} {}'.format(trade_singal.command, trade_singal.code))
    if trade_singal.command == 'B':
        trade_manager.buy(trade_singal.code, close=trade_singal.price, policy=trade_singal.policy)
    else:
        trade_manager.sell(trade_singal.code, close=trade_singal.price)


def notify(trade_singal: TradeSignal):

    # log
    command = '买入' if trade_singal.command == 'B' else '卖出'
    # tts
    from toolkit import tts
    txt = '注意, {1}信号, {2}, {0}'.format(' '.join(trade_singal.code), command, trade_singal.policy.value)
    logger.info(txt)
    tts.say(txt)


def query_trade_order_code_list():
    r = quote_db.query_trade_order_map()
    return [code for code, name in r.items()]


def monitor_today():
    period = 'm5'

    logger.info(TradeSignalManager.signal_map)
    while True:
        TradeSignalManager.reload_trade_order()

        now = datetime.datetime.now()
        if now.hour == 15:
            return
        if now.hour == 12 or (now.hour == 11 and now.minute > 30):
            time.sleep(60)
            continue

        if now.second > 50:
            logger.info('quotation monitor is running')

        for code in TradeSignalManager.trade_order_map.keys():
            time.sleep(random.randint(3, 10))
            trade_signal = check(code, period)
            if not trade_signal:
                continue

            if not TradeSignalManager.need_signal(trade_signal):
                continue

            # write to log
            # supplemental_signal: [(code, date, 'B/S', price), (code, date, 'B/S', price), ...]

            supplemental_signal_path = config.supplemental_signal_path
            write_supplemental_signal(supplemental_signal_path, trade_signal)

            logger.info(TradeSignalManager.signal_map)
            p = multiprocessing.Process(target=open_graph, args=(code, trade_signal.period,))
            p.start()

            order(trade_signal)
            notify(trade_signal)

            p.join(timeout=1)


if __name__ == '__main__':
    monitor_today()
