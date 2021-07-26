
1. 从沪深所有股票列表中, 按候选策略扫描, 将满足条件的股票加入到 portfolio 表中, 设置 status 为 candidate
2. 周期地扫描 portfolio 表中 status 为 candidate 的股票, 将进入调整期股票的 status 设置为 traced
3. 使用跟踪策略周期地扫描 portfolio 表中 status 为 traced 的股票, 将满足条件的股票的 status 设置为 allow_buy

all ---候选---> candidate ---调整---> traced ---买点---> allow_buy
strong base

候选策略(candidate strategy): second_stage, super, strong_base, dyn_sys_green, dyn_sys_blue
跟踪策略(trace strategy): strong_base_breakout, magic_line, vcp_breakout, bull_deviation, osc_oversold

strong_base_breakout:
  input: strong_base
  period: day
ema_value:
  input: super, second_stage, dyn_sys_green, dyn_sys_blue
  period: day
magic_line:
  input: super
  period: week
vcp_breakout:
  input: super
  period: day
bull_deviation:
  input: second_stage, dyn_sys_green, dyn_sys_blue
  period: day
osc_oversold
  input: second_stage, dyn_sys_green, dyn_sys_blue
  period: day