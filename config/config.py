import glob
from enum import Enum

import util.util
from config.confighandler import ConfigHandler

import os
cwd = os.getcwd()
# ch = ConfigHandler(os.path.join(os.getcwd(), 'config', 'config.ini'), 'db')

# config_dir = '../config' if 'test' in os.getcwd() else 'config'
config_dir = os.path.dirname(__file__)

ch = ConfigHandler(os.path.join(config_dir, 'config.ini'), 'db')

db_host = ch.db_host
db = ch.db
db_user = ch.db_user
db_passwd = ch.db_passwd
sql_tab_basic_info = ch.sql_table_basic_info
sql_tab_quote = ch.sql_table_quote
sql_tab_selected = ch.sql_table_selected
sql_tab_selected_history = ch.sql_table_selected_history
sql_tab_bought = ch.sql_table_bought
sql_tab_cleared = ch.sql_table_cleared
sql_tab_operation_detail = ch.sql_table_operation_detail
sql_tab_operation_detail_history = ch.sql_table_operation_detail_history
sql_tab_trade_order = ch.sql_table_trade_order
sql_tab_asset = ch.sql_table_asset
sql_tab_position = ch.sql_table_position
sql_tab_equity = ch.sql_table_equity
sql_tab_market = ch.sql_table_market

quote_columns = ['code', 'name', 'open', 'close', 'high', 'low', 'volume', 'amount', 'price_change', 'yest_close',
                 'percent', 'turnover_ratio', 'per', 'pb', 'mktcap', 'nmc']

charg = ConfigHandler(os.path.join(config_dir, 'config.ini'), 'arg')
check_per_sec = charg.check_per_sec

###

emulate = True
emulate = False
monitoring = False
monitoring = True
if emulate:
    monitoring = True

# data_config_trade
auto_active_wnd = 1
auto_open_stock_graph_half = 1
auto_open_stock_graph_full = 0
auto_trade_half = 1
auto_trade_full = 0

class cfg:
    auto_active_wnd = 1
    auto_open_stock_graph_half = 1
    auto_open_stock_graph_full = 0
    auto_trade_half = 1
    auto_trade_full = 0


def cfg_auto_active_wnd(val):
    cfg.auto_active_wnd = val


def cfg_auto_open_stock_graph_half(val):
    cfg.auto_open_stock_graph_half = val


def cfg_auto_open_stock_graph_full(val):
    cfg.auto_open_stock_graph_full = val


def cfg_auto_trade_half(val):
    cfg.auto_trade_half = val


def cfg_auto_trade_full(val):
    cfg.auto_trade_full = val


dict_data_config_trade = {
    'auto_active_wnd': cfg_auto_active_wnd,
    'auto_open_stock_graph_half': cfg_auto_open_stock_graph_half,
    'auto_open_stock_graph_full': cfg_auto_open_stock_graph_full,
    'auto_trade_half': cfg_auto_trade_half,
    'auto_trade_full': cfg_auto_trade_full
}


def cfg_data(key, val):
    dict_data_config_trade.get(key)(int(val))


"""
注意,
通达信与中信证券交易软件操作界面并不相同
中信证券光标会自动跳转到'买入数量'
国金证券还没有测试
"""

pid = 0
hwnd = 0
start_time_am = 0
start_time_pm = 0

# 转向 逆转 突破 异动
indicator_h = {
    'zx_up': 4,
    'lz_up': 2,
    'tp_up': 1,
    'zx_down': -4,
    'lz_down': -2,
    'tp_down': -1,
    'yd_up': 1,
    'yd_down': -1
}

indicator_l = {
    'zx_up': 2,
    'lz_up': 1,
    'tp_up': 0.5,
    'zx_down': -2,
    'lz_down': -1,
    'tp_down': -0.5,
    'yd_up': 1,
    'yd_down': -1
}

if emulate:
    indicator = indicator_h
else:
    indicator = indicator_l

if emulate:
    wait_time_ll = 0.1
    wait_time_l = 0.1
    wait_time_m = 0.1
    wait_time_s = 0.1
    wait_time_ss = 0.1
    alert_interval_time = 1
    alert_startup_time = 1
