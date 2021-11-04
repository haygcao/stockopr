# -*- coding: utf-8 -*-
import datetime
import json

import tornado.web

from .. import config
from ..component import tradeapi, tradeapi_credit, helper


def base_filter(func):
    def wrapper(self, *args, **kwargs):
        screen_size = helper.get_screen_size()
        if screen_size != config.screen_size:
            self.write({'ret_code': -1, 'err_msg': 'screen size({}) not adapted'.format(screen_size)})
            return

        now = datetime.datetime.now()
        w_day = now.isoweekday()
        hour = now.hour
        minute = now.minute
        if w_day <= 5 and (hour < 15 and (hour > 9 or (hour == 9 and minute >= 15))):
            self.write({'ret_code': -1, 'err_msg': ''})
            return

        return func(self, *args, **kwargs)

    return wrapper


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # The value of the 'Access-Control-Allow-Origin' header in the response must not be the wildcard '*' when the request's credentials mode is 'include'. Origin 'http://localhost:4200' is therefore not allowed access. The credentials mode of requests initiated by the XMLHttpRequest is controlled by the withCredentials attribute.
        # self.set_header('Access-Control-Allow-Origin', 'http://kylin-ux.com:4200')
        #self.set_header('Access-Control-Allow-Origin', 'http://localhost:4200')
        self.set_header('Access-Control-Allow-Origin', '*')
        # self.set_header("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        self.set_header("Access-Control-Allow-Headers", '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, GET, OPTIONS')
        # set-cookie in response not set for Angular2 post request
        # because CORS
        # return this.http.post('http://localhost:8888/api/query_mshopbook_init_data', JSON.stringify({}), { withCredentials: true })
        # The value of the 'Access-Control-Allow-Credentials' header in the response is 'True' which must be 'true' when the request's credentials mode is 'include'. Origin 'http://localhost:4200' is therefore not allowed access. The credentials mode of requests initiated by the XMLHttpRequest is controlled by the withCredentials attribute.
        # self.set_header('Access-Control-Allow-Credentials', 'true')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

        
class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        self.write({})


class OrderHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")
        
    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        code = param['code']
        direct = param['direct']
        price = param['price']
        count = param['count']
        auto = param['auto']

        account_id = param['account_id']
        if account_id == config.ACCOUNT_ID_PT:
            tradeapi.order(direct, code, count, price, auto=auto)
        else:
            op_type = param['op_type']
            tradeapi_credit.order(op_type, direct, code, count, price, auto=auto)
        self.write({})


class WithdrawHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        direct = param['direct']

        tradeapi.withdraw(direct)

        self.write({})


class QueryWithdrawOrderHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        account_id = param['account_id']
        if account_id == config.ACCOUNT_ID_PT:
            order_list = tradeapi.get_order()
        else:
            order_list = tradeapi_credit.get_order()
        self.write(json.dumps(order_list))


class QueryMoneyHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    @base_filter
    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        account_id = param['account_id']
        if account_id == config.ACCOUNT_ID_PT:
            r = tradeapi.get_asset()
        else:
            r = tradeapi_credit.get_asset()
        self.write(r)


class QueryPositionHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    @base_filter
    def post(self):
        param = self.request.body.decode('utf-8')
        print(param)
        param = json.loads(param)
        if 'code' in param and param['code']:
            code = param['code']
        else:
            code = None

        account_id = param['account_id']
        if account_id == config.ACCOUNT_ID_PT:
            position = tradeapi.query_position(code)
        else:
            position = tradeapi_credit.query_position(code)

        self.write(json.dumps(position))


class QueryOperationDetailHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    @base_filter
    def post(self):
        param = self.request.body.decode('utf-8')
        print(param)
        param = json.loads(param)
        if 'code' in param and param['code']:
            code = param['code']
        else:
            code = None

        account_id = param['account_id']
        if account_id == config.ACCOUNT_ID_PT:
            detail_list = tradeapi.get_operation_detail(code)
        else:
            detail_list = tradeapi_credit.get_operation_detail(code)
        self.write(json.dumps(detail_list))


class QueryTodayOrderHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    @base_filter
    def post(self):
        param = self.request.body.decode('utf-8')
        print(param)
        param = json.loads(param)
        if 'code' in param and param['code']:
            code = param['code']
        else:
            code = None

        account_id = param['account_id']
        if account_id == config.ACCOUNT_ID_PT:
            detail_list = tradeapi.get_operation_detail(code)
        else:
            detail_list = tradeapi_credit.get_today_order(code)
        self.write(json.dumps(detail_list))


class QueryTradeSignalHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        param = self.request.body.decode('utf-8')
        print(param)
        param = json.loads(param)

        if 'date' in param and param['date']:
            date = datetime.datetime.strptime(param['date'], '%Y-%m-%d %H:%M:%S')
        else:
            date = None

        from pointor import signal
        from config import config
        supplemental_signal_path = config.supplemental_signal_path
        period = 'day'
        supplemental_signal = signal.get_supplemental_signal(supplemental_signal_path, period)

        signal_list = []
        from trade_manager import trade_manager
        position_list = trade_manager.query_current_position()
        position_list = [position.code for position in position_list]
        now = datetime.datetime.now() - datetime.timedelta(minutes=5)
        for signal_dict in supplemental_signal:
            if signal_dict['code'] not in position_list:
                continue
            if not date:
                date = now

            if signal_dict['date'] <= date:
                continue

            if not signal_dict['price']:
                signal_dict['price'] = 0
            signal_list.append(signal_dict)

        from util.util import DateEncoder
        res = json.dumps(signal_list, indent=2, cls=DateEncoder)

        self.write(res)
