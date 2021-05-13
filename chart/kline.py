# -*- coding: utf-8 -*-
import functools
import threading
import time

import sys; sys.path.append(".")

from acquisition import tx

import numpy

from indicator.atr import compute_atr

import mplfinance as mpf
import matplotlib as mpl  # 用于设置曲线参数
from cycler import cycler  # 用于定制线条颜色
import pandas
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, Locator
from matplotlib.widgets import Cursor

from pointor import signal_triple_screen, signal_channel, signal_bull_market_deviation
from selector.plugin import dynamical_system, force_index

# http://www.cjzzc.com/web_color.html

panel_ratios = {
    3: (8, 0.2, 1.8),
    4: [7, 0.2, 1.4, 1.4],
    5: [7, 0.1, 0.1, 1.4, 1.4]
}


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
            '成交金额': 'turnover'
        },
        inplace=True)
    # 转换为日期格式
    df['date'] = pandas.to_datetime(df['date'], format='%Y-%m-%d')
    # 将日期列作为行索引
    df.set_index(['date'], inplace=True)
    df.sort_index(ascending=True, inplace=True)

    return df


class DataFinanceDraw(object):
    """
    获取数据，并按照 mplfinanace 需求的格式格式化，然后绘图
    """

    def __init__(self, code):
        self.show_volume = False
        self.show_macd = True
        self.panel_volume = 1 if self.show_volume else 0
        self.n_panels = 5 if self.show_volume else 4
        self.panel_dlxt_long_period = self.panel_volume + 1
        self.panel_dlxt = self.panel_dlxt_long_period + 1
        self.panel_qlzs = self.panel_dlxt + 1
        self.panel_macd = self.panel_qlzs + 1

        self.data_long_period_origin = pandas.DataFrame()
        self.data_origin = pandas.DataFrame()
        self.data = None
        self.need_update = False
        self.style = None
        self.code = code
        self.period = 'day'

        self.add_plot = []
        self.fig = None

        self.set_plot_style()

    def set_plot_style(self):
        # 设置marketcolors
        # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
        # down:与up相反，这样设置与国内K线颜色标准相符
        # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
        # wick:灯芯(上下影线)颜色
        # volume:成交量直方图的颜色
        # inherit:是否继承，选填
        mc = mpf.make_marketcolors(
            up='white', #'dimgray',
            down='grey',
            edge='grey',
            wick='grey',
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
            marketcolors=mc)

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

    def fetch_data(self, code, period, count=250):
        self.period = period
        self.data_origin = tx.get_kline_data(code, period, count)
        # self.data_long_period_origin = tx.get_min_data(code, period, count)

    def load_data(self, file_name='2020.csv', count=250):
        """
        获取数据, 把数据格式化成 mplfinance 的标准格式
        :return:
        """
        data = import_csv(file_name)
        self.data_origin = data.iloc[-count:]

    def more_panel_draw(self):
        data = self.data_origin   # .iloc[-100:]
        """
        make_addplot 绘制多个图，这里添加macd指标为例
        """
        exp12 = data['close'].ewm(span=12, adjust=False).mean()
        exp26 = data['close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        # 添加macd子图
        histogram = macd - signal

        # data = dynamical_system.dynamical_system(data)
        # triple_screen signal
        data = signal_triple_screen.signal_enter(data, period=self.period)
        data = signal_triple_screen.signal_exit(data, period=self.period)

        data = signal_channel.signal_enter(data, period=self.period)
        data = signal_channel.signal_exit(data, period=self.period)

        dlxt = data["dlxt"]
        dlxt_long_period = data["dlxt_long_period"]

        # LightGreen #90EE90   DarkOliveGreen3 #A2CD5A   LightCoral #F08080   IndianRed1 #FF6A6A   LightBlue #ADD8E6
        dark_olive_green3 = '#A2CD5A'
        light_coral = '#F08080'
        light_blue = '#ADD8E6'
        indian_red = '#CD5C5C'
        dark_sea_green = '#8FBC8F'

        data = force_index.force_index(data)
        data_force_index = data['force_index']
        force_index_abs_avg = data_force_index.abs().mean()
        # force_index_positive_avg = data_force_index[data_force_index > 0].mean()

        data_force_index = data_force_index.mask(data_force_index > force_index_abs_avg * 5, force_index_abs_avg * 5)
        data_force_index = data_force_index.mask(data_force_index < -force_index_abs_avg * 5, -force_index_abs_avg * 5)

        # A value is trying to be set on a copy of a slice from a DataFrame
        # mask1 = data_force_index.loc[data_force_index > force_index_abs_avg * 5] = force_index_abs_avg * 5
        # mask1 = data_force_index.loc[:] > force_index_abs_avg * 5
        # data_force_index[mask1] = force_index_abs_avg * 5
        # mask2 = data_force_index.loc[:] < -force_index_abs_avg * 5
        # data_force_index[mask2] = -force_index_abs_avg * 5

        data = signal_bull_market_deviation.signal_enter(data, self.period)

        # IndianRed #CD5C5C   DarkSeaGreen #8FBC8F

        # 以交易为生中，采用的是 exp21
        # exp = data['close'].ewm(span=21, adjust=False).mean()
        exp = exp26
        data = compute_atr(data)

        #
        self.data = data

        # data = data.iloc[-100:]

        dlxt_long_period_color = [dark_olive_green3 if v > 0 else light_coral if v < 0 else light_blue for v in
                                  dlxt_long_period]
        dlxt_color = [dark_olive_green3 if v > 0 else light_coral if v < 0 else light_blue for v in dlxt]

        force_index_color = ['lightgrey' if v >= 0 else 'grey' for v in data["force_index"]]
        force_index_color = [
            dark_olive_green3 if v == force_index_abs_avg * 5 else light_coral if v == -force_index_abs_avg * 5 else force_index_color[i]
            for (i,), v in numpy.ndenumerate(data_force_index.values)]

        data_atr = data['atr']
        self.add_plot.extend([
            mpf.make_addplot(data_atr + exp, type='line', width=1, panel=0, color='lightgrey', linestyle='dotted'),
            mpf.make_addplot(data_atr * 2 + exp, type='line', width=1, panel=0, color='grey', linestyle='dashdot'),
            mpf.make_addplot(data_atr * 3 + exp, type='line', width=1, panel=0, color='dimgrey'),
            mpf.make_addplot(-data_atr + exp, type='line', width=1, panel=0, color='lightgrey', linestyle='dotted'),
            mpf.make_addplot(-data_atr * 2 + exp, type='line', width=1, panel=0, color='grey', linestyle='dashdot'),
            mpf.make_addplot(-data_atr * 3 + exp, type='line', width=1, panel=0, color='dimgrey'),
        ])

        data_support = self.data[:]['low'].copy()
        data_stress = self.data[:]['high'].copy()
        # data_stress = data_stress.mask(data_stress > 0, data_stress.max())
        data_stress[:] = self.data[-60:]['high'].max()
        data_support[:] = self.data[-60:]['low'].min()

        dlxt.values[:] = 1
        # dlxt_long_period.values[:] = self.data_origin['high'].max()   # data['low']
        dlxt_long_period.values[:] = self.data_origin['low']
        self.add_plot.extend([
            mpf.make_addplot(data_stress, type='line', color='r'),
            mpf.make_addplot(data_support, type='line', color='g'),
            mpf.make_addplot(exp12, type='line', color='dimgrey'),
            mpf.make_addplot(exp26, type='line', color='black'),
            mpf.make_addplot(data_force_index, type='bar', panel=self.panel_qlzs, color=force_index_color),
            mpf.make_addplot(data_force_index, type='line', width=1, panel=self.panel_qlzs, color='dimgrey'),
            mpf.make_addplot(dlxt, type='bar', width=1, panel=self.panel_dlxt_long_period, color=dlxt_long_period_color),
            mpf.make_addplot(dlxt, type='bar', width=1, panel=self.panel_dlxt, color=dlxt_color),
            mpf.make_addplot(dlxt_long_period, type='bar', width=1, panel=0, color=dlxt_long_period_color, alpha=0.1),
        ])

        if data['channel_signal_enter'].any(skipna=True):
            self.add_plot.append(
                mpf.make_addplot(data['channel_signal_enter'], type='scatter', width=1, panel=0, color='lightgrey',
                                 markersize=50, marker='^'))
        if data['channel_signal_exit'].any(skipna=True):
            self.add_plot.append(
                mpf.make_addplot(data['channel_signal_exit'], type='scatter', width=1, panel=0, color='dimgrey',
                                 markersize=50, marker='v'))

        if data['triple_screen_signal_enter'].any(skipna=True):
            self.add_plot.append(
                mpf.make_addplot(data['triple_screen_signal_enter'], type='scatter', width=1, panel=0, color='g',
                                 markersize=50, marker='^'))
        if data['triple_screen_signal_exit'].any(skipna=True):
            self.add_plot.append(
                mpf.make_addplot(data['triple_screen_signal_exit'], type='scatter', width=1, panel=0, color='r',
                                 markersize=50, marker='v'))
        if data['macd_bull_market_deviation'].any(skipna=True):
            self.add_plot.extend([
                mpf.make_addplot(data['macd_bull_market_deviation'], type='scatter', width=1, panel=0, color='g',
                                 markersize=50, marker='D'),

            ])
        if self.show_macd:
            self.n_panels += 1
            # 计算macd的数据。计算macd数据可以使用第三方模块talib（常用的金融指标kdj、macd、boll等等都有，这里不展开了），
            # 如果在金融数据分析和量化交易上深耕的朋友相信对这些指标的计算原理已经了如指掌，直接通过原始数据计算即可，以macd的计算为例如下：

            # histogram[histogram < 0] = None
            # histogram_positive = histogram
            # histogram = macd - signal
            # histogram[histogram >= 0] = None
            # histogram_negative = histogram

            macd_bull_market_deviation = data['macd_bull_market_deviation']
            d = macd_bull_market_deviation.mask(macd_bull_market_deviation.notnull().values, histogram*1.2).values

            # macd panel
            colors = ['lightgrey' if v >= 0 else 'grey' for v in histogram]
            colors = [dark_olive_green3 if not numpy.isnan(v) else colors[i]
                      for (i,), v in numpy.ndenumerate(macd_bull_market_deviation.values)]
            self.add_plot.extend(
                [
                    # mpf.make_addplot(histogram_positive, type='bar', width=0.7, panel=2, color='b'),
                    # mpf.make_addplot(histogram_negative, type='bar', width=0.7, panel=2, color='fuchsia'),
                    # mpf.make_addplot(macd, panel=self.panel_macd, color='lightgrey'),
                    # mpf.make_addplot(signal, panel=self.panel_macd, color='dimgrey'),
                    mpf.make_addplot(histogram, type='bar', panel=self.panel_macd, color=colors),  # , secondary_y=True)
                    mpf.make_addplot(d, type='scatter', width=1, panel=self.panel_macd, color='g',
                                     markersize=50, marker='^', secondary_y=False),
                ])

        # fig = mpf.figure(figsize=(10, 7), style=self.style)  # pass in the self defined style to the whole canvas
        # ax = fig.add_subplot(2, 1, 1)  # main candle stick chart subplot, you can also pass in the self defined style here only for this subplot
        # av = fig.add_subplot(2, 1, 2, sharex=ax)  # volume chart subplot
        # mpf.plot(self.data, type='candle', ax=ax, volume=av)

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
        self.kwargs = dict(
            type='candle',  # 'ohlc',
            # mav=13, #(7, 30, 60),
            volume=self.show_volume,
            title='{} {}'.format(self.code, self.period),
            # ylabel='OHLC Candles',
            # ylabel_lower='Shares\nTraded Volume',
            # axisoff=True,
            figratio=(2, 1),
            figscale=1)

        self.fig, axlist = mpf.plot(self.data, **self.kwargs,
                                    style=self.style,
                                    show_nontrading=False,
                                    addplot=self.add_plot,
                                    main_panel=0,
                                    volume_panel=self.panel_volume,
                                    returnfig=True,
                                    #panel_ratios=(8, 0.2, 1.8),
                                    panel_ratios=panel_ratios[self.n_panels]
                                    )

        # import matplotlib.dates as mdates
        # xmajorLocator = mdates.DayLocator(1)
        # xmajorFormatter = mdates.DateFormatter('%Y-%m-%d')
        # xminorLocator = mdates.DayLocator()
        # axlist[7].xaxis.set_major_locator(xmajorLocator)
        # axlist[7].xaxis.set_major_formatter(xmajorFormatter)

        standard_unit = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500]
        high = self.data['high'].max()
        low = self.data['low'].min()
        yminor_unit_origin = round((high - low) / 12, 2)
        yminor_unit_origin = max(yminor_unit_origin, 0.01)

        yminor_unit = functools.reduce(min, map(lambda x: abs(x - yminor_unit_origin), filter(lambda x: x > (yminor_unit_origin-yminor_unit_origin/4), standard_unit)))
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
        cursor = Cursor(axlist[0], useblit=True, color='grey', linewidth=1)
        # axlist[0].yaxis.set_label_position("right")
        # axlist[0].yaxis.tick_right()
        axlist[0].tick_params(axis='y', which='both', labelleft=False, labelright=True)
        axlist[1].tick_params(axis='y', which='both', labelleft=True, labelright=False)

        # self.fig.tight_layout()
        # print(len(axlist))   # 8

        ylim_min = self.data_origin['low'].min()
        ylim_max = self.data_origin['high'].max()
        diff = (ylim_max - ylim_min) * 0.1
        axlist[0].set_ylim(ymin=ylim_min - diff, ymax=ylim_max + diff)
        # # 没有效果
        # plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        # plt.margins(0, 0)

        # axlist[3].fill_between(self.data.index, self.data['force_index'])

        plt.show()
        # plt.show(block=False)  # 显示
        # plt.close()  # 关闭plt，释放内存


def update(candle):
    # if candle.fig:
    #     plt.close(candle.fig)
    candle.more_panel_draw()
    candle.need_update = True


def show(candle):
    candle.show()


def open_graph(code, peroid, path=None):
    candle = DataFinanceDraw(code)
    if path:
        candle.load_data(path)
    else:
        candle.fetch_data(code, peroid)

    update(candle)
    show(candle)


if __name__ == "__main__":
    code = '000001'
    # code = '300502'
    code = '000999'
    period = 'day'   # m5 m30 day week
    open_graph(code, period, 'data/' + code + '.csv')
    # open_graph(code, period)

    # code = '000001'
    # candle = DataFinanceDraw(code)
    # candle.load_data('data/' + code + '.csv')
    # t = threading.Thread(target=update, args=(candle,))
    # t.start()
    # show()
    # t.join()