else:
    wait_time_ll = 0.5  # 10
    wait_time_l = 0.5  # 5
    wait_time_m = 0.5  # 1
    wait_time_s = 0.5
    wait_time_ss = 0.1
    alert_interval_time = 60
    alert_startup_time = 300


wait_time = wait_time_m

mouse_clk_x = 800
mouse_clk_y = 300

dbip = '127.0.0.1'
dbport = 6379
dbpassword = ''

cmd_buy_tdx = '221'
cmd_sell_tdx = '223'

cfg_file_trade = ''
cfg_file_trade_stocks = ''

stocks_realtime_info = {}

ChinaStockIndexList = [
    "000001",  # sh000001 上证指数
    "399001",  # sz399001 深证成指
    "000300",  # sh000300 沪深300
    "399005",  # sz399005 中小板指
    "399006",  # sz399006 创业板指
    "000003",  # sh000003 B股指数
]

# tdx_home = r"C:\new_tdx"
tdx_home = "/home/shuhm/PlayOnLinux's virtual drives/tdx/drive_c/new_jyplug"
tdx_window_name = '通达信金融终端V7.56'

accounts = {'tdx_zxs': {'pid': '', 'hwnd': '', 'hwnd_name': '', 'exe_path': ''},
            'ths_gjs': {'pid': '', 'hwnd': '', 'hwnd_name': '', 'exe_path': 'D:\\BIN\\全能行证券交易终端\\xiadan.exe'},
            'ths_gjl': {'pid': '', 'hwnd': '', 'hwnd_name': '', 'exe_path': 'D:\\BIN\\weituo\\国金证券\\xiadan.exe'},  #'D:\\BIN\\weituo\\国金证券\\xiadan.exe'},
            'hs_s': {'pid': '', 'hwnd': '', 'hwnd_name': '', 'exe_path': 'D:\\BIN\\HOMS钱江版(独立委托版)\\Trading.exe'}}

dict_exe_path_account = {'D:\\BIN\\全能行证券交易终端\\xiadan.exe': 'ths_gjs',
                         'D:\\BIN\\weituo\\国金证券\\xiadan.exe': 'ths_gjl',
                         'D:\\BIN\\HOMS钱江版(独立委托版)\\Trading.exe': 'hs_s'}

stages = ['3', '35', '354', '352', '3523', '3526', '35264', '35261', '352613', '352614',
          '4', '42', '423', '425', '4254', '4251', '42513', '42516', '425164', '425163']


key_list = ['code', 'name', 'trading_date', 'open', 'high', 'low', 'close', 'volume', 'amount']

'''
selector
'''
T = 'W'
# T = 'D'
USING_LONG_PERIOD = True
MAX_CLOSE_PAST_DAYS = 30 * 9
DECLINE_RATIO = 0.5

DAY_MIN = 250
WEEK_MIN = 50
MIN = DAY_MIN if T == 'D' else WEEK_MIN

DZ_MIN = 120 if T == 'D' else 25
DD_MIN = 120 if T == 'D' else 25

ALMOST_EQUAL = 1
MA_NUM = 5
MAS = [5, 10, 20, 30, 60, 120, 250]

# 多头
DT_DAY = 1
DT_LAST_N_MA = 4
# 多头最小涨幅, (ma5 - ma60)/ma60 * 100
DT_MIN_UP_P = 5
# boll中线, 10天以前
DT_BOLL_DAY = 10
DT_BOLL_DAY_AGO = 60
DT_SAR_DAY = 5

# 回调
HT_MA_N = 10
HT_RANGE = 10

# 大涨
# 1.1^5 = 1.61
DZ_PERCENT_LIMIT = 11 if T == 'D' else 61

# 大跌
# 0.9^5 = 59.04
DD_PERCENT_LIMIT = 11 if T == 'D' else 41

# 横盘
STEP_BOLL_BACK = 20 if T == 'D' else 4
STEP_BOLL_DURATION = 60 if T == 'D' else 12

