# -*- coding: utf-8 -*-
"""
https://matplotlib.org/stable/gallery/lines_bars_and_markers/marker_reference.html
http://www.cjzzc.com/web_color.html
"""

import datetime
import functools
import os
import sys

from config import config
from config.config import is_long_period, OscIndicator

from acquisition import tx, quote_db

import numpy

from indicator.atr import compute_atr

import mplfinance as mpf
import matplotlib as mpl  # 用于设置曲线参数
from cycler import cycler  # 用于定制线条颜色
import pandas
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.widgets import Cursor

from pointor import signal_dynamical_system, signal_channel, signal_market_deviation, signal_stop_loss, signal
from indicator import force_index, relative_price_strength, new_high_new_low, advance_decline, up_ema

import logging

from util import dt, util

# plt.rcParams['axes.unicode_minus'] = False  # 未解决 '负号(-)' 显示为小方框的问题
logging.getLogger("matplotlib").setLevel(logging.WARNING)

panel_ratios = {
    2: (7, 3),
    3: (8, 0.2, 1.8),
    4: [7.1, 0.1, 1.4, 1.4],
    # 5: [7.05, 0.075, 0.075, 1.4, 1.4]
    5: [6.9, 0.1, 1.0, 1.0, 1.0]
}

oscillatior = 'force_index'
# oscillatior = 'volume_ad'
oscillatior_list = ['macd', 'asi', 'force_index', 'volume_ad', 'skdj', 'rsi']
# oscillatior_list = ['force_index']
show_long_period_dynamical_system = False
show_signal_detail = False

g_dyn_sys_enabled = False
g_signal_enabled = False

alpha = 0.1

yellow = '#FFFF00'
orange = '#FFA500'
light_green = '#90EE90'
dark_olive_green3 = '#A2CD5A'
light_coral = '#F08080'
blue = '#0000FF'
light_blue = '#ADD8E6'
indian_red = '#CD5C5C'
indian_red1 = '#FF6A6A'
dark_sea_green = '#8FBC8F'
purple = '#A020F0'
red = 'r'
dark_red = '#8B0000'
green = 'g'
dark_green = '#006400'
sea_green = '#2E8B57'
medium_sea_green = '#3CB371'
light_sea_green = '#20B2AA'
lightgrey = 'lightgrey'
grey = 'grey'
dimgrey = 'dimgrey'
grey91 = '#E8E8E8'
black = 'black'
marker_up = '^'
marker_down = 'v'


def is_market_index(code):
    if code == 'maq' or len(code) > 6:
        return True
    return False


def import_csv(path):
    # 导入股票数据
    df = pandas.read_csv(path, encoding='gbk')
    # 格式化列名，用于之后的绘制
    df.rename(
        columns={
            '股票代码': 'code',
            '日期': 'date',
            '开盘价': 'open',
            '最高价': 'high',
            '最低价': 'low',
            '收盘价': 'close',
            '成交量': 'volume',
            '成交金额': 'amount'
        },
        inplace=True)
    # 转换为日期格式
    df['date'] = pandas.to_datetime(df['date'], format='%Y-%m-%d')
    # 将日期列作为行索引
    df.set_index(['date'], inplace=True)
    df.sort_index(ascending=True, inplace=True)

    return df


def tune_deviation(data_in):
    data = data_in.copy()
    x = numpy.where(~numpy.isnan(data))
    for i in range(0, len(x[0]), 2):
        data[x[0][i]] = numpy.nan
    return data


