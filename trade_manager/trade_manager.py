# -*- coding: utf-8 -*-
import datetime
import threading
import time

import indicator
from acquisition import tx, quote_db
from config import config
from config.config import Policy, ERROR
from data_structure import trade_data
from indicator import atr, ema, dynamical_system, relative_price_strength, ad
from pointor import signal, signal_stop_loss
from server import config as svr_config
import selector
from . import tradeapi, db_handler
from util import mysqlcli, dt, qt_util

from util.log import logger
from util.qt_util import popup_warning_message_box_mp, popup_info_message_box_mp, popup_warning_message_box


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


def query_position_ex(account_id):
    code_list = []
    position_list = db_handler.query_current_position(account_id)
    code_list.extend([position.code for position in position_list])

    for status in ['TO', 'ING']:
        code_name_map = db_handler.query_trade_order_map(account_id, status=status)
        code_list_tmp = [code for code in code_name_map.keys() if code not in code_list]
        code_list_tmp.sort()
        code_list.extend(code_list_tmp)

    code_list_tmp = []
    with open('data/portfolio.txt', encoding='utf8') as fp:
        for code_name in fp:
            code_name = code_name.strip()
            if not code_name:
                continue
            code_list_tmp.append(code_name.split()[0])
    code_list_tmp.sort()
    code_list.extend(code_list_tmp)

    return code_list


def query_withdraw_order(account_id):
    order_list = tradeapi.query_withdraw_order(account_id)
    return order_list


def compute_unsync(position: trade_data.Position):
    sold_position_in_operation_detail = query_position_in_operation_detail(position.code)
    position.avail_position -= sold_position_in_operation_detail
    position.current_position -= sold_position_in_operation_detail

    sold_position_in_operation_detail = query_position_in_operation_detail(position.code, direct='B')
    position.current_position += sold_position_in_operation_detail


def query_position(account_id, code):
    """
    可以卖的股数
    还可以买的股数
    """
    position = db_handler.query_position(account_id, code)
    if not position:
        return

    compute_unsync(position)

    return position


def query_current_position(account_id):
    """
    可以卖的股数
    还可以买的股数
    """
    position_list = db_handler.query_current_position(account_id)
    for position in position_list:
        compute_unsync(position)

    return position_list


def query_money(account_id):
    money = db_handler.query_money(account_id)
    money_in_operation_detail = query_money_in_operation_detail(account_id)
    money.avail_money -= money_in_operation_detail

    return money


def query_operation_detail(account_id, code=None):
    """
    可以卖的股数
    还可以买的股数
    """
    detail_list = db_handler.query_operation_details(account_id, code)

    return detail_list


def query_money_in_operation_detail(account_id, code=None, trade_date=None):
    if not trade_date:
        trade_date = datetime.date.today()
    detail_list = db_handler.query_operation_details(account_id, date=trade_date)

    money = 0
    for detail in detail_list:
        money += detail.price_trade * detail.count

    return money


def query_position_in_operation_detail(account_id, code=None, trade_date=None, direct='S'):
    if not trade_date:
        trade_date = datetime.date.today()
    detail_list = db_handler.query_operation_details(account_id, code, trade_date)

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