STEP_DAY = 1
STEP_DURATION = -1
STEP_FIRST_N_MA = 5


SECOND_DAY = 1
SECOND_LAST_N_MA = 4

# 突破
TP_MA_N = 20
TP_RANGE = 5

# 跌
D_PERCENT_EXP = 15
D_NDAY = 5

# 涨
Z_PERCENT_EXP = 15
Z_NDAY = 5

# 振幅
ZF_NDAY = 20
ZF_PERCENT_AVG_MAX = 5
ZF_PERCENT_MIN = 2
ZF_PERCENT_GT_MIN = 90

# 强度
QD_NDAY = 120
QD_PERCENT_MAX = 20
QD_PERCENT_HT_MAX = 20
QD_PERCENT = 20
QD_PERCENT_MIN = 10

''' macd '''
macd_threshold_hp = 0.2 #
macd_threshold_0 = 0.03 # 高价股与低价股 相同走势 macd 值相差很大

# 转向 突破 逆转
TR_ZX = 6
TR_TP = 3
TR_LZ = 3

B = 'B'
S = 'S'
N = ''


def gen_signal_config_path(period):
    if period.startswith('m'):
        period = '_rt'
    else:
        period = ''
    return os.path.join(config_dir, 'signal{}.json'.format(period))


def get_a_signal_list(key, period):
    import json
    fp = open(gen_signal_config_path(period))
    signals = json.load(fp)

    fp.close()

    d: dict = signals[key]

    return d


def get_signal_enter_list(period):
    d = get_a_signal_list('signal_enter', period)
    return [s for s, enabled in d.items() if enabled]


def get_all_signal_enter(period):
    d = get_a_signal_list('signal_enter', period)
    return d


def get_signal_enter_deviation(period):
    d = get_a_signal_list('signal_enter', period)
    return [s for s, enabled in d.items() if 'deviation' in s and enabled]


def get_signal_exit_list(period):
    d = get_a_signal_list('signal_exit', period)
    return [s for s, enabled in d.items() if enabled]


def get_all_signal_exit(period):
    d = get_a_signal_list('signal_exit', period)
    return d


def get_signal_exit_deviation(period):
    d = get_a_signal_list('signal_exit', period)
    return [s for s, enabled in d.items() if 'deviation' in s and enabled]


def get_all_signal(period):
    signals = {}
    signals.update(get_all_signal_enter(period))
    signals.update(get_all_signal_exit(period))
    return signals


def get_signal_list(period):
    signals = []
    signals.extend(get_signal_enter_list(period))
    signals.extend(get_signal_exit_list(period))
    return signals


def enabled_signal(signal, period):
    signals = get_signal_list(period)
    return signal in signals


def enable_signal(signal, enable, period):
    # cache_path = util.util.get_cache_dir()
    # files = glob.glob(os.path.join(cache_path, '[0-9]*-[0-9]*-*.csv'))  # '[0-9]{6}-[0-9]{8}-.*.csv'))
    # for f in files:
    #     os.remove(f)
    enable = True if enable else False
    import json
    with open(gen_signal_config_path(period), 'r+') as fp:
        signals = json.load(fp)

        key = signal[signal.index('signal'):]
        for s, enabled in signals[key].items():
            if s == signal:
                signals[key][s] = enable
                break

        # next is OK
        # fp.truncate(0)
        # fp.seek(0)
        # json.dump(signals, fp, indent=2)

    with open(gen_signal_config_path(period), 'w', newline='\n') as fp:
        json.dump(signals, fp, indent=2)


def get_white_list():
    import json
    with open(os.path.join(config_dir, 'trade_manager.json')) as fp:
        trade_manager_config = json.load(fp)

        return trade_manager_config['white_list']


def get_ignore_list():
    import json
    with open(os.path.join(config_dir, 'trade_manager.json')) as fp:
        trade_manager_config = json.load(fp)

        return trade_manager_config['ignore_list']