class DataFinanceDraw(object):
    """
    获取数据，并按照 mplfinanace 需求的格式格式化，然后绘图
    """

    def __init__(self, code, period):
        self.init_timestamp = datetime.datetime.now().timestamp()
        self.load_data_timestamp = 0
        self.compute_timestamp = 0
        self.plot_timestamp = 0
        self.add_line_timestamp = 0
        self.show_timestamp = 0

        self.code = code
        self.period = period
        self.count = 250

        self.show_volume = False
        self.show_macd = True
        self.panel_volume = 1 if self.show_volume else 0
        osc_len = 1  # len(oscillatior_list)
        self.n_panels = (3 if self.show_volume else 2) + osc_len
        if show_long_period_dynamical_system and not is_long_period(self.period):
            self.n_panels += 1
            self.panel_dyn_sys_long_period = self.panel_volume + 1
            self.panel_dyn_sys = self.panel_dyn_sys_long_period + 1
        else:
            self.panel_dyn_sys = self.panel_volume + 1
        if not g_dyn_sys_enabled:
            self.panel_dyn_sys -= 1
            self.n_panels -= 1
        self.panel_oscillation = self.panel_dyn_sys + 1
        self.panel_macd = self.panel_oscillation + osc_len

        self.data_long_period_origin = pandas.DataFrame()
        self.data_origin = pandas.DataFrame()
        self.data = None
        self.histogram_macd = None
        self.histogram_volume_ad = None
        self.histogram_force_index = None
        self.histogram_skdj = None
        self.histogram_rsi = None

        self.need_update = False
        self.style = None

        self.add_plot = []
        self.fig = None

        self.set_plot_style()

    def get_window(self, data):
        # if self.period == 'week':
        #     return data[-125:]
        return data[-self.count:]

        # if isinstance(data) 'pandas.core.series.Series' 'numpy.ndarray' 'pandas.core.frame.DataFrame'
        # return data[-250:]

    def set_plot_style(self):
        # 设置marketcolors
        # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
        # down:与up相反，这样设置与国内K线颜色标准相符
        # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
        # wick:灯芯(上下影线)颜色
        # volume:成交量直方图的颜色
        # inherit:是否继承，选填
        mc = mpf.make_marketcolors(
            up='white',  # 'dimgray',
            down=grey,
            edge=grey,
            wick=grey,
            volume='in',
            inherit=False)

        # 设置图形风格
        # gridaxis:设置网格线位置
        # gridstyle:设置网格线线型
        # y_on_right:设置y轴位置是否在右
        self.style = mpf.make_mpf_style(
            gridaxis='both',
            gridstyle='-.',
            y_on_right=False,
            marketcolors=mc,
            facecolor=grey91,
            figcolor=grey91
        )

        # 设置均线颜色，配色表可见下图
        # 建议设置较深的颜色且与红色、绿色形成对比
        # 此处设置七条均线的颜色，也可应用默认设置
        mpl.rcParams['axes.prop_cycle'] = cycler(
            color=['dodgerblue', 'deeppink',
                   'navy', 'teal', 'maroon', 'darkorange',
                   'indigo'])

        # 设置线宽
        mpl.rcParams['lines.linewidth'] = .5
        # mpl.rcParams['toolbar'] = 'None'
        # mpl.rcParams['interactive'] = True
        mpl.rcParams['axes.titlesize'] = 1
        # mpl.rcParams['axes.xmargin'] = 0
        # mpl.rcParams['axes.ymargin'] = 0

        # 显示中文
        # plt.rcParams['font.sans-serif'] = ['SimHei']
        # 显示负数
        plt.rcParams['axes.unicode_minus'] = False

        # TODO 中文显示方框
        # mpl.matplotlib_fname()
        # ~/workspace/stockopr/venv/lib/python3.7/site-packages/matplotlib/mpl-data/matplotlibrc
        # font.family:  sans-serif   # 本行去掉注释
        # font.sans-serif: SimHei,    # 本行去掉注释, 添加 SimHei 字体
        # cp /usr/share/fonts/truetype/msfonts/simsun.ttf mpl-data/fonts/ttf/
        mpl.rcParams['font.sans-serif'] = 'SimHei'

    def fetch_data(self, code):
        count = self.count
        if not is_long_period(self.period):
            count *= 5
        if is_market_index(self.code) or (self.period in ['week', 'day'] and not dt.istradetime()):
            period_type = config.period_map[self.period]['period']
            self.data_origin = quote_db.get_price_info_df_db(code, count, period_type=period_type)
        else:
            self.data_origin = tx.get_kline_data(code, self.period, count)

        # self.data_long_period_origin = tx.get_min_data(code, period, count)
        self.load_data_timestamp = datetime.datetime.now().timestamp()

    def load_data(self, file_name='2020.csv'):
        """
        获取数据, 把数据格式化成 mplfinance 的标准格式
        :return:
        """
        count = self.count
        if not is_long_period(self.period):
            count *= 5
        data = import_csv(file_name)
        data = data[data.close > 0]
        self.data_origin = data.iloc[-count:]
        self.load_data_timestamp = datetime.datetime.now().timestamp()

    def add_oscillation_deviation(self, osc, oscillation_bull_market_deviation, oscillation_bear_market_deviation, data_oscillation):
        data_oscillation_bull_deviation = oscillation_bull_market_deviation.mask(
            oscillation_bull_market_deviation.notnull().values,
            data_oscillation * 1.2).values

        data_oscillation_bear_deviation = oscillation_bear_market_deviation.mask(
            oscillation_bear_market_deviation.notnull().values,
            data_oscillation * 1.2).values

        # draw line
        # https://github.com/matplotlib/mplfinance/issues/42
        # https://github.com/matplotlib/mplfinance/issues/54
        # if self.get_window(data[bull_deviation_column]).any(skipna=True):
        #     self.add_plot.extend([mpf.make_addplot(self.get_window(data_oscillation), aline=[
        #         (oscillation_bull_market_deviation.index[0], oscillation_bull_market_deviation[0]),
        #     (oscillation_bull_market_deviation.index[1], oscillation_bull_market_deviation[1])],
        #                                            type='line', width=1, panel=0, color=green),
        #                           ])

        oscillation_bull_market_deviation_single_point = tune_deviation(oscillation_bull_market_deviation)
        oscillation_bear_market_deviation_single_point = tune_deviation(oscillation_bear_market_deviation)
        data_oscillation_bull_deviation_single_point = tune_deviation(data_oscillation_bull_deviation)
        data_oscillation_bear_deviation_single_point = tune_deviation(data_oscillation_bear_deviation)

        if self.get_window(oscillation_bull_market_deviation).any(skipna=True):
            self.add_plot.extend([mpf.make_addplot(self.get_window(oscillation_bull_market_deviation_single_point),
                                                   type='scatter', width=1, panel=0, color=green, markersize=50,
                                                   marker=marker_up),
                                  ])
        if self.get_window(oscillation_bear_market_deviation).any(skipna=True):
            self.add_plot.extend([mpf.make_addplot(self.get_window(oscillation_bear_market_deviation_single_point),
                                                   type='scatter', width=1, panel=0, color=red, markersize=50,
                                                   marker=marker_down), ])

    def add_oscillation(self, data, osc):
        signal_enabled = config.enabled_signal('{}_signal_exit'.format(osc), self.period)
        signal_deviation_enabled = config.enabled_signal('{}_bear_market_deviation_signal_exit'.format(osc), self.period)
        # macd
        if not signal_enabled and not signal_deviation_enabled and osc != oscillatior:
            return

        data_column = signal.get_osc_key(osc)
        data_oscillation = data[data_column]

        oscillation_color = [lightgrey if v >= 0 else grey for v in self.get_window(data[data_column])]

        force_index_abs_avg = data_oscillation.abs().mean()
        mask = (data_oscillation < force_index_abs_avg * 5) & (data_oscillation > force_index_abs_avg * -5)
        data_oscillation_bar = data_oscillation.mask(mask, numpy.nan)

        oscillation_color = [
            dark_olive_green3 if v >= force_index_abs_avg * 5 else light_coral if v <= -force_index_abs_avg * 5 else
            oscillation_color[i]
            for (i,), v in numpy.ndenumerate(self.get_window(data_oscillation).values)]

        # force_index_positive_avg = data_oscillation[data_oscillation > 0].mean()
        data_oscillation = data_oscillation.mask(data_oscillation > force_index_abs_avg * 5,
                                                 force_index_abs_avg * 3)
        data_oscillation = data_oscillation.mask(data_oscillation < -force_index_abs_avg * 5,
                                                 -force_index_abs_avg * 3)
        data_oscillation_bar = data_oscillation_bar.mask(data_oscillation_bar > force_index_abs_avg * 5,
                                                 force_index_abs_avg * 3)
        data_oscillation_bar = data_oscillation_bar.mask(data_oscillation_bar < -force_index_abs_avg * 5,
                                                     -force_index_abs_avg * 3)

        # eval 不能赋值
        # eval('self.histogram_{} = data_oscillation'.format(osc))
        exec('self.histogram_{} = data_oscillation'.format(osc))

        if signal_deviation_enabled:
            oscillation_bull_market_deviation = data['{}_bull_market_deviation'.format(osc)]
            oscillation_bear_market_deviation = data['{}_bear_market_deviation'.format(osc)]

            oscillation_color = [dark_olive_green3 if not numpy.isnan(v) else oscillation_color[i]
                                 for (i,), v in
                                 numpy.ndenumerate(self.get_window(oscillation_bull_market_deviation).values)]
            oscillation_color = [light_coral if not numpy.isnan(v) else oscillation_color[i]
                                 for (i,), v in
                                 numpy.ndenumerate(self.get_window(oscillation_bear_market_deviation).values)]

            self.add_oscillation_deviation(osc, oscillation_bull_market_deviation, oscillation_bear_market_deviation, data_oscillation)

        # 只显示一个振荡指标 panel
        if osc != oscillatior:
            return

        zero = data_oscillation.mask(data_oscillation.notnull(), 0)
        panel = self.panel_oscillation  # + oscillatior_list.index(osc)
        self.add_plot.append(mpf.make_addplot(self.get_window(zero), type='line', width=0.5, panel=panel,
                         color=grey, secondary_y=False, title=oscillatior))
        if osc == 'macd':
            self.add_macd(data, panel)
            return

        self.add_plot.extend([
            mpf.make_addplot(self.get_window(data_oscillation), type='line', width=0.7, panel=panel, color=dimgrey)])

        if self.get_window(data_oscillation_bar).any(skipna=True):
            self.add_plot.extend([
                mpf.make_addplot(self.get_window(data_oscillation_bar), type='bar', panel=panel,
                                 color=oscillation_color, secondary_y=False)])

        if osc == 'skdj':
            self.add_plot.append(mpf.make_addplot(
                self.get_window(data['d']), width=0.7, panel=panel, color=grey, linestyle='dashdot', secondary_y=False))

        d = {
            'rsi': (70, 30),
            'skdj': (80, 20)
        }

        if osc in d:
            for val in d[osc]:
                hline = data_oscillation.mask(data_oscillation.notnull(), val)
                self.add_plot.append(
                    mpf.make_addplot(self.get_window(hline), width=0.5, panel=panel, color=grey, secondary_y=False))

    def add_oscillations(self, data):
        for osc in oscillatior_list:
            self.add_oscillation(data, osc)

    def add_resistance_support(self, data):
        if not config.enabled_signal('resistance_support_signal_exit', self.period)\
                and not config.enabled_signal('resistance_support_signal_enter', self.period):
            return

        data_support = self.data[:]['low'].copy()
        data_resistance = self.data[:]['high'].copy()
        # data_resistance = data_resistance.mask(data_resistance > 0, data_resistance.max())
        data_resistance[:] = self.data[-60:]['high'].max()
        data_support[:] = self.data[-60:]['low'].min()

        width = 0.5
        color = dimgrey
        if 'support' in self.data.columns:
            # data_resistance_20 = data_resistance_20.mask(data_resistance_20.index < data_resistance_20.index[-60], numpy.nan)
            # data_resistance_20 = data_resistance_20.mask(data_resistance_20 > 0, data_resistance_20[-1])

            data_support_20 = self.data['support']
            # data_support_20 = data_support_20.mask(data_support_20.index < data_support_20.index[-60], numpy.nan)
            # data_support_20 = data_support_20.mask(data_support_20 > 0, data_support_20[-1])

            self.add_plot.append(
                mpf.make_addplot(self.get_window(data_support_20), type='line', width=width, color=color))

        if 'resistance' in self.data.columns:
            data_resistance_20 = self.data['resistance']

            self.add_plot.append(
                mpf.make_addplot(self.get_window(data_resistance_20), type='line', width=width, color=color))

        self.add_plot.extend([
            mpf.make_addplot(self.get_window(data_resistance), type='line', width=width + 0.3, color=grey),
            mpf.make_addplot(self.get_window(data_support), type='line', width=width + 0.3, color=grey),
        ])

    def add_rps(self, quote, market_index, panel):
        quote = relative_price_strength.relative_price_strength(quote, self.period, market_index)
        if market_index != 'maq':
            market_index = ''
        rps = 'rps' + market_index
        erps = 'erps' + market_index
        diff = quote[rps] - quote[erps]
        diff_zero = diff.copy()
        diff_zero[:] = 0

        width = 0.5
        self.add_plot.extend([
            # window
            # mpf.make_addplot(quote['rps3'], panel=1, type='line', width=width+0.2, color=dimgrey),
            # mpf.make_addplot(quote['rps10'], panel=1, type='line', width=width+0.2, color=grey),
            # mpf.make_addplot(quote['rps20'], panel=1, type='line', width=width+0.2, color=grey),
            # osc
            # mpf.make_addplot(quote['rps'], panel=1, type='line', width=width + 0.2, color=grey),
            # stock.close/market.close

            mpf.make_addplot(self.get_window(diff)
                             , panel=panel, type='bar', width=1, color=lightgrey, alpha=0.5),
            mpf.make_addplot(self.get_window(diff_zero), panel=panel, type='line', width=0.5, color=grey, secondary_y=False),

            mpf.make_addplot(self.get_window(quote[rps]), panel=panel, type='line', width=width, color=dimgrey),
            mpf.make_addplot(self.get_window(quote[erps]), panel=panel, type='line', width=width, color=grey, linestyle='dashdot'),
        ])

    def add_macd(self, data, panel):
        macd = data['macd_line']
        macd_signal = data['macd_signal']

        # 添加macd子图
        histogram = data['macd_histogram']
        self.histogram_macd = histogram

        # macd panel
        colors = [lightgrey if v >= 0 else grey for v in self.get_window(histogram)]

        if 'macd_bull_market_deviation' in data.columns:
            macd_bull_market_deviation = data['macd_bull_market_deviation']
            data_macd_bull_deviation = macd_bull_market_deviation.mask(macd_bull_market_deviation.notnull().values,
                                                                       histogram * 1.2).values

            macd_bear_market_deviation = data['macd_bear_market_deviation']
            data_macd_bear_deviation = macd_bear_market_deviation.mask(macd_bear_market_deviation.notnull().values,
                                                                       histogram * 1.2).values

            macd_bull_market_deviation_single_point = tune_deviation(macd_bull_market_deviation)
            macd_bear_market_deviation_single_point = tune_deviation(macd_bear_market_deviation)
            data_macd_bull_deviation_single_point = tune_deviation(data_macd_bull_deviation)
            data_macd_bear_deviation_single_point = tune_deviation(data_macd_bear_deviation)

            # if self.get_window(data['macd_bull_market_deviation']).any(skipna=True):
            #     self.add_plot.extend([mpf.make_addplot(self.get_window(macd_bull_market_deviation_single_point), type='scatter',
            #                                            width=1, panel=0, color=green, markersize=50, marker=marker_up), ])
            # if self.get_window(data['macd_bear_market_deviation']).any(skipna=True):
            #     self.add_plot.extend([mpf.make_addplot(self.get_window(macd_bear_market_deviation_single_point), type='scatter',
            #                                           width=1, panel=0, color=red, markersize=50, marker=marker_down), ])

            # 计算macd的数据。计算macd数据可以使用第三方模块talib（常用的金融指标kdj、macd、boll等等都有，这里不展开了），
            # 如果在金融数据分析和量化交易上深耕的朋友相信对这些指标的计算原理已经了如指掌，直接通过原始数据计算即可，以macd的计算为例如下：

            # histogram[histogram < 0] = None
            # histogram_positive = histogram
            # histogram = macd - signal
            # histogram[histogram >= 0] = None
            # histogram_negative = histogram

            colors = [dark_olive_green3 if not numpy.isnan(v) else colors[i]
                      for (i,), v in numpy.ndenumerate(self.get_window(macd_bull_market_deviation).values)]
            colors = [light_coral if not numpy.isnan(v) else colors[i]
                      for (i,), v in numpy.ndenumerate(self.get_window(macd_bear_market_deviation).values)]
        self.add_plot.extend(
            [
                # mpf.make_addplot(self.get_window(histogram_positive, type='bar', width=0.7, panel=2, color='b')),
                # mpf.make_addplot(self.get_window(histogram_negative, type='bar', width=0.7, panel=2, color='fuchsia')),
                mpf.make_addplot(self.get_window(macd), width=0.5, panel=panel, color=grey, secondary_y=False),
                mpf.make_addplot(self.get_window(macd_signal), width=0.5, panel=panel, color=grey, linestyle='dashdot', secondary_y=False),
                mpf.make_addplot(self.get_window(histogram), type='bar', panel=panel, color=colors),
                # ), secondary_y=True)
                # mpf.make_addplot(self.get_window(data_macd_bull_deviation_single_point), type='scatter', width=1, panel=self.panel_macd, color=dark_olive_green3, markersize=50, marker=marker_up, secondary_y=False),
                # mpf.make_addplot(self.get_window(data_macd_bear_deviation_single_point), type='scatter', width=1, panel=self.panel_macd, color=light_coral, markersize=50, marker=marker_down, secondary_y=False),
            ])

    def add_dynamical_system(self, data):
        dyn_sys = data["dyn_sys"]
        dyn_sys_long_period = data["dyn_sys_long_period"]

        dyn_sys_long_period_color = [dark_olive_green3 if v > 0 else light_coral if v < 0 else light_blue for v in
                                  self.get_window(dyn_sys_long_period)]
        dyn_sys_color = [dark_olive_green3 if v > 0 else light_coral if v < 0 else light_blue for v in
                      self.get_window(dyn_sys)]

        dyn_sys.values[:] = 1
        # dyn_sys_long_period.values[:] = self.data_origin['high'].max()   # data['low']
        dyn_sys_long_period.values[:] = data['low']
        # dyn_sys.values[:] = self.data_origin['low']

        if is_long_period(self.period):
            dyn_sys_long_period_color = dyn_sys_color

        self.add_plot.extend([
            mpf.make_addplot(self.get_window(dyn_sys_long_period), type='bar', width=1, panel=0,
                             color=dyn_sys_long_period_color,
                             alpha=alpha)])

        if show_long_period_dynamical_system:
            self.add_plot.extend([
                mpf.make_addplot(self.get_window(dyn_sys_long_period), type='bar', width=1, panel=0,
                                 color=dyn_sys_long_period_color,
                                 alpha=alpha)])

        self.add_plot.extend([
            mpf.make_addplot(self.get_window(dyn_sys), type='bar', width=1, panel=self.panel_dyn_sys, color=dyn_sys_color)
        ])

    def add_channel(self, data):
        if not config.enabled_signal('channel_signal_exit', self.period):
            return

        data_atr = data['atr']
        exp = data['close'].ewm(span=26, adjust=False).mean()

        width = 0.2
        color = grey
        self.add_plot.extend([
            mpf.make_addplot(self.get_window(data_atr + exp), type='line', width=width, panel=0, color=lightgrey,
                             linestyle='dotted'),
            mpf.make_addplot(self.get_window(data_atr * 2 + exp), type='line', width=width, panel=0, color=color,
                             linestyle='dashdot'),
            mpf.make_addplot(self.get_window(data_atr * 3 + exp), type='line', width=width, panel=0, color=color),

            mpf.make_addplot(self.get_window(-data_atr + exp), type='line', width=width, panel=0, color=lightgrey,
                             linestyle='dotted'),
            mpf.make_addplot(self.get_window(-data_atr * 2 + exp), type='line', width=width, panel=0, color=color,
                             linestyle='dashdot'),
            mpf.make_addplot(self.get_window(-data_atr * 3 + exp), type='line', width=width, panel=0, color=color),
        ])

    def add_stop_loss(self, data):
        if not config.enabled_signal('stop_loss_signal_exit', self.period):
            return

        data_stop_loss = self.data[:]['stop_loss'].copy()
        data_stop_loss_signal_exit = self.data[:]['stop_loss_signal_exit'].copy()
        if self.get_window(data_stop_loss).any(skipna=True):
            self.add_plot.append(mpf.make_addplot(self.get_window(data_stop_loss), type='line', width=0.5, color=light_coral))
        if self.get_window(data['stop_loss_signal_exit']).any(skipna=True):
            self.add_plot.append(
                mpf.make_addplot(self.get_window(data_stop_loss_signal_exit), type='scatter', width=1, color=purple,
                                 markersize=50, marker=marker_down))

    def add_a_signal(self, data, s, color, up):
        if self.get_window(data[s]).any(skipna=True):
            self.add_plot.append(
                mpf.make_addplot(self.get_window(data[s]), type='scatter', width=1,
                                 panel=0, color=color, markersize=50, marker=up))

    def add_signal(self, data):
        if show_signal_detail:
            signal_list = config.get_signal_enter_list(self.period)
            for s in signal_list:
                self.add_a_signal(data, s, dark_olive_green3, marker_up)

            signal_list = config.get_signal_exit_list(self.period)
            for s in signal_list:
                self.add_a_signal(data, s, light_coral, marker_down)

            return

        self.add_a_signal(data, 'signal_enter', dark_olive_green3, marker_up)
        self.add_a_signal(data, 'signal_exit', light_coral, marker_down)

    def add_market(self):
        if self.period not in ['day']:  # ['week', 'day']:
            return
        period_type = config.period_map[self.period]['period']
        market = quote_db.get_price_info_df_db('maq', days=self.count, period_type=period_type)
        self.add_plot.append(mpf.make_addplot(
            self.get_window(market['close']), panel=0, type='line', width=0.5, color=light_blue, secondary_y=True))

    def add_market_indicator(self, quote):
        period = self.period
        # quote = quote_db.get_price_info_df_db('maq', days=250, period_type=config.period_map[period]['period'])
        market = new_high_new_low.new_high_new_low(quote, period)

        width = 0.5
        panel = self.panel_oscillation
        if oscillatior == 'nhnl':
            nh_y = 100 * market['new_high_y'] / market['count']
            nl_y = -100 * market['new_low_y'] / market['count']
            hl = nh_y + nl_y
            hl_zero = hl.copy()
            hl_zero.loc[:] = 0
            self.add_plot.extend([
                mpf.make_addplot(self.get_window(nh_y), panel=panel, type='line', linestyle='dashdot', width=width, color=grey, title='NL',
                                 y_on_right=True),
                mpf.make_addplot(self.get_window(nl_y), panel=panel, type='line', linestyle='dashdot', width=width, color=grey,
                                 secondary_y=False),
                mpf.make_addplot(self.get_window(hl), panel=panel, type='line', width=width, color=dimgrey, secondary_y=False),
                mpf.make_addplot(self.get_window(hl_zero), panel=panel, type='line', width=width, color=grey, secondary_y=False),
            ])
        elif oscillatior == 'adl':
            ad = advance_decline.advance_decline(quote)
            self.add_plot.extend([
                mpf.make_addplot(self.get_window(ad), panel=panel, type='line', width=width, color=dimgrey, title='A/D', y_on_right=True),
                # mpf.make_addplot(ad_zero, panel=3, type='line', width=width, color=dimgrey, secondary_y=False),
            ])
        elif oscillatior == 'ema_over':
            up_ema52 = up_ema.up_ema(quote, period)
            up_ema_h = up_ema52.copy()
            up_ema_h.loc[:] = 75
            up_ema_l = up_ema52.copy()
            up_ema_l.loc[:] = 25
            self.add_plot.extend([
                mpf.make_addplot(self.get_window(up_ema52), panel=panel, type='line', width=width, color=dimgrey, ylabel='EMA_OVER'),
                mpf.make_addplot(self.get_window(up_ema_h), panel=panel, type='line', width=width, color=dimgrey, secondary_y=False),
                mpf.make_addplot(self.get_window(up_ema_l), panel=panel, type='line', width=width, color=dimgrey, secondary_y=False),
            ])

    def more_panel_draw(self):
        data = None
        data = self.data_origin  # .iloc[-100:]

        # IndianRed #CD5C5C   DarkSeaGreen #8FBC8F

        exp13 = data['close'].ewm(span=13, adjust=False).mean()
        # 以交易为生中，采用的是 exp21
        # exp = data['close'].ewm(span=21, adjust=False).mean()
        exp26 = data['close'].ewm(span=26, adjust=False).mean()
        exp = exp26

        #
        self.data = data

        if g_dyn_sys_enabled:
            self.add_dynamical_system(data)

        width = 0.5
        color = dimgrey
        self.add_plot.extend([
            mpf.make_addplot(self.get_window(exp13), type='line', width=width + 0.2, color=dimgrey),
            mpf.make_addplot(self.get_window(exp26), type='line', width=width + 0.1, color=black),
        ])

        if 'min_period' in data.columns:
            self.add_plot.extend([
                mpf.make_addplot(self.get_window(data.min_period), type='scatter', marker='_', width=1, color=green),
                mpf.make_addplot(self.get_window(data.max_period), type='scatter', marker='_', width=1, color=red)
            ])

        if g_signal_enabled:
            if is_market_index(self.code):
                self.add_market_indicator(data)
            else:
                self.add_signal(data)

            self.add_resistance_support(data)
            self.add_channel(data)
            self.add_stop_loss(data)
            self.add_market()

            if oscillatior == 'rps':
                self.add_rps(data, market_index='co', panel=self.panel_oscillation)
            else:
                self.add_oscillations(data)

            self.n_panels += 1
            if self.period.startswith('m'):
                self.add_macd(data, self.panel_macd)
            else:
                self.add_rps(data, market_index='maq', panel=self.panel_macd)

        from indicator import trend_strength
        data = trend_strength.compute_trend_strength(self.data_origin, self.period)
        strength = self.get_window(data['trend_strength'])
        color = pandas.Series(lightgrey, index=strength.index)
        color = color.mask(data['trend_strength'] > 50, dark_sea_green)
        color = color.mask(data['trend_strength'] < -50, light_coral)
        color = color.mask(data['trend_strength'] > 80, dark_green)
        color = color.mask(data['trend_strength'] < -80, purple)
        self.add_plot.append(mpf.make_addplot(
            strength, panel=1, type='bar', width=0.7, color=color.to_list()))  # marker='.',
        # data = data.iloc[-100:]

        self.compute_timestamp = datetime.datetime.now().timestamp()

    def draw_arrow(self, axlist, yminor_unit):
        if not g_signal_enabled:
            return
        if is_market_index(self.code):
            return

        # 带箭头的线
        len_osc = len(oscillatior_list)

        # 只显示一个振荡指示 panel
        len_osc = 1

        # map_index = {
        #     'macd_bull_market_deviation': {'data': self.histogram_macd,
        #                                    'ax': axlist[4 + 2 * len_osc] if not show_long_period_dynamical_system or is_long_period(self.period) else axlist[6 + 2 * len_osc]},
        #     'macd_bear_market_deviation': {'data': self.histogram_macd,
        #                                    'ax': axlist[4 + 2 * len_osc] if not show_long_period_dynamical_system or is_long_period(self.period) else axlist[6 + 2 * len_osc]},
        # }
        map_index = {}
        for i, osc in enumerate(oscillatior_list):
            # 只显示一个振荡指示 panel
            if osc != oscillatior:
                continue
            i = 0
            map_index.update({
                '{}_bull_market_deviation'.format(osc): {'data': eval('self.histogram_{}'.format(osc)),
                                                         'ax': axlist[
                                                             4 + i * 2] if not show_long_period_dynamical_system or is_long_period(
                                                             self.period) else axlist[6 + i * 2]}
            })
            map_index.update({'{}_bear_market_deviation'.format(osc): {'data': eval('self.histogram_{}'.format(osc)),
                                                                       'ax': axlist[
                                                                           4 + i * 2] if not show_long_period_dynamical_system or is_long_period(
                                                                           self.period) else axlist[6 + i * 2]}})
            # 只显示一个振荡指示 panel
            break

        def draw_deviation_line(data, ax, ax2, data1, data2, unit1, unit2, color, will, draw_minor):
            """
            width: float, default: 0.001
            Width of full arrow tail.

            length_includes_head: bool, default: False
            True if head is to be counted in calculating the length.

            head_width: float or None, default: 3*width
            Total width of the full arrow head.

            head_length: float or None, default: 1.5*head_width
            Length of arrow head.
            """
            points = data1[data1.notnull()]
            if not points.any(skipna=True):
                return
            mask = data1.notnull()

            if len(points) % 2 == 1:
                points = points.iloc[1:]

            # points2 = data2[data2.notnull()]
            if draw_minor:
                points2 = data2[mask]
                points2 = points2[points2.notnull()]
                if len(points2) % 2 == 1:
                    points2 = points2.iloc[1:]
            else:
                points2 = None

            value = data.min() if will == 1 else data.max()
            shape = 'left' if will == 1 else 'right'  # full
            for index in range(0, len(points), 2):
                index_first = numpy.where(data1.index == points.index[index])[0][0]
                index_second = numpy.where(data1.index == points.index[index + 1])[0][0]

                width = unit1 / 10
                ax.arrow(index_first, points.values[index], index_second - index_first,
                         (points.values[index + 1] - points.values[index]), shape=shape, color=color,
                         length_includes_head=True, width=width, head_width=0, head_length=0)

                ax.arrow(index_second, points.values[index + 1], 0,
                         (value - points.values[index + 1]), shape=shape, linestyle='-', color=color,
                         length_includes_head=True, width=width, head_width=0, head_length=0)

                if not draw_minor:
                    continue

                width = unit2 / 10
                ax2.arrow(index_first, points2.values[index], index_second - index_first,
                          (points2.values[index + 1] - points2.values[index]), shape=shape, color=color, )
                # length_includes_head=True, width=width, head_width=0, head_length=0)

        ax = axlist[0] if is_long_period(self.period) else axlist[0]
        deviation_list = [
            'macd_bull_market_deviation', 'macd_bear_market_deviation',
            # '{}_bull_market_deviation'.format(oscillatior), '{}_bear_market_deviation'.format(oscillatior)
        ]
        deviation_list.extend(['{}_bull_market_deviation'.format(osc) for osc in oscillatior_list])
        deviation_list.extend(['{}_bear_market_deviation'.format(osc) for osc in oscillatior_list])

        # deviation_list = ['force_index_bull_market_deviation']
        for column_name in deviation_list:
            tail = 'signal_enter' if 'bull' in column_name else 'signal_exit'
            signal_name = '{}_{}'.format(column_name, tail)
            if not g_signal_enabled or not config.enabled_signal(signal_name, self.period):
                continue
            data = self.get_window(self.data[column_name])

            unit1 = yminor_unit * 0.01
            # unit1 = 0

            # draw_minor = 'macd' in column_name or oscillatior in column_name
            draw_minor = oscillatior in column_name
            data2 = self.get_window(map_index[column_name]['data']) if draw_minor else None
            ax2 = map_index[column_name]['ax'] if draw_minor else -1
            # high = self.get_window(data2).max()
            # low = self.get_window(data2).min()
            # yminor_unit2 = round((high - low) / 10, 2)
            # yminor_unit2 = max(yminor_unit2, 0.01)
            #
            # unit2 = yminor_unit2 * 0.1
            unit2 = 0

            # print(unit1, unit2)

            if 'bull' in column_name:
                will = 1
                color = dark_green  # if 'macd' in column_name else dark_green
            else:
                will = -1
                color = red  # if 'macd' in column_name else dark_red

            draw_deviation_line(self.data['close'], ax, ax2, data, data2, unit1, unit2, color,
                                will, draw_minor)

    def show(self):
        # 设置基本参数
        # type:绘制图形的类型, 有candle, renko, ohlc, line等
        # 此处选择candle,即K线图
        # mav(moving average):均线类型,此处设置7,30,60日线
        # volume:布尔类型，设置是否显示成交量，默认False
        # title:设置标题
        # y_label:设置纵轴主标题
        # y_label_lower:设置成交量图一栏的标题
        # figratio:设置图形纵横比
        # figscale:设置图形尺寸(数值越大图像质量越高)

        quote_type = 'line' if is_market_index(self.code) else 'candle'
        self.kwargs = dict(
            type=quote_type,  # 'ohlc',
            # mav=13, #(7, 30, 60),
            volume=self.show_volume,
            title='{} {}'.format(self.code, self.period),
            # ylabel='OHLC Candles',
            # ylabel_lower='Shares\nTraded Volume',
            # axisoff=True,
            tight_layout=True,
            scale_padding=0.3,
            xrotation=0,
            # figratio=(20, 9),
            # figscale=2,
            # figsize=(1920, 1080)
        )

        self.fig, axlist = mpf.plot(self.get_window(self.data), **self.kwargs,
                                    style=self.style,
                                    show_nontrading=False,
                                    addplot=self.add_plot,
                                    main_panel=0,
                                    volume_panel=self.panel_volume,
                                    returnfig=True,
                                    panel_ratios=panel_ratios[self.n_panels]
                                    )

        self.plot_timestamp = datetime.datetime.now().timestamp()

        # import matplotlib.dates as mdates
        # xmajorLocator = mdates.DayLocator(1)
        # xmajorFormatter = mdates.DateFormatter('%Y-%m-%d')
        # xminorLocator = mdates.DayLocator()
        # axlist[7].xaxis.set_major_locator(xmajorLocator)
        # axlist[7].xaxis.set_major_formatter(xmajorFormatter)

        standard_unit = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500]
        high = self.get_window(self.data)['high'].max()
        low = self.get_window(self.data)['low'].min()
        yminor_unit_origin = round((high - low) / 12, 2)
        yminor_unit_origin = max(yminor_unit_origin, 0.01)

        yminor_unit = functools.reduce(min, map(lambda x: abs(x - yminor_unit_origin),
                                                filter(lambda x: x > (yminor_unit_origin - yminor_unit_origin / 4),
                                                       standard_unit)))
        yminor_unit = yminor_unit_origin + yminor_unit if yminor_unit_origin + yminor_unit in standard_unit else yminor_unit_origin - yminor_unit

        # 修改主刻度
        # xmajorLocator = MultipleLocator(10)  # 将x主刻度标签设置为20的倍数
        # xmajorFormatter = FormatStrFormatter('%5.1f')  # 设置x轴标签文本的格式
        ymajorLocator = MultipleLocator(yminor_unit * 5)  # 将y轴主刻度标签设置为0.5的倍数
        ymajorFormatter = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
        # 设置主刻度标签的位置,标签文本的格式
        ax = axlist[0]
        # ax.xaxis.set_major_locator(xmajorLocator)
        # ax.xaxis.set_major_formatter(xmajorFormatter)
        ax.yaxis.set_major_locator(ymajorLocator)
        ax.yaxis.set_major_formatter(ymajorFormatter)

        # 修改次刻度
        # xminorLocator = MultipleLocator(5)  # 将x轴次刻度标签设置为5的倍数
        yminorLocator = MultipleLocator(yminor_unit)  # 将此y轴次刻度标签设置为0.1的倍数
        # 设置次刻度标签的位置,没有标签文本格式
        # ax.xaxis.set_minor_locator(xminorLocator)
        ax.yaxis.set_minor_locator(yminorLocator)

        # 打开网格
        ax.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
        ax.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度

        # cursor = Cursor(self.fig, useblit=True, color='red', linewidth=2)
        cursor = Cursor(axlist[1], useblit=True, color=grey, linewidth=1)
        # axlist[0].yaxis.set_label_position("right")
        # axlist[0].yaxis.tick_right()
        axlist[0].tick_params(axis='y', which='both', labelleft=False, labelright=True)
        axlist[1].tick_params(axis='y', which='both', labelleft=True, labelright=False)

        # self.fig.tight_layout()
        # print(len(axlist))   # 8

        ylim_min = self.get_window(self.data)['low'].min()
        ylim_max = self.get_window(self.data)['high'].max()
        diff = (ylim_max - ylim_min) * 0.1
        axlist[0].set_ylim(ymin=ylim_min - diff, ymax=ylim_max + diff)
        # # 没有效果
        # plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        # plt.margins(0, 0)

        # https://stackoverflow.com/questions/14908576/how-to-remove-frame-from-matplotlib-pyplot-figure-vs-matplotlib-figure-frame
        # ax.patch.set_visible(False)
        # ax.get_xaxis().set_ticks([])

        # axlist[3].fill_between(self.data.index, self.data['force_index'])

        self.draw_arrow(axlist, yminor_unit)

        # l = matplotlib.lines.Line2D([points.index[0], points.index[1]], [points.values[1], points.values[0]], color=red, marker=marker_up)
        # axlist[0].add_line(l)

        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()

        self.add_line_timestamp = datetime.datetime.now().timestamp()

        plt.show()
        # plt.show(block=False)  # 显示
        # plt.close()  # 关闭plt，释放内存

        self.show_timestamp = datetime.datetime.now().timestamp()


