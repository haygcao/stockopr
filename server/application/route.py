# -*- coding: utf-8 -*-

from ..business.main_handler import MainHandler
from ..business.main_handler import OrderHandler
from ..business.main_handler import QueryMoneyHandler
from ..business.main_handler import QueryPositionHandler
from ..business.main_handler import QueryOperationDetailHandler
from ..business.main_handler import QueryWithdrawOrderHandler
from ..business.main_handler import QueryTodayOrderHandler
from ..business.main_handler import WithdrawHandler
from ..business.main_handler import QueryTradeSignalHandler


handlers = [
    (r"/", MainHandler),
    (r"/api/order", OrderHandler),
    (r"/api/query_money", QueryMoneyHandler),
    (r"/api/query_position", QueryPositionHandler),
    (r"/api/query_operation_detail", QueryOperationDetailHandler),
    (r"/api/query_today_order", QueryTodayOrderHandler),
    (r"/api/query_withdraw_order", QueryWithdrawOrderHandler),
    (r"/api/withdraw", WithdrawHandler),
    (r"/api/query_trade_signal", QueryTradeSignalHandler)
]
