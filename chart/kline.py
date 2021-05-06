# -*- coding: utf-8 -*-

import mplfinance as mpf
import matplotlib as mpl  # 用于设置曲线参数
from cycler import cycler  # 用于定制线条颜色
import pandas
import matplotlib.pyplot as plt


def import_csv(stock_code):
    # 导入股票数据
    df = pandas.read_csv('data/' + stock_code + '.csv', encoding='gbk')
    # 格式化列名，用于之后的绘制
    df.rename(
        columns={
            '日期': 'Date', '开盘价': 'Open',
            '最高价': 'High', '最低价': 'Low',
            '收盘价': 'Close', '成交量': 'Volume'},
        inplace=True)
    # 转换为日期格式
    df['Date'] = pandas.to_datetime(df['Date'], format='%Y-%m-%d')
    # 将日期列作为行索引
    df.set_index(['Date'], inplace=True)
    df.sort_index(ascending=True, inplace=True)

    return df


class DataFinanceDraw(object):
    """
    获取数据，并按照 mplfinanace 需求的格式格式化，然后绘图
    """

    def __init__(self):
        self.data = pandas.DataFrame()

    def my_data(self, file_name='2020.csv'):
        """
        获取数据,把数据格式化成mplfinance的标准格式
        :return:
        """
        data = import_csv(file_name)
        self.data = data

        return data

    def more_panel_draw(self):
        data = self.data.iloc[-100:]
        """
        make_addplot 绘制多个图，这里添加macd指标为例
        """

        # 计算macd的数据。计算macd数据可以使用第三方模块talib（常用的金融指标kdj、macd、boll等等都有，这里不展开了），如果在金融数据分析和量化交易上深耕的朋友相信对这些指标的计算原理已经了如指掌，直接通过原始数据计算即可，以macd的计算为例如下：
        exp12 = data['Close'].ewm(span=12, adjust=False).mean()
        exp26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()

        # 添加macd子图
        histogram = macd - signal
        histogram[histogram < 0] = None
        histogram_positive = histogram
        histogram = macd - signal
        histogram[histogram >= 0] = None
        histogram_negative = histogram

        add_plot = [
            mpf.make_addplot(exp12, type='line', color='y'),
            mpf.make_addplot(exp26, type='line', color='r'),
            mpf.make_addplot(histogram_positive, type='bar', width=0.7, panel=2, color='b'),
            mpf.make_addplot(histogram_negative, type='bar', width=0.7, panel=2, color='fuchsia'),
            mpf.make_addplot(macd, panel=2, color='fuchsia', secondary_y=True),
            mpf.make_addplot(signal, panel=2, color='b', secondary_y=True),
            # mplfinance.make_addplot(data['PercentB'], panel=1, color='g', secondary_y='auto'),
        ]

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
        kwargs = dict(
            type='candle',
            mav=(7, 30, 60),
            volume=True,
            title='\nA_stock candle_line',
            ylabel='OHLC Candles',
            ylabel_lower='Shares\nTraded Volume',
            figratio=(15, 10),
            figscale=5)

        # 设置marketcolors
        # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
        # down:与up相反，这样设置与国内K线颜色标准相符
        # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
        # wick:灯芯(上下影线)颜色
        # volume:成交量直方图的颜色
        # inherit:是否继承，选填
        mc = mpf.make_marketcolors(
            up='red',
            down='green',
            edge='i',
            wick='i',
            volume='in',
            inherit=True)

        # 设置图形风格
        # gridaxis:设置网格线位置
        # gridstyle:设置网格线线型
        # y_on_right:设置y轴位置是否在右
        s = mpf.make_mpf_style(
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

        mpf.plot(data, **kwargs,
                 style=s,
                 show_nontrading=False,
                 addplot=add_plot,
                 main_panel=0, volume_panel=1,
                 )

        plt.show()  # 显示
        plt.close()  # 关闭plt，释放内存



if __name__ == "__main__":
    candle = DataFinanceDraw()
    candle.my_data('300502')
    candle.more_panel_draw()