def update(candle):
    # if candle.fig:
    #     plt.close(candle.fig)
    candle.more_panel_draw()
    candle.need_update = True


def show(candle):
    candle.show()


def open_graph_no_signal(code, period):
    candle = DataFinanceDraw(code, period)
    candle.data_origin = signal.compute_signal(code, period, candle.data_origin)

    update(candle)
    show(candle)


def open_graph(code, peroid, indicator, path=None):
    global oscillatior
    if indicator:
        indicator = 'volume_ad' if indicator == 'adosc' else indicator
        oscillatior = indicator

    print('indicator: {}, oscillatior: {}'.format(indicator, oscillatior))
    candle = DataFinanceDraw(code, peroid)

    file = signal.get_cache_file(code, peroid)
    if file:
        candle.data_origin = signal.load(file)
    else:
        if path:
            candle.load_data(path)
        else:
            candle.fetch_data(code)
    # candle.data_origin = signal.compute_signal(code, peroid, candle.data_origin)

    update(candle)
    show(candle)

    info = [
        'init',
        'load',
        'compute',
        'plot',
        'addline',
        'show']
    timestamp = [
        candle.init_timestamp,
        candle.load_data_timestamp,
        candle.compute_timestamp,
        candle.plot_timestamp,
        candle.add_line_timestamp,
        candle.show_timestamp]

    print('='*10)
    for i, t in enumerate(timestamp):
        print('{}\t[{}]\t[{}]'.format(info[i], round(timestamp[-2] - t, 2), round(t - timestamp[max(0, i-1)], 2)))
    print('=' * 10)
    exit(0)


