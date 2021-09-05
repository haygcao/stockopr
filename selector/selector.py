# -*- coding: utf-8 -*-

import datetime
import multiprocessing
import functools
import sys

import tqdm

from acquisition import tx
from config import config
from selector import util

import acquisition.basic as basic
import acquisition.quote_db as quote_db

import selector.plugin.hp as hp
import selector.plugin.second_wave as second_wave
import selector.plugin.tp as tp

import selector.plugin.z as z
import selector.plugin.d as d
import selector.plugin.qd as qd

from selector.plugin import market_deviation, super, bull_at_bottom, second_stage, hot_strong, magic_line, \
    base_breakout, blt, vcp, strong_base, amplitude, value_return
from selector.plugin import ema_value
from selector.plugin import dynamical_system
from selector.plugin import force_index
from util import dt, qt_util

from . import selected

# 横盘 第二波 突破 涨 跌 大涨 大跌
from util.log import logger

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
    'amplitude': amplitude.amplitude,
    'bull_deviation': market_deviation.market_deviation,   # 牛市背离
    'ema_value': ema_value.ema_value,   # 价值回归
    'super': super.super,
    'second_stage': second_stage.second_stage,   # 第二阶段
    'magic_line': magic_line.magic_line,
    'base_breakout': base_breakout.base_breakout,
    'value_return': value_return.value_return,
    'blt': blt.blt,
    'vcp': vcp.vcp,
    'strong_base': strong_base.strong_base,
    'bull_at_bottom': bull_at_bottom.bull_at_bottom,
    'dyn_sys_green': dynamical_system.dynamical_system_green,
    'dyn_sys_red': dynamical_system.dynamical_system_red,
    'dyn_sys_blue': dynamical_system.dynamical_system_blue,
    'hot_strong': hot_strong.hot_strong,
    'force_index_p': force_index.force_index_positive,
    'force_index_m': force_index.force_index_minus
}

strategy_map = {
    'value_return': 'traced'
}


def is_match(df, strategy_name, period):
    if util.filter_quote(df):
        return False

    rc = selector.get(strategy_name)(df, period)
    if rc:
        return True

    return False


def _select(strategy_name, period, code):
    import util.mysqlcli as mysqlcli
    # _conn = mysqlcli.get_connection()

    # 无法频繁获取数据
    # if dt.istradetime():
    #     df = tx.get_kline_data(code, 'day')
    # else:
    #     df = quote_db.get_price_info_df_db(code, days=1000, period_type='D')

    df = quote_db.get_price_info_df_db(code, days=1000, period_type='D')
    if df.empty:
        logger.info(code, 'no quote')
        return

    ret = None
    if is_match(df, strategy_name, period):
        # print('{}'.format(code))
        ret = code

    # _conn.close()

    return ret


def select_one_strategy(code_list, strategy_name, period, mp=True):
    """
    https://docs.python.org/3/library/multiprocessing.html
    This means that if you try joining that process you may get a deadlock
    unless you are sure that all items which have been put on the queue have been consumed.
    Similarly, if the child process is non-daemonic then the parent process may hang on exit
    when it tries to join all its non-daemonic children.

    Note that a queue created using a manager does not have this issue.
    """

    logger.info('[{}] to check {}...'.format(len(code_list), strategy_name))

    select_func = functools.partial(_select, strategy_name, period)

    r = []
    if not mp:
        for code in code_list:
            if not select_func(code):
                continue
            r.append(code)
        return r

    nproc = multiprocessing.cpu_count()
    with multiprocessing.Pool(nproc) as p:
        # r = p.map(select_func, [code for code in code_list])
        # code_list = [code for code in r if code]

        # for i, _ in enumerate(p.imap_unordered(select_func, [code for code in code_list]), 1):
        #     r.append(_)
        #     if i % 100 == 0:
        #         sys.stderr.write('\rdone {0:%}'.format(i/len(code_list)))
        for _ in tqdm.tqdm(p.imap_unordered(select_func, [code for code in code_list]),
                           total=len(code_list), ncols=64):
            r.append(_)

        code_list = [code for code in r if code]

    logger.info('{}: {}'.format(strategy_name, len(code_list)))

    return code_list


def update_candidate_pool(strategy_list, period='day'):
    t1 = datetime.datetime.now()
    msg = ''
    for strategy in strategy_list:
        code_list = basic.get_all_stock_code()
        # code_list = ['600331']
        code_list = select_one_strategy(code_list, strategy, period, mp=True)
        # 科创板
        # code_list = [code for code in code_list if not code.startswith('688')]
        msg += '{}: {}\n'.format(strategy, len(code_list))
        basic.upsert_candidate_pool(code_list, 'candidate', strategy, ignore_duplicate=False)

    t2 = datetime.datetime.now()
    cost = (t2 - t1).seconds
    qt_util.popup_info_message_box_mp('update candidate finished in [{}s]\n{}'.format(cost, msg))


def select(strategy_name_list, candidate_list=None, period='day'):
    begin = datetime.datetime.now()

    candidate_list = candidate_list if candidate_list else ['super']
    if config.update_candidate_pool:
        update_candidate_pool(candidate_list)

    code_list = basic.get_candidate_stock_code(candidate_list)
    # code_list = basic.get_all_stock_code()
    # code_list = future.get_future_contract_list()
    # 科创板
    # code_list = [code for code in code_list if int(code[:2]) <= 60]
    # code_list = ['600331']

    strategy_name_list = config.get_scan_strategy_name_list() if not strategy_name_list else strategy_name_list
    for strategy_name in strategy_name_list:
        code_list = select_one_strategy(code_list, strategy_name, period)
        # for code in code_list:
        #     selected.add_selected(code, strategy_name)
        basic.upsert_candidate_pool(code_list, strategy_map.get(strategy_name, 'allow_buy'), strategy_name)
        logger.info(strategy_name, code_list)

    # code_list.append('300502')
    code_list.sort()

    stock_list = []
    for code in code_list:
        stock_list.append((code, basic.get_stock_name(code)))

    end = datetime.datetime.now()
    cost = (end - begin).seconds

    log = '\n'.join([' '.join(t) for t in stock_list])
    with open(config.scan_log_path, 'a') as f:
        f.writelines('[{}] cost [{}s] [{}][{}] [{}]'.format(
            begin, cost, ', '.join(candidate_list), ', '.join(strategy_name_list), len(stock_list)))
        f.writelines('\n')
        f.writelines(log)
        f.writelines('\n\n')

    qt_util.popup_info_message_box_mp('scan finished in [{}s]\ntotal: {}'.format(cost, len(stock_list)))