def sync_impl(account_id, trade_date):
    """
    sync previous trade date's data
    run at 9:00 on trade day
    """
    now = datetime.datetime.now()
    # if now.hour > 9 or (now.hour == 9 and now.minute > 14):
    #     return

    # position
    position_list = tradeapi.query_position(account_id)
    if position_list:
        order_ing_map = db_handler.query_trade_order_map(account_id, status='ING')
        order_to_map = db_handler.query_trade_order_map(account_id, status='TO')
        for i in range(len(position_list)):
            position = position_list[i]
            code = position.code
            trade_config = config.get_trade_config(code)
            if 'profit' in trade_config:
                position_list[i].add_profile(trade_config['profit'])
            position_list[i].avail_position = position.current_position

            # trade order
            trade_order_ing = order_ing_map.pop(code) if code in order_ing_map else None
            trade_order_to = order_to_map.pop(code) if code in order_to_map else None
            if position.current_position == 0 and trade_order_ing:
                db_handler.update_trade_order_status(account_id, trade_order_ing.date, code, 'ED')
            if position.current_position > 0 and trade_order_to:
                db_handler.update_trade_order_status(account_id, trade_order_to.date, code, 'ING')

        db_handler.save_positions(account_id, position_list, sync=True)

        for code, trade_order in order_ing_map.items():
            db_handler.update_trade_order_status(account_id, trade_order.date, code, 'ED')
        logger.info('update trade order')

    if position_list is None:
        logger.warning('sync position failed')
    else:
        logger.info('sync position ok')

    # money
    money = tradeapi.get_asset(account_id)
    if money:
        ps = db_handler.query_current_position(account_id)
        money.profit = float(sum([p.profit_total for p in ps]))

        trade_config = config.get_trade_config()
        money.profit += trade_config['not_in_position_profit']
        money.update_origin(money.net_money - money.profit - trade_config['debt'][account_id], trade_config['period'])

        db_handler.save_money(account_id, money, sync=True)

    if money is None:
        logger.warning('sync money failed')
    else:
        logger.info('sync money ok')

    # operation detailtotal_money
    operation_detail = tradeapi.query_operation_detail(account_id)
    if operation_detail:
        # trade_date = datetime.date(2021, 9, 28)
        _date = dt.get_pre_trade_date(trade_date) if trade_date == now.date() else trade_date
        operation_detail = [detail for detail in operation_detail if detail.trade_time.date() == _date]
        db_handler.save_operation_details(account_id, operation_detail, _date, sync=True)

    if operation_detail is None:
        logger.warning('sync operation detail failed')
    else:
        logger.info('sync operation detail ok')




def sync():
    r = False
    m_date = ''
    p_date = ''
    trade_date = dt.get_trade_date()
    for account_id in [svr_config.ACCOUNT_ID_PT, svr_config.ACCOUNT_ID_XY]:
        if account_id == svr_config.ACCOUNT_ID_PT:
            continue
        sync_impl(account_id, trade_date)

        m = db_handler.query_money(account_id)
        ps = db_handler.query_current_position(account_id)
        p = ps[0] if ps else None
        if (m and m.date == trade_date) and (not p or p.date == trade_date):
            r = True
            m_date = m.date
            p_date = p.date
    # o = db_handler.query_operation_details()
    if r:
        qt_util.popup_info_message_box_mp('[{}] [{}]\nsync account OK'.format(m_date, p_date))
    else:
        qt_util.popup_warning_message_box_mp('[{}] [{}]\nsync account FAILED'.format(m_date, p_date))


def check_quota(code, direction):
    """
    巡检, 周期巡检超出配额的已有仓位
    """
    current_position = query_position(code)
    quota_position = db_handler.query_quota_position()
    if current_position.current_position > quota_position:
        return False
    return True


def update_operation_detail(detail):
    db_handler.save_operation_details([detail])


def check_list(quote, period):
    from indicator import second_stage as second_stage_indicator
    quote = second_stage_indicator.second_stage(quote, period)
    if not quote['second_stage'][-1]:
        return ERROR.E_SECOND_STAGE

    quote = dynamical_system.dynamical_system_dual_period(quote, period='day')
    if quote['dyn_sys'].iloc[-1] < 0 or quote['dyn_sys_long_period'].iloc[-1] < 0:
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
    if quote['rpsmaq'][-1] < quote['erpsmaq'][-1]:
        return ERROR.E_WEAKER_THAN_MARKET

    quote = ad.compute_ad(quote)
    if quote['ad'][-1] < quote['ad_ma'][-1]:
        return ERROR.E_AD_INC

    return ERROR.OK


