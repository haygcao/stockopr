from pointor import signal_dynamical_system, signal_channel, signal_force_index, signal_value_return, signal_blt, \
    signal_vcp, signal_step, signal_step_breakout, signal_volume_ad, signal_resistance_support, signal_market_deviation, \
    signal_stop_loss, signal_weak

signal_func = {
    "dynamical_system_signal_enter": signal_dynamical_system.signal_enter,
    "channel_signal_enter": signal_channel.signal_enter,
    "force_index_signal_enter": signal_force_index.signal_enter,
    "value_return_signal_enter": signal_value_return.signal_enter,
    "blt_signal_enter": signal_blt.signal_enter,
    "vcp_signal_enter": signal_vcp.signal_enter,
    "step_signal_enter": signal_step.signal_enter,
    "step_breakout_signal_enter": signal_step_breakout.signal_enter,
    "volume_ad_signal_enter": signal_volume_ad.signal_enter,
    "resistance_support_signal_enter": signal_resistance_support.signal_enter,
    "weak_signal_enter": signal_weak.signal_enter,
    "force_index_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "volume_ad_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "skdj_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "rsi_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,
    "macd_bull_market_deviation_signal_enter": signal_market_deviation.signal_enter,

    "dynamical_system_signal_exit": signal_dynamical_system.signal_exit,
    "channel_signal_exit": signal_channel.signal_exit,
    "force_index_signal_exit": signal_force_index.signal_exit,
    "volume_ad_signal_exit": signal_volume_ad.signal_exit,
    "resistance_support_signal_exit": signal_resistance_support.signal_exit,
    "weak_signal_exit": signal_weak.signal_exit,
    "force_index_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "volume_ad_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "skdj_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "rsi_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "macd_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "stop_loss_signal_exit": signal_stop_loss.signal_exit,
  }


# 'second_stage'
# 'dyn_sys_long_period' >= 0
# 'dyn_sys' >= 0
# 长周期 ema26 向上, 且 close > 长周期 ema26   slow_ma_ins
# (快均线 - 慢均线) 值增大   diff_fma_sma_ins
# a/d
# rps
# dmi

mask_trend_up = [
    'mask_dyn_sys_long_period', 'mask_dyn_sys', 'mask_slow_ma_ins', 'mask_diff_fma_sma_ins', 'mask_ad', 'mask_rps', 'mask_second_stage']

signal_mask_column = {
    "macd_signal_enter": [],
    "force_index_signal_enter": mask_trend_up + ['mask_dmi'],
    "volume_ad_signal_enter": mask_trend_up + ['mask_dmi'],
    "dynamical_system_signal_enter": mask_trend_up,
    "channel_signal_enter": [],
    "resistance_support_signal_enter": ['mask_resistance'] + mask_trend_up + ['mask_second_stage'],
    "value_return_signal_enter": mask_trend_up + ['mask_dmi'] + ['mask_value_return'],
    "blt_signal_enter": mask_trend_up + ['mask_dmi'],
    "vcp_signal_enter": mask_trend_up,
    "step_signal_enter": ['mask_step'] + mask_trend_up + ['mask_step'],
    "step_breakout_signal_enter": ['mask_step'] + mask_trend_up + ['mask_second_stage'] + ['mask_step'],
    "weak_signal_enter": [],  # mask_trend_up,
    "macd_bull_market_deviation_signal_enter": ['mask_second_stage'],  # ['mask_dyn_sys_long_period'], # ['second_stage'],
    "force_index_bull_market_deviation_signal_enter": [],
    "volume_ad_bull_market_deviation_signal_enter": [],
    "skdj_bull_market_deviation_signal_enter": [],
    "rsi_bull_market_deviation_signal_enter": [],

    "macd_signal_exit": [],
    "force_index_signal_exit": [],
    "volume_ad_signal_exit": [],
    "dynamical_system_signal_exit": [],
    "channel_signal_exit": [],
    "resistance_support_signal_exit": ['mask_support'],
    "stop_loss_signal_exit": [],
    "macd_bear_market_deviation_signal_exit": [],
    "force_index_bear_market_deviation_signal_exit": [],
    "volume_ad_bear_market_deviation_signal_exit": [],
    "skdj_bear_market_deviation_signal_exit": [],
    "rsi_bear_market_deviation_signal_exit": []
}
