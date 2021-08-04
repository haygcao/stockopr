# -*- coding: utf-8 -*-


def dma(data, n1=10, n2=50, m=10):
    """ 计算DMA
        输入参数：
            symbol <- str  标的代码
            start_time <- str  开始时间
            end_time <- 结束时间
            N1 <- 大周期均值
            N2 <- 小周期均值
        输出参数：
            DMA <- dataframe
    """
    ma1 = data['close'].rolling(n1).mean()
    ma2 = data['close'].rolling(n2).mean()
    data['dif'] = ma1 - ma2
    data['ama'] = data['dif'].rolling(m).mean()

    return data
