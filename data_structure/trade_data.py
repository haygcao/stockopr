from dataclasses import dataclass


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
        return 'code: {}, current_position{}, avail_position: {}'.format(self.code, self.current_position, self.avail_position)


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