def buy(account_id, op_type, code, price_trade, price_limited=0, count=0, period='day', policy=None, auto=None):
    """
    单次交易仓位: min(加仓至最大配额, 可用全部资金对应仓位)
    """
    position_quota = db_handler.query_quota_position(account_id, code)
    # check #1
    if not position_quota:
        popup_warning_message_box_mp('请先创建交易指令单, 请务必遵守规则!')
        return

    if period == 'day' and policy != Policy.DEVIATION:
        quote = tx.get_kline_data(code)
        error = check_list(quote, 'day')
        if error != ERROR.OK:
            popup_warning_message_box_mp(error.value)
            return

    # position = query_position(account_id, code)
    positions = tradeapi.query_position(account_id, code)
    position = positions[0] if positions else None

    # check #2
    if position and position.profit_total_percent < 0:
        popup_warning_message_box_mp('[补仓] - 严禁补仓, 当前亏损[{}%], 请务必遵守规则!'.format(position.profit_total_percent))
        return

    current_position = position.current_position if position else 0

    avail_position = position_quota - current_position

    # check #3
    if avail_position < 100:
        popup_warning_message_box_mp('配额已用完, 请务必遵守规则!')
        avail_position = 0
        return

    # quote = tx.get_realtime_data_sina(code)
    # money = query_money(account_id)
    money = tradeapi.get_asset(account_id)
    max_position = money.avail_money / (price_limited if price_limited > 0 else price_trade * 1.01) // 100 * 100

    trade_config = config.get_trade_config(code)
    position_unit = trade_config['position_unit']
    max_position = min(max_position, (position_unit / price_trade) // 100 * 100)
    if not auto:
        auto = trade_config['auto_buy']

    if count == 0 and 'count' in trade_config:
        count = trade_config['count']
    # avail_position = min(avail_position, count)

    if count <= 0:
        count = min(max_position, avail_position)

    used = max(position.market_value, position.cost) if position else 0
    if (count * price_trade + used) * 4 > money.origin:
        popup_warning_message_box_mp('[重仓] - 严禁重仓, 当前仓位[{}%], 请务必遵守规则!'.format(
            round(100 * used / float(money.origin), 2)))
        return

    order(account_id, op_type, 'B', code, price_trade=price_trade, price_limited=price_limited, count=count, auto=auto)
    position = position if position else trade_data.Position(code, count, 0, price_limited, price_trade, 0)
    db_handler.save_positions(account_id, [position])


def sell(account_id, op_type, code, price_trade, price_limited=0, count=0, period='day', policy=None, auto=None):
    """
    单次交易仓位: 可用仓位   # min(总仓位/2, 可用仓位)
    """
    # position = query_position(account_id, code)
    positions = tradeapi.query_position(account_id, code)
    position = positions[0] if positions else None

    if not position:
        popup_warning_message_box_mp('没有 [{}] 持仓!'.format(code))
        return

    if period == 'day' and (not policy or (policy != Policy.DEVIATION and policy != Policy.CHANNEL)):
        quote = tx.get_kline_data(code)
        quote = dynamical_system.dynamical_system_dual_period(quote, period='day')
        if quote['dyn_sys'].iloc[-1] >= 0 and quote['dyn_sys_long_period'].iloc[-1] >= 0:
            popup_warning_message_box_mp('动力系统不为红色, 禁止清仓, 请务必遵守规则!')
            return

        ema12 = quote['close'].ewm(span=12, adjust=False).mean()
        ema26 = quote['close'].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        if macd_line[-1] > macd_line[-2] and macd_line[-1] > 0 and macd_signal[-1] > macd_signal[-2]:
            popup_warning_message_box_mp('MACD LINE [> 0] 且 [向上], MACD SIGNAL [向上], 禁止清仓, 请务必遵守规则!')
            return

    current_position = position.current_position
    avail_position = position.avail_position

    trade_config = config.get_trade_config(code)
    position_unit = trade_config['position_unit']

    # to_position = ((current_position / 2) // 100) * 100
    to_position = ((position_unit / price_trade) // 100) * 100
    to_position = min(avail_position, to_position)

    if auto is None:
        auto = trade_config['auto_sell']

    if count == 0 and 'count' in trade_config:
        count = trade_config['count']
    # count = min(to_position, count)

    # count = to_position
    if count <= 0:
        count = to_position
    # operation = TradeManager.get_operation()
    # operation.__sell(code, count, price, auto=auto)
    order(account_id, op_type, 'S', code, price_trade=price_trade, price_limited=price_limited, count=count, auto=auto)


def order(account_id, op_type, direct, code, price_trade, price_limited=0, count=0, auto=False):
    try:
        count = count // 100 * 100
        tradeapi.order(account_id, op_type, direct, code, count, price_limited, auto)
        now = datetime.datetime.now()
        price_ed = 0   # 成交的价格
        count = count * (1 if direct == 'B' else -1)
        detail = trade_data.OperationDetail(now, code, price_ed, price_trade, price_limited, count)

        if auto and price_limited == 0:
            threading.Thread(target=assure_finish, args=(account_id, op_type, code, count, now)).start()
        if not auto:
            popup_warning_message_box_mp('更新 operation detail?', update_operation_detail, detail)
        # update_operation_detail(detail)
    except Exception as e:
        print(e)


def assure_finish(account_id, op_type, direct, code, count, trade_time):
    for i in range(10):
        time.sleep(5)
        count_to = wait_finish(account_id, op_type, direct, code, count, trade_time)
        if count_to == -1:
            logger.warning('something error, continue')
            continue
        re_order(account_id, op_type, direct, code, count)
    logger.warning(direct, code, count, trade_time, 'unfinished')


def wait_finish(account_id, op_type, direct, code, count, trade_time):
    count_to = 0

    orders: [trade_data.WithdrawOrder] = query_withdraw_order(account_id)
    if not orders:
        return -1

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


def re_order(account_id, op_type, direct, code, count):
    # details = db_handler.query_operation_details(date=datetime.date.today())
    # details = [detail for detail in details if detail.price_limited == 0 and detail.count > 0]

    # notify()
    withdraw()
    tradeapi.order(account_id, op_type, direct, code, count=count, auto=True)


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


def create_trade_order(account_id, code, price_limited, stop_loss, strategy):
    """
    单个股持仓交易风险率 <= 1%
    总持仓风险率 <= 6%
    """
    quote = tx.get_kline_data(code, 'day')
    quote_week = quote_db.resample_quote(quote, period_type=config.period_map['day']['long_period'])

    price = quote['close'].iloc[-1] if price_limited == 0 else price_limited
    if not stop_loss:
        # quote = signal.compute_signal(code, 'day', quote)
        # quote = signal_stop_loss.compute_index(quote, 'day')
        # stop_loss = quote['stop_loss_full'].iloc[-1]

        # quote = indicator.atr.compute_atr(quote)
        # stop_loss = max(quote[config.stop_loss_atr_price][-10:]) - config.stop_loss_atr_ratio * quote['atr'][-1]

        stop_loss = price * 0.96
        stop_loss = round(stop_loss, 2)

    money = query_money(account_id)
    # total money, begin of month
    # total_money = money.total_money
    total_money = float(money.origin)   # 投入总资金
    # avail_money = float(money.avail_money)

    loss = total_money * config.one_risk_rate
    total_loss_used = db_handler.query_total_risk_amount(account_id)
    total_loss_remain = total_money * config.total_risk_rate - total_loss_used

    loss = min(loss, total_loss_remain)
    position = loss / (price - stop_loss) // 100 * 100
    # 创建交易指令单, 可以先不考虑可用的资金是否足够
    # position = min(position, avail_money / price // 100 * 100)
    if position < 100:
        popup_info_message_box_mp('create trade order failed\nposition < 100')
        return False

    capital_quota = position * price
    capital_quota_by_trade_rule = money.origin * 0.25
    capital_quota = min(capital_quota, capital_quota_by_trade_rule)
    position = (capital_quota / price) // 100 * 100

    capital_quota_pct = round(100 * capital_quota / money.origin, 2)
    if capital_quota_pct < 20:
        popup_info_message_box_mp('create trade order failed\nposition pct is [{}%]\nless than [20%]'.format(
            capital_quota_pct))
        return False

    # 止盈价格, 需要根据具体的行情走势确定
    # stop_profit = compute_stop_profit(quote_week)
    #
    # profitability_ratios = (stop_profit - price) / (price - stop_loss)
    # if profitability_ratios < 2:
    #     return

    stop_profit = None
    profitability_ratios = None
    risk_rate = round(100 * (1 - stop_loss / price), 2)
    risk_rate_total = round(100 * (position * (price - stop_loss)) / total_money, 2)
    if risk_rate > config.one_risk_rate or risk_rate_total > config.total_risk_rate:
        popup_info_message_box_mp('create trade order failed\nrisk rate exceed\npos: [{}%] total: [{}%]'.format(
            risk_rate, risk_rate_total))
        return False

    strategy_in_db = strategy[:strategy.index('_signal_enter')]

    trade_order_info = 'code: {}\ntry_price: {}\nstop_loss: {}\ncapital_quota: \ncapital_quota_pct: {}\nposition: \n' \
                       'risk_rate: {}\nrisk_rate_total: {}\nstrategy: {}'.format(
        code, price, stop_loss, capital_quota, capital_quota_pct, position, risk_rate, risk_rate_total, strategy)
    click_ok = popup_warning_message_box('info', trade_order_info)
    if not click_ok:
        return False

    val = [datetime.date.today(), code, capital_quota, position, price, stop_loss, stop_profit,
           risk_rate, risk_rate_total, profitability_ratios, strategy_in_db, 'TO', svr_config.ACCOUNT_ID_XY]

    val = tuple(val)

    keys = ['date', 'code', 'capital_quota', '`position`', 'try_price', 'stop_loss',
            'stop_profit', 'risk_rate', 'risk_rate_total', 'profitability_ratios', 'strategy', 'status', 'account_id']

    key = ', '.join(keys)
    fmt_list = ['%s' for i in keys]
    fmt = ', '.join(fmt_list)
    sql = "insert into {} ({}) values ({})".format(config.sql_tab_trade_order, key, fmt)
    with mysqlcli.get_cursor() as c:
        try:
            sql_exists = "select code, stop_loss from trade_order " \
                         "where code = %s and account_id = %s and status in ('TO', 'ING')"
            c.execute(sql_exists, (code, account_id))
            r = c.fetchone()
            if r:
                stop_loss_o = round(r['stop_loss'], 2)
                msg = 'trade order for [{}] exists, stop loss [{}] -> [{}]'.format(code, stop_loss_o, stop_loss)
                popup_info_message_box_mp(msg, db_handler.update_trade_order_stop_loss,
                                          account_id, code, stop_loss, risk_rate, risk_rate_total)
                return False
            c.execute(sql, val)
        except Exception as e:
            print(e)
            return False

    return True


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
        quota = db_handler.query_quota_position(position.code)
        if not quota:
            handle_illegal_position(position, quota)
            continue
        if position.current_position > quota:
            handle_illegal_position(position, quota)
            continue

        quote = tx.get_kline_data(position.code)
        error = check_list(quote, 'day')
        if error != ERROR.OK:
            logger.info('{} - {}'.format(position.code, error.value))
            handle_illegal_position(position, quota)


def create_position_price_limited():
    account_id = svr_config.ACCOUNT_ID_XY
    order_map = db_handler.query_trade_order_map(account_id, status='TO')
    for code, trade_order in order_map.items():
        quote = tx.get_realtime_data_sina(code)
        close = quote['close'][-1]
        count = trade_order.position
        date = trade_order.date
        if close > trade_order.try_price:
            logger.info('建仓 限价交易单[{} {}] {}x{}'.format(date, code, close, count))
            buy(code, price_trade=close, price_limited=close, count=count, period='day', auto=True)
            db_handler.update_trade_order_status(trade_order.date, code, 'ING')
