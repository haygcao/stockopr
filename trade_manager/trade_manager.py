# -*- coding: utf-8 -*-
import datetime
import threading
import time

import trade_manager.db_handler
from acquisition import tx, quote_db
from config import config
from config.config import Policy, ERROR
from data_structure import trade_data
from indicator import atr, ema, dynamical_system, relative_price_strength, ad
from pointor import signal
from trade_manager import tradeapi, db_handler
from util import mysqlcli, dt

from util.log import logger
from util.qt_util import popup_warning_message_box_mp


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


def compute_unsync(position: trade_data.Position):
    sold_position_in_operation_detail = query_position_in_operation_detail(position.code)
    position.avail_position -= sold_position_in_operation_detail
    position.current_position -= sold_position_in_operation_detail

    sold_position_in_operation_detail = query_position_in_operation_detail(position.code, direct='B')
    position.current_position += sold_position_in_operation_detail


def query_position(code):
    """
    可以卖的股数
    还可以买的股数
    """
    position = db_handler.query_position(code)
    compute_unsync(position)

    return position


def query_current_position():
    """
    可以卖的股数
    还可以买的股数
    """
    position_list = db_handler.query_current_position()
    for position in position_list:
        compute_unsync(position)

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


def query_position_in_operation_detail(code=None, trade_date=None, direct='S'):
    if not trade_date:
        trade_date = datetime.date.today()
    detail_list = db_handler.query_operation_details(code, trade_date)

    position = 0
    for detail in detail_list:
        if direct == 'S':
            if detail.count > 0:
                continue
            position += abs(detail.count)
        else:
            if detail.count < 0:
                continue
            position += abs(detail.count)

    return position


def sync():
    """
    sync previous trade date's data
    run at 9:00 on trade day
    """
    now = datetime.datetime.now()
    # if now.hour > 9 or (now.hour == 9 and now.minute > 14):
    #     return

    # money
    money = tradeapi.get_asset()
    db_handler.save_money(money, sync=True)
    logger.info('sync money')

    # position
    position_list = tradeapi.query_position()
    db_handler.save_positions(position_list, sync=True)
    logger.info('sync position')

    order_map = trade_manager.db_handler.query_trade_order_map(status='ING')
    for code, trade_order in order_map.items():
        if code not in [position.code for position in position_list]:
            db_handler.update_trade_order_status(trade_order.date, code, 'ED')
    logger.info('update trade order')

    # operation detail
    operation_detail = tradeapi.query_operation_detail()
    trade_date = dt.get_trade_date()
    # trade_date = datetime.date(2021, 7, 1)
    operation_detail = [detail for detail in operation_detail if detail.trade_time.date() == trade_date]
    db_handler.save_operation_details(operation_detail, trade_date, sync=True)
    logger.info('sync operation detail')


def check_quota(code, direction):
    """
    巡检, 周期巡检超出配额的已有仓位
    """
    current_position = query_position(code)
    quota_position = trade_manager.db_handler.query_quota_position()
    if current_position.current_position > quota_position:
        return False
    return True


def update_operation_detail(detail):
    db_handler.save_operation_details([detail])


def check_list(quote):
    quote = dynamical_system.dynamical_system_dual_period(quote, period='day')
    if quote['dlxt'].iloc[-1] < 0 or quote['dlxt_long_period'].iloc[-1] < 0:
        return ERROR.E_DYNAMICAL_SYSTEM
    # 长周期 ema26 向上, 且 close > 长周期 ema26
    n = 120
    ema_slow = quote.close.ewm(span=n).mean()
    ema_slow_shift = ema_slow.shift(periods=1)
    if ema_slow[-1] <= ema_slow_shift[-1]:
        return ERROR.E_LONG_PERIOD_EMA_INC

    if quote.close[-1] <= ema_slow[-1]:
        return ERROR.E_CLOSE_OVER_LONG_PERIOD_EMA

    ema_fast = quote.close.ewm(span=int(n / 2)).mean()
    macd_line = ema_fast - ema_slow
    macd_line_shift = macd_line.shift(periods=1)
    if macd_line[-1] <= macd_line_shift[-1]:
        return ERROR.E_MACD_LINE_INC

    quote = relative_price_strength.relative_price_strength(quote, period='day')
    if quote['rps'][-1] < quote['erps'][-1]:
        return ERROR.E_WEAKER_THAN_MARKET

    quote = ad.compute_ad(quote)
    if quote['ad'] < quote['ad_ema']:
        return ERROR.E_AD_INC

    return ERROR.OK


