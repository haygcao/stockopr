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
