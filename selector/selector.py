# -*- coding: utf-8 -*-

import datetime
import multiprocessing
import functools
import os
import pathlib

import pandas
import tqdm

from acquisition import tx
from config import config
from selector import util

import acquisition.basic as basic
import acquisition.quote_db as quote_db

import selector.plugin.step as step
import selector.plugin.second_wave as second_wave
import selector.plugin.step_breakout as step_breakout

import selector.plugin.up as up
import selector.plugin.down as down
import selector.plugin.strong_variability as strong_variability

from selector.plugin import market_deviation, super, bull_at_bottom, second_stage, hot_strong, magic_line, \
    base_breakout, blt, vcp, strong_base, amplitude, signal_config, bottom, volume_dry_up, breakout, finance, fund, \
    trend_weak
from selector.plugin import value_return
from selector.plugin import dynamical_system
from selector.plugin import force_index
from util import qt_util, dt
from util import util as util_util

from . import selected

# 横盘 第二波 突破 涨 跌 大涨 大跌
from util.log import logger

selector = {
    'finance': finance.finance,
    'finance_ex': finance.finance_ex,
    'fund': fund.fund,
    'trend_up': signal_config.mask_config,
    'trend_weak': trend_weak.trend_weak,
    'signal_config': signal_config.signal_config,
    'step': step.step,
    'step_p': step.step_p,
    '2nd': second_wave.second_wave,
    '2nd2': second_wave.second_wave2,
    'qd': strong_variability.strong_variability,
    'up': up.up,
    'up_p': up.up_p,
    'down': down.down,
    'down_p': down.down_p,
    'amplitude': amplitude.amplitude,
    'bull_deviation': market_deviation.market_deviation,   # 牛市背离
    'value_return': value_return.value_return,   # 价值回归
    'value_return_ing': value_return.value_return_ing,
    'super': super.super,
    'second_stage': second_stage.second_stage,   # 第二阶段
    'magic_line': magic_line.magic_line,
    'step_breakout': step_breakout.step_breakout,
    'blt_breakout': breakout.blt_breakout,
    'vcp_breakout': breakout.vcp_breakout,
    'magic_line_breakout': breakout.magic_line_breakout,
    'base_breakout': base_breakout.base_breakout,
    'blt': blt.blt,
    'vcp': vcp.vcp,
    'strong_base': strong_base.strong_base,
    'volume_dry_up': volume_dry_up.volume_dry_up,
    'volume_shrink': volume_dry_up.volume_shrink,
    'volume_dry_up_ing': volume_dry_up.volume_dry_up_ing,
    'bottom': bottom.bottom,
    'fallen': bottom.fallen,
    'bull_at_bottom': bull_at_bottom.bull_at_bottom,
    'dyn_sys_green': dynamical_system.dynamical_system_green,
    'dyn_sys_red': dynamical_system.dynamical_system_red,
    'dyn_sys_blue': dynamical_system.dynamical_system_blue,
    'hot_strong': hot_strong.hot_strong,
    'force_index_p': force_index.force_index_positive,
    'force_index_m': force_index.force_index_minus
}


def get_strategy_status(strategy):
    for status, strategy_info in config.strategy_map.items():
        if strategy in strategy_info['strategies']:
            return status
    raise Exception('{} is UNKNOWN'.format(strategy))


def get_status_backdays(status):
    strategy_info = config.strategy_map[status]
    return strategy_info['back_day']


def is_match(df, strategy_name, period):
    if util.filter_quote(df):
        return False

    status = get_strategy_status(strategy_name)
    backdays = get_status_backdays(status)
    rc = selector.get(strategy_name)(df, period, backdays)
    if rc:
        return True

    return False


def dump(data, file):
    # file = gen_cache_path(data.code[-1], datetime.date.today(), period)
    if os.path.exists(file):
        os.remove(file)

    if 'date' not in data.columns:
        data.insert(len(data.columns), 'date', data.index)

    data.to_csv(file)


def load(file):
    # file = gen_cache_path(code, datetime.date.today(), period)
    data = pandas.read_csv(file, dtype={'code': str})

    data['date'] = pandas.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S')
    # data['code'] = str(data['code'])
    # 将日期列作为行索引
    data.set_index(['date'], inplace=True)
    # data.sort_index(ascending=True, inplace=True)

    return data