def buy(code, price_trade=0, price_limited=0, count=0, period='day', policy: Policy = None, auto=None):
    """
    单次交易仓位: min(加仓至最大配额, 可用全部资金对应仓位)
    """
    position_quota = trade_manager.db_handler.query_quota_position(code)
    if not position_quota:
        popup_warning_message_box_mp('请先创建交易指令单, 请务必遵守规则!')
        return

    quote = tx.get_kline_data(code)
    if period == 'day' and policy != Policy.DEVIATION:
        error = check_list(quote)
        if error != ERROR.OK:
            popup_warning_message_box_mp(error.value)
            return

    position = query_position(code)
    current_position = position.current_position if position else 0

    avail_position = position_quota - current_position
    if avail_position < 100:
        popup_warning_message_box_mp('配额已用完, 请务必遵守规则!')
        return

    # quote = tx.get_realtime_data_sina(code)
    money = query_money()
    max_position = money.avail_money / (price_limited if price_limited > 0 else price_trade * 1.01) // 100 * 100

    trade_config = config.get_trade_config(code)
    position_unit = trade_config['position_unit']
    max_position = min(max_position, (position_unit / price_trade) // 100 * 100)
    if not auto:
        auto = trade_config['auto_buy']

    if count == 0:
        count = trade_config['count']
    # avail_position = min(avail_position, count)

    if count <= 0:
        count = min(max_position, avail_position)

    order('B', code, price_trade=price_trade, price_limited=price_limited, count=count, auto=auto)

    position = position if position else trade_data.Position(code, count, 0)
    db_handler.save_positions([position])


def sell(code, price_trade, price_limited=0, count=0, period='day', policy: Policy = None, auto=None):
    """
    单次交易仓位: 可用仓位   # min(总仓位/2, 可用仓位)
    """
    position = query_position(code)
    if not position:
        return
    quote = tx.get_kline_data(code)
    if period == 'day' and (not policy or (policy != Policy.DEVIATION and policy != Policy.CHANNEL)):
        quote = dynamical_system.dynamical_system_dual_period(quote, period='day')
        if quote['dlxt'].iloc[-1] >= 0 and quote['dlxt_long_period'].iloc[-1] >= 0:
            popup_warning_message_box_mp('动力系统不为红色, 禁止清仓, 请务必遵守规则!')
            return

    current_position = position.current_position
    avail_position = position.avail_position

    trade_config = config.get_trade_config(code)
    position_unit = trade_config['position_unit']

    # to_position = ((current_position / 2) // 100) * 100
    to_position = ((position_unit / price_trade) // 100) * 100
    to_position = min(avail_position, to_position)

    if not auto:
        auto = trade_config['auto_sell']

    if count == 0:
        count = trade_config['count']
    # count = min(to_position, count)

    # count = to_position
    if count <= 0:
        count = to_position
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
        if not auto:
            popup_warning_message_box_mp('更新 operation detail?', update_operation_detail, detail)
        # update_operation_detail(detail)
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


def create_trade_order(code, price_limited=0):
    """
    单个股持仓交易风险率 <= 1%
    总持仓风险率 <= 6%
    """
    quote = tx.get_kline_data(code, 'day')
    quote_week = quote_db.get_price_info_df_db_week(quote, period_type=config.period_map['day']['long_period'])

    quote = signal.compute_signal(code, 'day', quote)

    price = quote['close'].iloc[-1] if price_limited == 0 else price_limited
    stop_loss = quote['stop_loss_full'].iloc[-1]

    money = query_money()
    # total money, begin of month
    # total_money = money.total_money
    trade_config = config.get_trade_config(code)
    total_money = trade_config['total_money']
    avail_money = money.avail_money

    loss = total_money * config.one_risk_rate
    total_loss_used = trade_manager.db_handler.query_total_risk_amount()
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
           (position * price) / total_money, profitability_ratios, 'TO']

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


def handle_illegal_position(position: trade_data.Position, quota):
    code = position.code

    popup_warning_message_box_mp('[{}]违规仓位, 请务必遵守规则, '.format(code))

    quote = tx.get_realtime_data_sina(code)

    price_trade = quote['close'][-1]
    count = position.avail_position - quota
    logger.warning('[{}]违规仓位, 请务必遵守规则, 持仓[{}]配额[{}], 卖出 {}x{}'.format(
        code, position.current_position, quota, price_trade, count))
    white_list = config.get_white_list()
    if code in white_list:
        logger.warning('[{}] 在[白名单]之中, 不做任何处理, 请确认白名单的合理性!'.format(code))
        return

    sell(code, price_trade=price_trade, count=count, auto=True)


def patrol():
    position_list = query_current_position()
    for position in position_list:
        quota = trade_manager.db_handler.query_quota_position(position.code)
        if not quota:
            handle_illegal_position(position, quota)
            continue
        if position.current_position > quota:
            handle_illegal_position(position, quota)
            continue

        quote = tx.get_kline_data(position.code)
        error = check_list(quote)
        if error != ERROR.OK:
            logger.info('{} - {}'.format(position.code, error.value))
            handle_illegal_position(position, quota)


def create_position_price_limited():
    order_map = trade_manager.db_handler.query_trade_order_map(status='TO')
    for code, trade_order in order_map.items():
        quote = tx.get_realtime_data_sina(code)
        close = quote['close'][-1]
        count = trade_order.position
        date = trade_order.date
        if close > trade_order.open_price:
            logger.info('建仓 限价交易单[{} {}] {}x{}'.format(date, code, close, count))
            buy(code, price_trade=close, price_limited=close, count=count, period='day', auto=True)
            db_handler.update_trade_order_status(trade_order.date, code, 'ING')
