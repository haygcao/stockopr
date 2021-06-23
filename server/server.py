import tornado.ioloop
import tornado.options
from tornado.options import define, options

from .application.application import Application
from .config import port

define("port", default=port, help="run on the given port", type=int)


def run():
    tornado.options.parse_command_line()
    Application().listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
