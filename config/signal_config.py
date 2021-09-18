from pointor import signal_dynamical_system, signal_channel, signal_force_index, signal_ema_value, signal_blt, \
  signal_vcp, signal_step, signal_step_breakout, signal_volume_ad, signal_resistance_support, signal_market_deviation, \
  signal_stop_loss


signal_func = {
    "dynamical_system_signal_enter": signal_dynamical_system.signal_enter,
    "channel_signal_enter": signal_channel.signal_enter,
    "force_index_signal_enter": signal_force_index.signal_enter,
    "ema_value_signal_enter": signal_ema_value.signal_enter,
    "blt_signal_enter": signal_blt.signal_enter,
    "vcp_signal_enter": signal_vcp.signal_enter,
    "step_signal_enter": signal_step.signal_enter,
    "step_breakout_signal_enter": signal_step_breakout.signal_enter,
    "volume_ad_signal_enter": signal_volume_ad.signal_enter,
    "resistance_support_signal_enter": signal_resistance_support.signal_enter,
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
    "force_index_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "volume_ad_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "skdj_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "rsi_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "macd_bear_market_deviation_signal_exit": signal_market_deviation.signal_exit,
    "stop_loss_signal_exit": signal_stop_loss.signal_exit,
  }

signal_mask_func = {
  "macd_signal_enter": None,
  "force_index_signal_enter": None,
  "volume_ad_signal_enter": None,
  "dynamical_system_signal_enter": None,
  "channel_signal_enter": None,
  "resistance_support_signal_enter": None,
  "ema_value_signal_enter": None,
  "blt_signal_enter": None,
  "vcp_signal_enter": None,
  "step_signal_enter": None,
  "step_breakout_signal_enter": None,
  "macd_bull_market_deviation_signal_enter": None,
  "force_index_bull_market_deviation_signal_enter": None,
  "volume_ad_bull_market_deviation_signal_enter": None,
  "skdj_bull_market_deviation_signal_enter": None,
  "rsi_bull_market_deviation_signal_enter": None,

  "macd_signal_exit": None,
  "force_index_signal_exit": None,
  "volume_ad_signal_exit": None,
  "dynamical_system_signal_exit": None,
  "channel_signal_exit": None,
  "resistance_support_signal_exit": None,
  "stop_loss_signal_exit": None,
  "macd_bear_market_deviation_signal_exit": None,
  "force_index_bear_market_deviation_signal_exit": None,
  "volume_ad_bear_market_deviation_signal_exit": None,
  "skdj_bear_market_deviation_signal_exit": None,
  "rsi_bear_market_deviation_signal_exit": None
}