period_map = {
        'm1': {'period': '1min', 'long_period': '5min', 'kline_long_period': 'm5'},
        'm5': {'period': '5min', 'long_period': '30min', 'kline_long_period': 'm30'},
        'm15': {'period': '15min', 'long_period': '30min', 'kline_long_period': 'm30'},
        'm30': {'period': '30min', 'long_period': 'D', 'kline_long_period': 'day'},
        'm60': {'period': '60min', 'long_period': 'D', 'kline_long_period': 'day'},
        'day': {'period': 'D', 'long_period': 'W', 'kline_long_period': 'week'},
        'week': {'period': 'W', 'long_period': 'M', 'kline_long_period': 'month'},
    }

period_price_diff_ratio_deviation_map = {
    'm1': 0.998,
    'm5': 0.995,
    'm15': 0.995,
    'm30': 0.99,
    'm60': 0.99,
    'day': 0.98,
    'week': 0.96
}

# period_price_diff_ratio_atr_map = {
#     'm1': 5,
#     'm5': 4,
#     'm15': 4,
#     'm30': 4,
#     'm60': 4,
#     'day': 3,
#     'week': 3
# }

period_price_diff_ratio_atr_map = {
    'm1': 3,
    'm5': 3,
    'm15': 3,
    'm30': 3,
    'm60': 3,
    'day': 3,
    'week': 3
}

stop_loss_atr_ratio = 2
stop_loss_atr_back_days = 10
stop_loss_atr_price = 'high'


def is_long_period(period):
    return period in ['week', 'm30']


def get_config_options():
    import json
    with open(os.path.join(config_dir, 'config.json')) as fp:
        options = json.load(fp)
        return options


def get_trade_config(code=None):
    import json
    fp = open(os.path.join(config_dir, 'config.json'))
    trade = json.load(fp)

    fp.close()

    d: dict = trade['global']
    if code in trade:
        d.update(trade[code])

    return d


def get_tradeapi_server():
    import json
    fp = open(os.path.join(config_dir, 'config.json'))
    trade = json.load(fp)

    fp.close()

    return trade['tradeapi_server']['base_url']


import json
fp = open(os.path.join(config_dir, 'config.json'))
global_config = json.load(fp)
fp.close()

update_candidate_pool = global_config['scan']['update_candidate_pool']


def get_scan_strategy_name_list():
    import json
    fp = open(os.path.join(config_dir, 'config.json'))
    trade = json.load(fp)

    fp.close()

    return trade['scan']['strategy_name_list']


# risk management
total_risk_rate = 0.05   # 5% = 1.25% * 4
one_risk_rate = 0.0125   # 1.25%

#
period_price_diff_ratio_resistance_support_map = {
    'm1': 0.01,
    'm5': 0.01,
    'm15': 0.01,
    'm30': 0.02,
    'm60': 0.02,
    'day': 0.04,
    'week': 0.04
}

resistance_over_rate = 0.02
support_under_rate = 0.02
resistance_support_backdays = 1

value_return_mas = [26]
step_mas = [20, 30, 60]
resistance_day = 60
support_day = 10

supplemental_signal_path = os.path.join(config_dir, '..', 'data/trade.csv')
signal_log_path = os.path.join(config_dir, '..', 'log/signal.log')
scan_log_path = os.path.join(config_dir, '..', 'log/scan.log')


# 振荡阈值
period_oscillation_threshold_map = {
    'm1': 1.025,
    'm5': 1.025,
    'm15': 1.025,
    'm30': 1.05,
    'm60': 1.05,
    'day': 1.05,
    'week': 1.1
}

period_ema26_oscillation_threshold_map = {
    'm1': 1.025,
    'm5': 1.025,
    'm15': 1.025,
    'm30': 1.05,
    'm60': 1.05,
    'day': 1.05,
    'week': 1.1
}

key_list = ['code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'yest_close', 'percent',
            'rs_rating', 'mktcap']

candidate_strategy_list = ['finance', 'finance_ex', 'fund', 'super', 'hot_strong', 'second_stage',
                           'dyn_sys_green', 'dyn_sys_blue',
                           'strong_base', 'bottom', 'fallen']
