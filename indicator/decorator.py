import numpy

from config.config import is_long_period


def computed(column_name=None):
    def decorate(func):
        def inner(*args, **kwargs):
            if column_name in (args[0]).columns:
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
            print('dynamic_system_filter')
            quote.loc[:, column_name] = quote[column_name].mask(quote['dlxt_long_period'] < 0, numpy.nan)
            quote.loc[:, column_name] = quote[column_name].mask(quote['dlxt'] < 0, numpy.nan)
            return quote
        return inner

    return decorate
