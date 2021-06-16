# -*- coding: utf-8 -*-
import json

import tornado.web

from ..component import tradeapi


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
        self.write("Hello, world")


class OrderHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")
        
    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        code = param['code']
        direct = param['direct']
        count = param['count']
        auto = param['auto']

        tradeapi.order(direct, code, count, auto=auto)

        self.write("Hello, world")


class WithdrawHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        direct = param['direct']

        tradeapi.withdraw(direct)

        self.write("Hello, world")


class QueryMoneyHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")
        
    def post(self):
        r = tradeapi.get_asset()
        print(r)
        self.write(r)


class QueryPositionHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")
        
    def post(self):
        param = self.request.body.decode('utf-8')
        print(param)
        param = json.loads(param)
        if 'code' in param and param['code']:
            code = param['code']
        else:
            code = None
            
        position = tradeapi.query_position(code)
        print(position)
        self.write(json.dumps(position))


class QueryOperationDetailHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")
        
    def post(self):
        param = self.request.body.decode('utf-8')
        print(param)
        param = json.loads(param)
        if 'code' in param and param['code']:
            code = param['code']
        else:
            code = None

        detail_list = tradeapi.get_operation_detail(code)
        self.write(json.dumps(detail_list))


class QueryWithdrawOrderHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        order_list = tradeapi.get_order()
        self.write(json.dumps(order_list))
