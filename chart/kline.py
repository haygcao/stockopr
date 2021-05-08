# -*- coding: utf-8 -*-
import threading
import time

import sys

import mplfinance as mpf
import matplotlib as mpl  # 用于设置曲线参数
from cycler import cycler  # 用于定制线条颜色
import pandas
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.widgets import Cursor

sys.path.append(".")
from selector.plugin import dynamical_system, force_index


show_volume = False
show_macd = False
panel_volume = 1 if show_volume else 0
panel_dlxt = panel_volume + 1
panel_qlzs = panel_dlxt + 1
panel_macd = panel_qlzs + 1

def import_csv(stock_code):
    # 导入股票数据
    df = pandas.read_csv('data/' + stock_code + '.csv', encoding='gbk')
    # 格式化列名，用于之后的绘制
    df.rename(
        columns={
            '日期': 'date', '开盘价': 'open',
            '最高价': 'high', '最低价': 'low',
            '收盘价': 'close', '成交量': 'volume'},
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

    def __init__(self):
        self.data_origin = pandas.DataFrame()
        self.data = None
        self.need_update = False
        self.style = None

        # 设置基本参数
        # type:绘制图形的类型，有candle, renko, ohlc, line等
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
            volume=show_volume,
            title='\nA_stock candle_line',
            ylabel='OHLC Candles',
            ylabel_lower='Shares\nTraded Volume',
            # axisoff=True,
            figratio=(16, 9),
            figscale=1)

        self.add_plot = []
        self.fig = None
        self.edge_color = []

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
            edge='black',
            wick='black',
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
        mpl.rcParams['toolbar'] = 'None'

    def my_data(self, file_name='2020.csv'):
        """
        获取数据,把数据格式化成mplfinance的标准格式
        :return:
        """
        data = import_csv(file_name)
        self.data_origin = data

        return data

    def more_panel_draw(self):
        data = self.data_origin.iloc[-100:]
        self.data = data
        """
        make_addplot 绘制多个图，这里添加macd指标为例
        """

        dynamical_system.dynamical_system(data)
        self.edge_color = ['g' if v > 0 else 'r' if v < 0 else '#ADD8E6' for v in data["dlxt"]]
        self.set_plot_style()
        dlxt = data["dlxt"]
        dlxt.values[:] = 1

        force_index.force_index(data)
        force_index_color = ['g' if v >= 0 else 'r' for v in data["force_index"]]

        self.add_plot = [
            mpf.make_addplot(data['force_index'], type='bar', width=1, panel=panel_qlzs, color=force_index_color),
            mpf.make_addplot(data['force_index'], type='line', width=1, panel=panel_qlzs, color='black'),
            mpf.make_addplot(dlxt, type='bar', width=1, panel=panel_dlxt, color=self.edge_color),
            # mplfinance.make_addplot(data['PercentB'], panel=1, color='g', secondary_y='auto'),
        ]
        if show_macd:
            # 计算macd的数据。计算macd数据可以使用第三方模块talib（常用的金融指标kdj、macd、boll等等都有，这里不展开了），如果在金融数据分析和量化交易上深耕的朋友相信对这些指标的计算原理已经了如指掌，直接通过原始数据计算即可，以macd的计算为例如下：
            exp12 = data['close'].ewm(span=12, adjust=False).mean()
            exp26 = data['close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9, adjust=False).mean()

            # 添加macd子图
            histogram = macd - signal
            # histogram[histogram < 0] = None
            # histogram_positive = histogram
            # histogram = macd - signal
            # histogram[histogram >= 0] = None
            # histogram_negative = histogram

            # macd panel
            colors = ['g' if v >= 0 else 'r' for v in histogram]
            self.add_plot.extend(
                [
                    mpf.make_addplot(exp12, type='line', color='y'),
                    mpf.make_addplot(exp26, type='line', color='r'),
                    mpf.make_addplot(histogram, type='bar', panel=panel_macd, color=colors),  # color='dimgray'
                    # mpf.make_addplot(histogram_positive, type='bar', width=0.7, panel=2, color='b'),
                    # mpf.make_addplot(histogram_negative, type='bar', width=0.7, panel=2, color='fuchsia'),
                    mpf.make_addplot(macd, panel=panel_macd, color='fuchsia', secondary_y=True),
                    mpf.make_addplot(signal, panel=panel_macd, color='b', secondary_y=True), ])

        # fig = mpf.figure(figsize=(10, 7), style=self.style)  # pass in the self defined style to the whole canvas
        # ax = fig.add_subplot(2, 1, 1)  # main candle stick chart subplot, you can also pass in the self defined style here only for this subplot
        # av = fig.add_subplot(2, 1, 2, sharex=ax)  # volume chart subplot
        # mpf.plot(self.data, type='candle', ax=ax, volume=av)

    def show(self):
        self.fig, axlist = mpf.plot(self.data, **self.kwargs,
                                    style=self.style,
                                    show_nontrading=False,
                                    addplot=self.add_plot,
                                    main_panel=0,
                                    volume_panel=panel_volume,
                                    returnfig=True,
                                    panel_ratios=(8, 0.2, 1.8)
                                    )

        # import matplotlib.dates as mdates
        # xmajorLocator = mdates.DayLocator(1)
        # xmajorFormatter = mdates.DateFormatter('%Y-%m-%d')
        # xminorLocator = mdates.DayLocator()
        # axlist[-1].xaxis.set_major_locator(xmajorLocator)
        # axlist[-1].xaxis.set_major_formatter(xmajorFormatter)

        # cursor = Cursor(self.fig, useblit=True, color='red', linewidth=2)
        cursor = Cursor(axlist[0], useblit=True, color='grey', linewidth=1)

        plt.show()
        # plt.show(block=False)  # 显示
        # plt.close()  # 关闭plt，释放内存


def update(candle, csv):
    # if candle.fig:
    #     plt.close(candle.fig)
    candle.my_data(csv)
    candle.more_panel_draw()
    candle.need_update = True


def show(candle):
    candle.show()


if __name__ == "__main__":
    candle = DataFinanceDraw()
    # candle.my_data('300502')
    # t = threading.Thread(target=update, args=(candle,))
    # t.start()
    update(candle, '300502')
    show(candle)

    # t.join()

