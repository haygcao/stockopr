# -*- coding: utf-8 -*-
import datetime
import multiprocessing

from PyQt5.QtWidgets import QMessageBox, QApplication

from acquisition import tx, quote_db
from config import config
from config.config import Policy
from indicator import atr, ema, dynamical_system
from pointor import signal
from trade_manager import tradeapi
from util import mysqlcli

from util.log import logger


class TradeManager:
    # operation: tradeapi.OperationThs = None

    def __init__(self):
        pass

    @classmethod
    def get_operation(cls):
        pass
        # if not cls.operation:
        #     cls.operation = tradeapi.OperationThs()
        # cls.operation.max_window()
        # return cls.operation


def query_position(code):
    """
    可以卖的股数
    还可以买的股数
    """
    position = tradeapi.query_position(code)

    return position


def query_money():
    money = tradeapi.get_asset()
    return money


def query_operation_detail(code):
    """
    可以卖的股数
    还可以买的股数
    """
    detail_list = tradeapi.query_operation_detail(code)

    return detail_list


def check_quota(code, direction):
    """
    巡检, 周期巡检超出配额的已有仓位
    """
    current_position = query_position(code)
    quota_position = quote_db.query_quota_position()
    if current_position.current_position > quota_position:
        return False
    return True


def buy(code, close, count=0, price=0, policy: Policy = None, auto=None):
    """
    单次交易仓位: min(加仓至最大配额, 可用全部资金对应仓位)
    """
    position_quota = quote_db.query_quota_position(code)
    if not position_quota:
        popup_warning_message_box('请先创建交易指令单, 请务必遵守规则!')
        return

    quote = tx.get_kline_data(code)
    if policy != Policy.DEVIATION:
        quote = dynamical_system.dynamical_system_dual_period(quote, period='day')
        if quote['dlxt'].iloc[-1] < 0 or quote['dlxt_long_period'].iloc[-1] < 0:
            popup_warning_message_box('动力系统为红色, 禁止买入, 请务必遵守规则!')
            return

    position = query_position(code)
    current_position = position.current_position if position else 0

    avail_position = position_quota - current_position
    if avail_position < 100:
        popup_warning_message_box('配额已用完, 请务必遵守规则!')
        return

    # quote = tx.get_realtime_data_sina(code)
    money = query_money()
    max_position = money.avail_money / (price if price > 0 else quote['close'].iloc[-1] * 1.01) // 100 * 100

    trade_config = config.get_trade_config(code)
    if not auto:
        auto = trade_config['auto_buy']
    # if count == 0:
    #     count = trade['count']
    # avail_position = min(avail_position, count)

    count = min(max_position, avail_position)
    # operation = TradeManager.get_operation()
    # operation.__buy(code, count, price, auto=auto)
    order('B', code, count, price, auto=auto)


def sell(code, close, count=0, price=0, auto=None):
    """
    单次交易仓位: 可用仓位   # min(总仓位/2, 可用仓位)
    """
    position = query_position(code)
    if not position:
        return
    current_position = position.current_position
    avail_position = position.avail_position

    to_position = ((current_position / 2) // 100) * 100
    to_position = min(avail_position, to_position)

    trade_config = config.get_trade_config(code)
    if not auto:
        auto = trade_config['auto_sell']

    # if count == 0:
    #     count = trade['count']
    # count = min(to_position, count)

    # count = to_position
    if count <= 0:
        count = avail_position
    # operation = TradeManager.get_operation()
    # operation.__sell(code, count, price, auto=auto)
    order('S', code, count, price, auto=auto)


def order(direct, code, count, price=0, auto=False):
    try:
        count = count // 100 * 100
        tradeapi.order(direct, code, count, price, auto)
    except Exception as e:
        print(e)


def compute_stop_profit(quote):
    quote = atr.compute_atr(quote)
    quote = ema.compute_ema(quote)
    series_atr = quote['atr']
    series_ema = quote['ema26']   # wrong
    # series_ema = quote['close'].ewm(span=26, adjust=False).mean()
    # series_ema = macd.ema(quote, 26)['ema']
    index = -2 if datetime.date.today().weekday() < 4 else -1
    last_diff = series_atr[index] - series_atr[index - 1]
    stop_profit = series_ema[index] + (series_atr[index] + last_diff) * 3

    return stop_profit


def create_trade_order(code):
    """
    单个股持仓交易风险率 <= 1%
    总持仓风险率 <= 6%
    """
    quote = tx.get_kline_data(code, 'day')
    quote_week = quote_db.get_price_info_df_db_week(quote, period_type=config.period_map['day']['long_period'])

    quote = signal.compute_signal(quote, 'day')
    price = quote['close'].iloc[-1]
    stop_loss = quote['stop_loss_full'].iloc[-1]

    money = query_money()
    # total money, begin of month
    # total_money = money.total_money
    trade_config = config.get_trade_config(code)
    total_money = trade_config['total_money']
    avail_money = money.avail_money

    loss = total_money * config.one_risk_rate
    total_loss_used = quote_db.query_total_risk_amount()
    total_loss_remain = total_money * config.total_risk_rate - total_loss_used

    loss = min(loss, total_loss_remain)
    loss = min(loss, avail_money)
    position = loss / (price - stop_loss) // 100 * 100
    position = min(position, avail_money / price // 100 * 100)
    if position < 100:
        return

    stop_profit = compute_stop_profit(quote_week)

    profitability_ratios = (stop_profit - price) / (price - stop_loss)
    if profitability_ratios < 2:
        return

    val = [datetime.date.today(), code, position * price, position, price, stop_loss, stop_profit,
           (position * price) / total_money, profitability_ratios, 'ING']

    val = tuple(val)

    keys = ['date', 'code', 'capital_quota', '`position`', 'open_price', 'stop_loss', 'stop_profit', 'risk_rate', 'profitability_ratios', 'status']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)
    sql = "insert into {} ({}) values ({})".format(config.sql_tab_trade_order, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            c.execute(sql, val)
        except Exception as e:
            print(e)


def handle_illegal_position(code):
    logger.warning('{} excess...'.format(code))

    popup_warning_message_box('[{}]违规仓位, 请务必遵守规则, '.format(code))


def _popup_warning_message_box(msg):
    app = QApplication([])
    msg_box = QMessageBox(QMessageBox.Warning, '警告', msg)
    msg_box.exec_()


def popup_warning_message_box(msg):
    multiprocessing.Process(target=_popup_warning_message_box, args=(msg,)).start()


def patrol():
    position_list = tradeapi.get_position()
    for position in position_list:
        quota = quote_db.query_quota_position(position.code)
        if not quota:
            handle_illegal_position(position.code)
            continue
        if position.current_position > quota:
            handle_illegal_position(position.code)
            continue


if __name__ == '__main__':
    # patrol()
    handle_illegal_position('300502')
