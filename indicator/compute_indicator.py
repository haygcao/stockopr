import indicator
from indicator import dynamical_system, macd, ema, force_index, atr, market_deviation
from pointor import signal_market_deviation


def compute_indicator(quote, period):
    # basic index data:
    # macd - macd_histogram
    quote = macd.compute_macd(quote)
    # ema - ema13 ema26
    quote = ema.compute_ema(quote)
    # force_index - force_index force_index13
    quote = force_index.force_index(quote)
    # dynamical system - dyn_sys_ema13(True/False), dyn_sys_macd(True/False), dyn_sys_long_period, dyn_sys
    quote = dynamical_system.dynamical_system_dual_period(quote, period=period)
    # atr - atr, ema26
    quote = atr.compute_atr(quote)
    # deviation - macd, force index
    quote = market_deviation.compute_index(quote, period, back_days=0)
    # support/resistance

    return quote