def show_indicator(code, period, indicator):
    quote = quote_db.get_price_info_df_db(code, days=250, period_type=config.period_map[period]['period'])
    quote = indicator(quote, period)
    market = quote_db.get_price_info_df_db('maq', days=250, period_type=config.period_map[period]['period'])
    diff = quote['rps'] - quote['erps']
    diff_zero = diff.copy()
    diff_zero[:] = 0

    add_plot = []
    width = 0.5
    add_plot.extend([
        # window
        # mpf.make_addplot(quote['rps3'], panel=1, type='line', width=width+0.2, color=dimgrey),
        # mpf.make_addplot(quote['rps10'], panel=1, type='line', width=width+0.2, color=grey),
        # mpf.make_addplot(quote['rps20'], panel=1, type='line', width=width+0.2, color=grey),
        # osc
        # mpf.make_addplot(quote['rps'], panel=1, type='line', width=width + 0.2, color=grey),
        # stock.close/market.close

        mpf.make_addplot(diff, panel=1, type='bar', width=1, color=lightgrey, alpha=0.5),
        mpf.make_addplot(diff_zero, panel=1, type='line', width=0.5, color=grey, secondary_y=False),

        mpf.make_addplot(quote['rps'], panel=1, type='line', width=width, color=dimgrey),
        mpf.make_addplot(quote['erps'], panel=1, type='line', width=width, color=grey, linestyle='dashdot'),

        mpf.make_addplot(market['close'], panel=0, type='line', width=width, color=grey, secondary_y=True),
    ])
    mpf.plot(quote[-250:], type="candle", addplot=add_plot)


if __name__ == "__main__":
    code, period, index = (sys.argv[1], sys.argv[2], sys.argv[3]) if len(sys.argv) == 4 else ('300502', 'day', 'rps')
    open_graph(code, period, index)
    # open_graph(code, period, OscIndicator.FORCE_INDEX.value, 'data/csv/' + code + '.csv')
    open_graph(code, period, 'rps')