def _select(strategy_name, period, code_day_quote):
    import util.mysqlcli as mysqlcli
    # _conn = mysqlcli.get_connection()

    code, day_quote = code_day_quote
    df = quote_db.get_price_info_df_db(code, days=1000, period_type='D')
    if df.empty:
        logger.info(code, 'no quote')
        return

    # 无法频繁获取数据
    if day_quote is not None:
        df = df.append(day_quote)

    ret = None
    if is_match(df, strategy_name, period):
        # print('{}'.format(code))
        ret = code

    # _conn.close()

    return ret


def select_one_strategy(code_list, strategy_name, period, options):
    """
    https://docs.python.org/3/library/multiprocessing.html
    This means that if you try joining that process you may get a deadlock
    unless you are sure that all items which have been put on the queue have been consumed.
    Similarly, if the child process is non-daemonic then the parent process may hang on exit
    when it tries to join all its non-daemonic children.

    Note that a queue created using a manager does not have this issue.
    """

    logger.info('[{}] to check [{}]...'.format(len(code_list), strategy_name))

    day_quote = None

    mp = options['selector_mp']
    use_rt_quote = options['selector_rt_quote']
    if use_rt_quote and dt.istradetime():
        cache_dir = util_util.get_cache_dir()
        cache = os.path.join(cache_dir, 'day_quote_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d')))
        has_cache = False
        if os.path.exists(cache):
            fname = pathlib.Path(cache)
            if (datetime.datetime.now() - datetime.datetime.fromtimestamp(fname.stat().st_mtime)).seconds > 5 * 60:
                os.remove(cache)
            else:
                has_cache = True

        if has_cache:
            day_quote = load(cache)
        else:
            day_quote = tx.get_today_all()
            dump(day_quote, cache)

        df_ = quote_db.get_price_info_df_db('000001', days=1, period_type='D')
        for column in day_quote.columns:
            if column not in df_.columns:
                day_quote = day_quote.drop([column], axis=1)

    select_func = functools.partial(_select, strategy_name, period)

    r = []
    if not mp:
        for code in code_list:
            if not select_func((code, None if day_quote is None else day_quote.loc[day_quote.code == code])):
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
        arg = [(code, None if day_quote is None else day_quote.loc[day_quote.code == code]) for code in code_list]
        for _ in tqdm.tqdm(p.imap_unordered(select_func, arg),
                           total=len(code_list), ncols=64):
            r.append(_)

        code_list = [code for code in r if code]

    logger.info('{}: {}'.format(strategy_name, len(code_list)))

    return code_list


def update_candidate_pool(strategy_list, period='day'):
    t1 = datetime.datetime.now()
    msg = ''
    options = config.get_config_options()
    for strategy in strategy_list:
        code_list = basic.get_all_stock_code()
        # code_list = ['600331']
        code_list = select_one_strategy(code_list, strategy, period, options)
        # 科创板
        # code_list = [code for code in code_list if not code.startswith('688')]
        msg += '{}: {}\n'.format(strategy, len(code_list))
        basic.upsert_candidate_pool(code_list, 'candidate', strategy, ignore_duplicate=False)

    t2 = datetime.datetime.now()
    cost = (t2 - t1).seconds
    qt_util.popup_info_message_box_mp('update candidate finished in [{}s]\n{}'.format(cost, msg))


def select(strategy_name_list, candidate_list=None, traced_list=None, period='day'):
    begin = datetime.datetime.now()

    code_list = []
    if candidate_list:
        if config.update_candidate_pool:
            update_candidate_pool(candidate_list)
        code_list = basic.get_candidate_stock_code(candidate_list)

    if traced_list:
        code_list.extend(basic.get_traced_stock_code(traced_list))

    if not code_list:
        code_list = basic.get_all_stock_code()
    # code_list = future.get_future_contract_list()
    # 科创板
    # code_list = [code for code in code_list if int(code[:2]) <= 60]
    # code_list = ['000408']

    options = config.get_config_options()
    strategy_name_list = config.get_scan_strategy_name_list() if not strategy_name_list else strategy_name_list
    for strategy_name in strategy_name_list:
        code_list = select_one_strategy(code_list, strategy_name, period, options)
        # for code in code_list:
        #     selected.add_selected(code, strategy_name)
        # code_list = ['002109']
        status = 'traced' if strategy_name in config.traced_strategy_list else 'allow_buy'
        basic.upsert_candidate_pool(code_list, status, strategy_name, ignore_duplicate=False)
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
