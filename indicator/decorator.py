import numpy

from config import config
from config.config import is_long_period


def computed(column_name=None):
    def decorate(func):
        def inner(*args, **kwargs):
            if column_name in (args[0]).columns:
                return args[0]
            if column_name.endswith('signal_enter') or column_name.endswith('signal_exit'):
                if not config.enabled_signal(column_name):
                    if 'stop_loss' in column_name:
                        args[0].insert(len(args[0].columns), 'stop_loss', numpy.nan)
                    args[0].insert(len(args[0].columns), column_name, numpy.nan)
                    return args[0]
            return func(*args, **kwargs)
        return inner
    return decorate


def ignore_long_period(column_name=None):
    def decorate(func):
        def inner(*args, **kwargs):
            if is_long_period(kwargs.get('period')):
                args[0].insert(len(args[0].columns), column_name, numpy.nan)
                return args[0]
            return func(*args, **kwargs)
        return inner
    return decorate


def dynamic_system_filter(column_name=None):
    def decorate(func):
        def inner(*args, **kwargs):
            quote = func(*args, **kwargs)
            mask = compute_enter_mask(quote, kwargs.get('period'))
            quote.loc[:, column_name] = quote[column_name].mask(mask, numpy.nan)

            return quote
        return inner

    return decorate


def compute_enter_mask(quote, period):
    mask = quote['dlxt_long_period'] < 0
    mask = mask | (quote['dlxt'] < 0)

    # 长周期 ema26 向上, 且 close > 长周期 ema26
    n = 26 if is_long_period(period) else 120
    ema = quote.close.ewm(span=n).mean()
    ema_shift = ema.shift(periods=1)
    mask = mask | (ema <= ema_shift) | (quote.close <= ema)

    ema_fast = quote.close.ewm(span=int(n / 2)).mean()
    macd_line = ema_fast - ema
    macd_line_shift = macd_line.shift(periods=1)
    mask = mask | (macd_line <= macd_line_shift)

    return mask
