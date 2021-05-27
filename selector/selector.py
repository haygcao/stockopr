# -*- coding: utf-8 -*-
import datetime
import multiprocessing
import functools

from selector import util

import acquisition.basic as basic
import acquisition.quote_db as quote_db

import selector.plugin.hp as hp
import selector.plugin.second_wave as second_wave
import selector.plugin.tp as tp

import selector.plugin.z as z
import selector.plugin.d as d

import selector.plugin.zf as zf
import selector.plugin.qd as qd

from selector.plugin import market_deviation, hot_strong
from selector.plugin import ema_value
import indicator.dynamical_system as dynamical_system
import indicator.force_index as force_index

import selector.selected as selected

# 横盘 第二波 突破 涨 跌 大涨 大跌
selector = {
    'hp': hp.hp,
    'hp_p': hp.hp_p,
    'hp_pp': hp.hp_pp,
    'hp_ppp': hp.hp_ppp,
    '2nd': second_wave.second_wave,
    '2nd2': second_wave.second_wave2,
    'tp': tp.tp,
    'qd': qd.qd,
    'z': z.z,
    'dz': z.dz,
    'd': d.d,
    'dd': d.dd,
    'zf': zf.zf,
    'qd': qd.qd,
    'nsbl': market_deviation.market_deviation,   # 牛市背离
    'ema_value': ema_value.ema_value,   # 价值回归
    'hot_strong': hot_strong.hot_strong,
    'dlxt_green': dynamical_system.dynamical_system_green,
    'dlxt_red': dynamical_system.dynamical_system_red,
    'dlxt_blue': dynamical_system.dynamical_system_blue,
    'qlzs_p': force_index.force_index_positive,
    'qlzs_m': force_index.force_index_minus
}


def is_match(df, strategy_name):
    if util.filter_quote(df):
        return False

    rc = selector.get(strategy_name)(df)
    if rc:
        return True

    return False


def _select(strategy_name, code):
    import util.mysqlcli as mysqlcli
    _conn = mysqlcli.get_connection()

    df = quote_db.get_price_info_df_db(code, 500, '', 'D', _conn)

    ret = None
    if is_match(df, strategy_name):
        selected.add_selected(code, strategy_name)
        # print('{}'.format(code))
        ret = code

    _conn.close()

    return ret


def select_one_strategy(code_list, strategy_name):
    """
    https://docs.python.org/3/library/multiprocessing.html
    This means that if you try joining that process you may get a deadlock
    unless you are sure that all items which have been put on the queue have been consumed.
    Similarly, if the child process is non-daemonic then the parent process may hang on exit
    when it tries to join all its non-daemonic children.

    Note that a queue created using a manager does not have this issue.
    """

    print('{} [{}] to check {}...'.format(datetime.datetime.now(), len(code_list), strategy_name))

    select_func = functools.partial(_select, strategy_name)

    nproc = multiprocessing.cpu_count()
    with multiprocessing.Pool(nproc) as p:
        r = p.map(select_func, [code for code in code_list])
        code_list = [code for code in r if code]

    print('{} {}: {}'.format(datetime.datetime.now(), strategy_name, len(code_list)))

    return code_list


def select(strategy_name_list):
    code_list = basic.get_all_stock_code()
    # code_list = future.get_future_contract_list()
    # code_list = ['300502']

    for strategy_name in strategy_name_list:
        code_list = select_one_strategy(code_list, strategy_name)

    return code_list
