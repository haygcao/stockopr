# -*- coding: utf-8 -*-

import os

import tornado.web
import os.path

from .route import handlers


class Application(tornado.web.Application):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        base_dir = base_dir.join('/..')
        settings = {
            "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            "login_url": "/login",
            'template_path': os.path.join(base_dir, "template"),
            'static_path': os.path.join(base_dir, "static"),
            'debug':True,
            # "xsrf_cookies": True,
        }

        tornado.web.Application.__init__(self, handlers, **settings)