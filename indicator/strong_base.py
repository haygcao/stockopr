# -*- coding: utf-8 -*-


def strong_base(quote, period):
    # ma_l = quote['ma150']
    # ma_m = quote['ma50']
    # ma_s = quote['ma30']

    max_ = quote[['ma30', 'ma100', 'ma150']].max()
    min_ = quote[['ma30', 'ma100', 'ma150']].min()

    mask = ((1 - min_ / max_) * 100 < 10)

    quote = quote.assign(strong_base=mask)

    return quote
