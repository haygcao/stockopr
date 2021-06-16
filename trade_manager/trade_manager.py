# -*- coding: utf-8 -*-
import datetime
import multiprocessing
import threading
import time

from PyQt5.QtWidgets import QMessageBox, QApplication

from acquisition import tx, quote_db
from config import config
from config.config import Policy
from data_structure import trade_data
from indicator import atr, ema, dynamical_system
from pointor import signal
from trade_manager import tradeapi, db_handler
from util import mysqlcli, dt
from util.dt import istradeday

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


def query_withdraw_order():
    order_list = tradeapi.query_withdraw_order()
    return order_list


def query_position(code):
    """
    可以卖的股数
    还可以买的股数
    """
    position = db_handler.query_position(code)
    sold_position_in_operation_detail = query_sold_position_in_operation_detail(code)
    position.avail_position -= sold_position_in_operation_detail

    return position


def query_current_position():
    """
    可以卖的股数
    还可以买的股数
    """
    position_list = db_handler.query_current_position()
    for position in position_list:
        sold_position_in_operation_detail = query_sold_position_in_operation_detail(position.code)
        position.avail_position -= sold_position_in_operation_detail

    return position_list


def query_money():
    money = db_handler.query_money()
    money_in_operation_detail = query_money_in_operation_detail()
    money.avail_money -= money_in_operation_detail

    return money


def query_operation_detail(code=None):
    """
    可以卖的股数
    还可以买的股数
    """
    detail_list = db_handler.query_operation_details(code)

    return detail_list


def query_money_in_operation_detail(code=None, trade_date=None):
    if not trade_date:
        trade_date = datetime.date.today()
    detail_list = db_handler.query_operation_details(trade_date)

    money = 0
    for detail in detail_list:
        money += detail.price_trade * detail.count

    return money


def query_sold_position_in_operation_detail(code=None, trade_date=None):
    if not trade_date:
        trade_date = datetime.date.today()
    detail_list = db_handler.query_operation_details(code, trade_date)

    position = 0
    for detail in detail_list:
        if detail.count < 0:
            position += abs(detail.count)

    return position


def sync():
    """
    sync previous trade date's data
    run at 9:00 on trade day
    """
    now = datetime.datetime.now()
    if now.hour > 9 or (now.hour == 9 and now.minute > 14):
        return

    # money
    money = tradeapi.get_asset()
    db_handler.save_money(money)
    logger.info('sync money')

    # position
    position_list = tradeapi.query_position()
    db_handler.save_positions(position_list)
    logger.info('sync position')

    # operation detail
    operation_detail = tradeapi.query_operation_detail()
    yesterday = dt.get_pre_trade_date()
    operation_detail = [detail for detail in operation_detail if detail.trade_time.date() == yesterday]
    db_handler.save_operation_details(operation_detail)
    logger.info('sync operation detail')


def check_quota(code, direction):
    """
    巡检, 周期巡检超出配额的已有仓位
    """
    current_position = query_position(code)
    quota_position = quote_db.query_quota_position()
    if current_position.current_position > quota_position:
        return False
    return True


def update_operation_detail(detail):
    db_handler.save_operation_details([detail])


def buy(code, price_trade=0, price_limited=0, count=0, policy: Policy = None, auto=None):
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
    max_position = money.avail_money / (price_limited if price_limited > 0 else quote['close'].iloc[-1] * 1.01) // 100 * 100

    trade_config = config.get_trade_config(code)
    if not auto:
        auto = trade_config['auto_buy']
    # if count == 0:
    #     count = trade['count']
    # avail_position = min(avail_position, count)

    count = min(max_position, avail_position)
    # operation = TradeManager.get_operation()
    # operation.__buy(code, count, price, auto=auto)
    order('B', code, price_trade=price_trade, price_limited=price_limited, count=count, auto=auto)


def sell(code, price_trade, price_limited=0, count=0, auto=None):
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
    order('S', code, price_trade=price_trade, price_limited=price_limited, count=count, auto=auto)


def order(direct, code, price_trade, price_limited=0, count=0, auto=False):
    try:
        count = count // 100 * 100
        tradeapi.order(direct, code, count, price_limited, auto)
        now = datetime.datetime.now()
        price = 0   # 成交的价格
        count = count * (1 if direct == 'B' else -1)
        detail = trade_data.OperationDetail(now, code, price, price_trade, price_limited, count)

        if auto and price_limited == 0:
            threading.Thread(target=assure_finish, args=(code, count, now)).start()

        update_operation_detail(detail)
    except Exception as e:
        print(e)


def assure_finish(direct, code, count, trade_time):
    for i in range(10):
        time.sleep(5)
        count_to = wait_finish(direct, code, count, trade_time)
        if count_to == 0:
            return
        re_order(direct, code, count)
    logger.warning(direct, code, count, trade_time, 'unfinished')


def wait_finish(direct, code, count, trade_time):
    count_to = 0

    orders: [trade_data.WithdrawOrder] = query_withdraw_order()
    for row in orders:
        if row.direct != direct or row.code != code or row.trade_time < trade_time:
            continue
        count_to += row.count - row.count_ed - row.count_withdraw

    return count_to


def withdraw(direct='last'):
    """
    full: 全撤
    buy: 撤买
    sell: 撤卖
    last: 撤最新
    """
    try:
        tradeapi.withdraw(direct)
    except Exception as e:
        print(e)


def re_order(direct, code, count):
    # details = db_handler.query_operation_details(date=datetime.date.today())
    # details = [detail for detail in details if detail.price_limited == 0 and detail.count > 0]

    # notify()
    withdraw()
    tradeapi.order(direct, code, count=count, auto=True)


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
