import datetime
from dataclasses import dataclass

from config import config


@dataclass
class Asset:
    total_money = 0
    avail_money = 0

    def __init__(self, total_money, avail_money):
        self.total_money = total_money
        self.avail_money = avail_money

    def __str__(self):
        return 'total_money: {}, avail_money: {}'.format(self.total_money, self.avail_money)


@dataclass
class Position:
    code = ''
    current_position = 0
    avail_position = 0

    def __init__(self, code, current, avail):
        self.code = code
        self.current_position = current
        self.avail_position = avail

    def __str__(self):
        return 'code: {}, current_position: {}, avail_position: {}'.format(self.code, self.current_position, self.avail_position)


@dataclass
class OperationDetail:
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
        self.amount = round(price_limited * count, 3)

        market = 'sz' if int(code[:2]) < 60 else 'sh'
        direct = 'buy' if self.operation == 'B' else 'sell'

        charge = 'config.charge_{}_{}'.format(direct, market)
        self.cost = round(self.amount * eval(charge), 3)

    def __str__(self):
        ret = ''
        for i in self.__dir__():
            if i.startswith('__'):
                continue
            ret += i + ': ' + str(eval('self.{}'.format(i)))
            ret += ' '
        return ret


@dataclass
class TradeOrder:
    code = ''
    position = 0
    open_price = 0
    stop_loss = 0
    stop_profit = 0
    risk_rate = 0
    profitability_ratios = 0

    def __init__(self, code, position, open_price, stop_loss, stop_profit):
        self.code = code
        self.position = position
        self.open_price = open_price
        self.stop_loss = stop_loss
        self.stop_profit = stop_profit
        self.risk_rate = (open_price - stop_loss) / open_price
        self.profitability_ratios = (stop_profit - open_price) / (open_price - stop_loss)

    def __str__(self):
        ret = ''
        for i in self.__dir__():
            if i.startswith('__'):
                continue
            ret += i + ': ' + str(eval('self.{}'.format(i)))
            ret += ' '
        return ret


@dataclass
class WithdrawOrder:
    trade_time: datetime.datetime
    code: str
    direct: str
    count: int
    count_ed: int
    price: float
    price_ed: float
    count_withdraw: int

    def __init__(self, trade_time, code, direct, count, count_ed, price, price_ed, count_withdraw):
        self.trade_time = trade_time
        self.code = code
        self.direct = direct
        self.count = count
        self.count_ed = count_ed
        self.price = price
        self.price_ed = price_ed
        self.count_withdraw = count_withdraw

    def __str__(self):
        ret = ''
        for i in self.__dir__():
            if i.startswith('__'):
                continue
            ret += i + ': ' + str(eval('self.{}'.format(i)))
            ret += ' '
        return ret