traced_strategy_list = ['trend_weak', 'magic_line', 'blt', 'vcp', 'step', 'value_return_ing', 'volume_dry_up_ing']
allow_buy_strategy_list = ['magic_line_breakout', 'blt_breakout', 'vcp_breakout', 'step_breakout', 'base_breakout',
                           'value_return', 'volume_dry_up', 'volume_shrink', 'bull_deviation', 'bull_at_bottom']

strategy_map = {
    'candidate': {'back_day': 1, 'strategies': candidate_strategy_list},
    'traced': {'back_day': 5, 'strategies': traced_strategy_list},
    'allow_buy': {'back_day': 3, 'strategies': allow_buy_strategy_list}
}

SELECTOR_FUND_STOCK_NMC_MAX = 10 * 1000 * 1000 * 1000  # 100万亿  单位万元

stamp_duty = 0.001   # 印花税 卖方
commission = 0.0002   # 佣金 - 中信证券 双向
transfer_fee = 0.00002   # 过户费 上海证券交易所收取 双向

# charge_sell_sz = commission + stamp_duty
# charge_sell_sh = commission + stamp_duty + transfer_fee
# charge_buy_sz = commission
# charge_buy_sh = commission + transfer_fee


def charge(amount, direct, market):
    amount = abs(amount)
    if amount < 1:
        return 0

    cost = max(5, amount * commission)
    if direct == 'S':
        cost += amount * stamp_duty
    if market == 'sh':
        cost += amount * transfer_fee
    return round(cost, 3)


def add_succ_and_pred_maps(cls):
    succ_map = {}
    pred_map = {}
    cur = None
    nxt = None
    for val in cls.__members__.values():
        if cur is None:
            cur = val
        elif nxt is None:
            nxt = val

        if cur is not None and nxt is not None:
            succ_map[cur] = nxt
            pred_map[nxt] = cur
            cur = nxt
            nxt = None
    cls._succ_map = succ_map
    cls._pred_map = pred_map

    def succ(self):
        return self._succ_map[self]

    def pred(self):
        return self._pred_map[self]

    cls.succ = succ
    cls.pred = pred
    return cls


@add_succ_and_pred_maps
class PositionStage(Enum):
    """
    +20% +30% +50% = 100% (+5% +7.5% +12.5% = 25%)
    涉水 建仓 加仓

    -50% -50% = 0%
    减仓 清仓
    """
    EMPTY = 0
    TRY = 0.2
    HALF = 0.5
    FULL = 1
    EX = 1


class Policy(Enum):
    DEFAULT = ''
    DEVIATION = '背离'  # 'deviation'
    EMA_VALUE = '价值回归'  # 'ema value'
    CHANNEL = '通道'  # 'channel'
    FORCE_INDEX = '强力指数'  # 'force index'
    DYNAMICAL_SYSTEM = '动力系统'  # 'dynamical system'
    STOP_LOSS = '止损'  # 'stop loss'
    STOP_PROFIT = '止盈'  # 'stop profit'
    OPEN_PRICE = '建仓价格'


class ERROR(Enum):
    OK = ''
    E_SECOND_STAGE = '不在第二阶段, 禁止买入, 禁止持有, 请务必遵守规则!'
    E_DYNAMICAL_SYSTEM = '动力系统为红色, 禁止买入, 禁止持有, 请务必遵守规则!'
    E_LONG_PERIOD_EMA_INC = '长周期EMA26向下, 禁止买入, 禁止持有, 请务必遵守规则!'
    E_CLOSE_OVER_LONG_PERIOD_EMA = 'CLOSE低于第周期EMA26, 禁止买入, 禁止持有, 请务必遵守规则!'
    E_MACD_LINE_INC = 'MACD线向下, 禁止买入, 禁止持有, 请务必遵守规则!'
    E_WEAKER_THAN_MARKET = '弱于市场, 禁止买入, 禁止持有, 请务必遵守规则!'
    E_AD_INC = 'A/D低于A/D EMA, 禁止买入, 禁止持有, 请务必遵守规则!'


class OscIndicator(Enum):
    FORCE_INDEX = 'force_index'
    ADOSC = 'adosc'
    SKDJ = 'skdj'
    RSI = 'rsi'
