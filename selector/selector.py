# -*- coding: utf-8 -*-

import datetime
import multiprocessing
import functools
import sys

import tqdm

from config import config
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

from selector.plugin import market_deviation, super, bull_at_bottom, second_stage, hot_strong, magic_line
from selector.plugin import ema_value
import indicator.dynamical_system as dynamical_system
import indicator.force_index as force_index

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
    'zf': zf.zf,
    'qd': qd.qd,
    'bull_deviation': market_deviation.market_deviation,   # 牛市背离
    'ema_value': ema_value.ema_value,   # 价值回归
    'super': super.super,
    'second_stage': second_stage.second_stage,   # 第二阶段
    'magic_line': magic_line.magic_line,
    'bull_at_bottom': bull_at_bottom.bull_at_bottom,
    'dyn_sys_green': dynamical_system.dynamical_system_green,
    'dyn_sys_red': dynamical_system.dynamical_system_red,
    'dyn_sys_blue': dynamical_system.dynamical_system_blue,
    'hot_strong': hot_strong.hot_strong,
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

    df = quote_db.get_price_info_df_db(code, 1000, '', 'D', _conn)
    if df.empty:
        logger.info(code, 'no quote')
        return

    ret = None
    if is_match(df, strategy_name):
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

    logger.info('{} [{}] to check {}...'.format(datetime.datetime.now(), len(code_list), strategy_name))

    select_func = functools.partial(_select, strategy_name)

    nproc = multiprocessing.cpu_count()
    with multiprocessing.Pool(nproc) as p:
        # r = p.map(select_func, [code for code in code_list])
        # code_list = [code for code in r if code]

        r = []
        # for i, _ in enumerate(p.imap_unordered(select_func, [code for code in code_list]), 1):
        #     r.append(_)
        #     if i % 100 == 0:
        #         sys.stderr.write('\rdone {0:%}'.format(i/len(code_list)))
        for _ in tqdm.tqdm(p.imap_unordered(select_func, [code for code in code_list]),
                           total=len(code_list), ncols=64):
            r.append(_)

        code_list = [code for code in r if code]

    logger.info('{} {}: {}'.format(datetime.datetime.now(), strategy_name, len(code_list)))

    return code_list


def update_candidate_pool(strategy_list):
    for strategy in strategy_list:
        code_list = basic.get_all_stock_code()
        # code_list = ['000652']
        code_list = select_one_strategy(code_list, strategy)
        # 科创板
        code_list = [code for code in code_list if not code.startswith('688')]
        basic.upsert_candidate_pool(code_list, 'candidate', strategy, ignore_duplicate=False)


def select(strategy_name_list, stock_list: list[tuple], candidate_list=['second_stage']):
    begin = datetime.datetime.now()

    if config.update_candidate_pool:
        update_candidate_pool()

    code_list = basic.get_candidate_stock_code(candidate_list)
    # code_list = basic.get_all_stock_code()
    # code_list = future.get_future_contract_list()
    code_list = [code for code in code_list if int(code[:2]) <= 60]
    # code_list = ['300502']

    strategy_name_list = config.get_scan_strategy_name_list() if not strategy_name_list else strategy_name_list
    for strategy_name in strategy_name_list:
        code_list = select_one_strategy(code_list, strategy_name)
        # for code in code_list:
        #     selected.add_selected(code, strategy_name)
        basic.upsert_candidate_pool(code_list, 'allow_buy', strategy_name)
        logger.info(strategy_name, code_list)

    # code_list.append('300502')
    code_list.sort()

    stock_list = [] if not isinstance(stock_list, list) else stock_list
    for code in code_list:
        stock_list.append((code, basic.get_stock_name(code)))

    end = datetime.datetime.now()

    log = '\n'.join([' '.join(t) for t in stock_list])
    with open(config.scan_log_path, 'a') as f:
        f.writelines('[{}] cost [{}s] [{}][{}] [{}]'.format(
            begin, (end - begin).seconds, ', '.join(candidate_list), ', '.join(strategy_name_list), len(stock_list)))
        f.writelines('\n')
        f.writelines(log)
        f.writelines('\n\n')
