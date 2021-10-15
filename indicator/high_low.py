import numpy


def compute_high_low(quote, column='close', compute_high=True, weak=False):
    """
    以高点计算为例
    1 低于往前20天的高点, 忽略   更低的高点
    2 往前10天以内有过高点, 忽略   太近的高点
    3
    """
    adj = 1 if compute_high else -1
    close = quote[column]
    close_lshift = close.shift(periods=1)
    close_rshift = close.shift(periods=-1)
    close_rshift2 = close.shift(periods=-2)

    days_before = 20
    agg = 'max' if adj == 1 else 'min'
    mask = (adj * close > adj * close_lshift) & \
           (adj * close >= adj * close_rshift) & \
           (adj * close_rshift >= adj * close_rshift2)

    close_high_low = quote[column].mask(~mask, numpy.nan)

    # 若往前 20 日已有更大/小值, 则忽略当前值
    # close_high_low_agg = eval('close_high_low.rolling({}, min_periods=1).{}()'.format(days_before, agg))
    # mask = adj * close_high_low < adj * close_high_low_agg
    # close_high_low_adj = close_high_low.mask(mask, numpy.nan)

    # 若往前 20 日已有值, 则忽略当前值, 即保留最早的值(非最值), 忽略后面的更高/低的值, 即时间优先
    # close_high_low_adj_shift = close_high_low_adj.shift(periods=1)
    # mask = close_high_low_adj_shift.rolling(days_before // 2, min_periods=1).apply(lambda _s: _s.any()).fillna(0).astype(bool)
    # close_high_low_adj = close_high_low_adj.mask(mask, numpy.nan)

    # 不应该用到与当前交易日往后的数据
    # close_high_low_adj_lshift = close_high_low_adj.shift(periods=-days_before)
    # close_high_low_agg = eval('close_high_low_adj_lshift.rolling({}, min_periods=1).{}()'.format(days_before, agg))
    # mask = adj * close_high_low_adj < adj * close_high_low_agg
    # mask[:days_before] = True
    # series = close_high_low.iloc[:days_before]
    # p = eval('series.{}()'.format(agg))
    # index = numpy.where(series == p)[0][0]
    # date = series.index[index]
    # mask.at[date] = False
    # close_high_low_adj = close_high_low_adj.mask(mask, numpy.nan)

    # index 不会 shift, 只是值 shift
    # close_high_low_shift = close_high_low.shift(periods=1)
    # days = close_high_low.index - close_high_low_shift.index

    # for i in range(1, len(close_high_low) - 1, 2):
    close_high_low = filter_high_low(adj, close_high_low, days_before, weak)

    hl_column = '{}_period'.format(agg)
    hl_column = 'weak_' + hl_column if weak else hl_column
    quote[hl_column] = quote[column].mask(~quote.index.isin(close_high_low.index), numpy.nan)

    return quote


def filter_high_low(adj, close_high_low, days_before, weak=False):
    index_full = close_high_low.index

    days_before_after = 80
    adj = adj if not weak else -adj
    i = 1
    i_prev = i - 1
    i_ignored = i_prev
    i_ignore_set = set()
    i_valid = -1
    i_prev_valid = -1

    close_high_low = close_high_low[close_high_low.notna()]
    index = close_high_low.index

    while i < len(close_high_low):
        # delta_before = (index[i] - index[i_prev]).days
        # delta_before_ignored = (index[i] - index[i_ignored]).days

        # 调试时使用
        # date_prev = index[i_prev]
        # date = index[i]

        delta_before = index_full.get_loc(index[i]) - index_full.get_loc(index[i_prev]) + 1
        delta_before_ignored = index_full.get_loc(index[i]) - index_full.get_loc(index[i_ignored]) + 1
        # delta_after = (index[i + 1] - index[i]).days
        if delta_before > days_before_after:  # and delta_after > days_before_after:
            # 忽略曾经的值, 应该是没有问题的
            # 比如 A B C D E 中 C 会被忽略
            # 时间点1, B, AB 值有效
            # 时间点2, C, AB 值有效, C被忽略, 因为 C 为单独的值
            # 时间点3, D, AB 值有效, C被忽略, 因为 C D 间隔时间大于 60 天, D被忽略, 因为 D 为单独的值
            # 时间点4, E, AB 值有效, C被忽略, 因为 C D 间隔时间大于 60 天, DE 值有效
            # 所以, 在 C 之前之后的时间点, 所有高低值是稳定的, 基于高低值计算的信号也是稳定的
            close_high_low.iat[i_prev] = numpy.nan

            # 可能会丢失高低值
            # 比如, A B C, A B 间隔小于 20 天, B 被忽略
            # A C 间隔大于 60 天, A 被忽略
            # B C 间隔大于20天, 小于60天, 属于有效高低值, 但会被忽略
            # i_prev = i
            # i += 1
            i_prev += 1
            i = i + 1 if i == i_prev else i
            i_ignored = i_prev
            continue

        # 未创出新高/新低
        if adj * close_high_low.iloc[i] < adj * close_high_low.iloc[i_prev]:
            if weak:
                close_high_low.iat[i_prev] = numpy.nan
                i_prev += 1
                i = i + 1 if i == i_prev else i
                continue

            if delta_before < days_before:
                i_ignore_set.add(i)
                i_ignored = i
                i += 1
                continue

        # 间隔时间太短
        if delta_before_ignored < 5 or delta_before < days_before:
            # 可能不会被忽略
            # i_ignore_set.add(i)
            # i += 1

            # A B C 三个点价格
            close_high_low.iat[i_prev] = numpy.nan
            i_prev += 1
            i = i + 1 if i == i_prev else i
            i_ignored = i_prev
            continue

        reset_invalid_value(close_high_low, i, i_ignore_set, i_prev)
        i_valid = i
        i_prev_valid = i_prev
        i += 2
        i_prev = i - 1
        i_ignored = i_prev

        if i >= len(close_high_low):
            break
        # 当矩阵运算未处理近期高低值时, 需要忽略往前近期的次高低值, 即最值优先
        # delta_before = (close_high_low.index[i_prev] - close_high_low.index[i_valid]).days
        delta_before = index_full.get_loc(index[i_valid]) - index_full.get_loc(index[i_prev]) + 1
        if delta_before < 5:
            close_high_low.iat[i_prev] = numpy.nan
            i_prev += 1
            i = i + 1 if i == i_prev else i
            i_ignored = i_prev
            continue

    reset_invalid_value(close_high_low, i_valid, i_ignore_set, i_prev_valid)
    if len(close_high_low) > 1 and (index[-1] - index[-2]).days > days_before_after:
        close_high_low.iat[-1] = numpy.nan
    close_high_low = close_high_low[close_high_low.notna()]
    if len(close_high_low) % 2 == 1:
        close_high_low = close_high_low.iloc[:-1]

    return close_high_low


def reset_invalid_value(close_high_low, i, i_ignore_set, i_prev):
    if i_prev in i_ignore_set:
        i_ignore_set.remove(i_prev)
    if i in i_ignore_set:
        i_ignore_set.remove(i)
    if i_ignore_set:
        close_high_low[list(i_ignore_set)] = numpy.nan