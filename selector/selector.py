#-*- coding: utf-8 -*-

import os
import datetime

import config.config as config
import selector.util as util

import acquisition.basic as basic
import acquisition.quote_db as quote_db

import selector.plugin.hp as hp
import selector.plugin.second_wave as second_wave
import selector.plugin.tp as tp
import selector.plugin.qd as qd

import selector.plugin.z as z
import selector.plugin.d as d

import selector.plugin.zf as zf
import selector.plugin.qd as qd

import selector.plugin.niushibeili as niushibeili
import selector.plugin.dynamical_system as dynamical_system
import selector.plugin.force_index as force_index

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
    'nsbl': niushibeili.niushibeili,
    'dlxt_green': dynamical_system.dynamical_system_green,
    'dlxt_red': dynamical_system.dynamical_system_red,
    'dlxt_blue': dynamical_system.dynamical_system_blue,
    'qlzs_p': force_index.force_index_positive,
    'qlzs_m': force_index.force_index_minus
}

from queue import Empty
from multiprocessing import Queue, Process


def is_match(df, strategy_name):
    if util.filter_quote(df):
        return False

    rc = selector.get(strategy_name)(df)
    if rc:
        return True

    return False


def _select(q, rq, strategy_name):
    import util.mysqlcli as mysqlcli
    _conn = mysqlcli.get_connection()
    while True:
        try:
            code = q.get(True, 0.1)
            df = quote_db.get_price_info_df_db(code, 250, '', config.T, _conn)
            if is_match(df, strategy_name):
                selected.add_selected(code, strategy_name)
                print('{}'.format(code))
                rq.put(code)
        except Empty:
            #print('{0} [{1}]: finished'.format(datetime.datetime.now(), os.getpid()))
            break
        except Exception as e:
            import traceback
            traceback.print_exc()

    _conn.close()


def select(strategy_name):
    r = []
    code_list = basic.get_all_stock_code()
    #code_list = future.get_future_contract_list()

    rq = Queue()

    code_queue = Queue()
    for code in code_list:
        code_queue.put(code)

    nproc = 16
    p_list = [Process(target=_select, args=(code_queue, rq, strategy_name,)) for i in range(nproc)]
    [p.start() for p in p_list]
    [p.join() for p in p_list]

    for _i in range(rq.qsize()):
        r.append(rq.get_nowait())

    return r
