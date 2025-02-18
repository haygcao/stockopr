import datetime
from dataclasses import dataclass

from config import config
from util import dt


class TradeData:
    def __str__(self):
        ret = ''
        for i in self.__dir__():
            if i.startswith('__'):
                continue
            ret += i + ': ' + str(eval('self.{}'.format(i)))
            ret += ' '
        return ret


@dataclass
class Asset(TradeData):
    date: datetime.date
    period: datetime.date
    origin = 0
    total_money = 0
    net_money = 0
    avail_money = 0
    deposit = 0
    market_value = 0
    position_percent = 0
    profit = 0
    profit_percent = 0

    def __init__(self, total_money, avail_money, net_money=0, deposit=0, market_value=0, date=None):
        self.date = dt.get_trade_date() if not date else date
        self.total_money = float(total_money)
        self.net_money = net_money if net_money > 0 else total_money
        self.avail_money = float(avail_money)
        self.deposit = deposit
        self.market_value = float(market_value if market_value > 0 else self.total_money - self.avail_money)
        asset = float(self.origin if self.origin else self.net_money)
        self.position_percent = round(100 * self.market_value / asset, 3)

    def update_origin(self, origin, period):
        self.origin = float(origin)
        self.period = datetime.datetime.strptime(period, '%Y-%m-%d').date()

        self.profit_percent = round(100 * self.profit / self.origin, 3)
        self.position_percent = round(100 * (self.market_value / self.origin), 3)


@dataclass
class Position(TradeData):
    date: datetime.date
    code = ''
    current_position = 0
    avail_position = 0
    price = 0
    price_cost = 0
    profit_total = 0
    cost = 0
    market_value = 0
    profit_total_percent = 0

    def __init__(self, code, current, avail, price_cost, price, profit_total, date=None):
        self.date = dt.get_trade_date() if not date else date
        self.code = code
        self.current_position = current
        self.avail_position = avail
        self.price = price
        self.price_cost = price_cost
        self.profit_total = profit_total

        self.cost = round(self.price_cost * self.current_position, 3)
        self.market_value = round(self.price * self.current_position, 3)
        self.profit_total_percent = round(100 * self.profit_total / self.cost, 3) if self.cost > 0 else 0

    def update_price_cost(self, price_cost):
        self.price_cost = price_cost
        self.cost = round(self.price_cost * self.current_position, 3)
        self.profit_total = self.market_value - self.cost
        self.profit_total_percent = round(100 * self.profit_total / self.cost, 3)

    def add_profile(self, profit):
        self.profit_total += profit
        self.profit_total_percent = round(100 * self.profit_total / self.cost, 3)
        self.price_cost = round(self.price - self.profit_total / self.current_position, 3)


@dataclass
class OperationDetail(TradeData):
    trade_time: datetime.datetime
    code: str
    operation: str
    price: float
    price_trade: float   # 用于当天交易时段计算可用资金和可用仓位
    price_limited: float   # 非限价委托未成交时, 进行重新委托
    count: int
    amount: float
    cost: float

    def __init__(self, trade_time, code, price, price_trade, price_limited, count):
        if isinstance(trade_time, str):
            self.trade_time = datetime.datetime.strptime(trade_time, '%Y-%m-%d %H:%M:%S')
        else:
            self.trade_time = trade_time
        self.code = code
        self.operation = 'B' if count > 0 else 'S'
        self.price = price
        self.price_trade = price_trade
        self.price_limited = price_limited
        self.count = count
        self.amount = round(price * count, 3)

        market = 'sz' if int(code[:2]) < 60 else 'sh'
        # direct = 'buy' if self.operation == 'B' else 'sell'
        # charge = 'config.charge_{}_{}'.format(direct, market)
        # self.cost = abs(round(self.amount * eval(charge), 3))
        self.cost = config.charge(self.amount, self.operation, market)


@dataclass
class TradeOrder(TradeData):
    date = None
    code = ''
    position = 0
    capital_quota = 0
    try_price = 0
    stop_loss = 0
    half_pos_price = 0
    full_pos_price = 0
    stop_profit = 0
    risk_rate = 0
    profitability_ratios = 0
    strategy = ''
    in_position = False

    def __init__(self, date, code, position, capital_quota, try_price, stop_loss, half_pos_price, full_pos_price, stop_profit,
                 risk_rate_total, strategy, in_position):
        self.date = date
        self.code = code
        self.position = position
        self.capital_quota = capital_quota
        self.try_price = try_price
        self.half_pos_price = half_pos_price
        self.full_pos_price = full_pos_price
        self.stop_loss = stop_loss
        self.stop_profit = stop_profit
        self.risk_rate = (try_price - stop_loss) / try_price
        self.risk_rate_total = risk_rate_total
        self.profitability_ratios = 0  # (stop_profit - try_price) / (try_price - stop_loss)
        self.strategy = strategy
        self.in_position = in_position


@dataclass
class WithdrawOrder(TradeData):
    trade_time: datetime.datetime
    code: str
    direct: str
    count: int
    count_ed: int
    price: float
    price_ed: float
    count_withdraw: int
    status: str

    def __init__(self, trade_time, code, direct, count, count_ed, price, price_ed, count_withdraw, status):
        self.trade_time = trade_time
        self.code = code
        self.direct = direct
        self.count = count
        self.count_ed = count_ed
        self.price = price
        self.price_ed = price_ed
        self.count_withdraw = count_withdraw
        self.status = status
