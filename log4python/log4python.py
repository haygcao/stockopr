# -*- coding: utf-8 -*-

import json
import pprint
import traceback
from logging.handlers import SysLogHandler
from os.path import dirname
import time
from datetime import datetime
import os
import sys
import logging
import logging.handlers

__author__ = 'root'
from .observer_model import Observer
from .log_subject import LogSubject


CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

if hasattr(sys, 'frozen'):  # support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)

# Global logger
logSubject = LogSubject()
# logSubject
__all__ = ['set_logger', 'debug', 'info', 'warning', 'error',
           'critical', 'exception']


def dump_var(data):
    if isinstance(data, list):
        ret = []
        for item in data:
            ret.append(json.dumps(item, ensure_ascii=False))
        result_data = "\n".join(ret)
    elif isinstance(data, dict):
        ret = []
        for item in data.keys():
            ret.append(json.dumps(data[item], ensure_ascii=False))
        result_data = "\n".join(ret)
    else:
        result_data = json.dumps(data, ensure_ascii=False)
    return result_data


def func_log(logger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug("FuncName:[%s] is enter" % func.__name__)
            t1 = int(time.time())
            ret = func(*args)
            t2 = (time.time())
            logger.debug("FuncName:[%s] is leaving. use time:[%s] secs" % (func.__name__, (t2 - t1)))
            return ret
        return wrapper
    return decorator


class ColoredFormatter(logging.Formatter):
    """A colorful formatter."""

    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)


g_logger = None
is_py2 = True if sys.version_info.major == 2 else False


def support_print_format(msg, args):
    if not isinstance(msg, str):
        return msg

    n = msg.count('%s')
    len_ = len(args)
    for i in range(0, len_ - n):
        msg += " %s"
    return msg


class Log:
    debugFile = "log4py.debug"
    errorFile = "log4py.error"
    module_name = None
    basePath = ""
    filename = None
    globalsLogSubject = None
    logger = None
    config_all = None
    config_logger = None
    config_appender_list = []
    config_logger_default = {
        'level': 'ERROR',
        'additivity': True,
    }
    config_appender_default = {
        'console': {
            'type': "Console",
            'target': "console",
            'PatternLayout': "[%(levelname)s] %(asctime)s %(message)s"
        }
    }
    level_type = {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'WARN': logging.WARN,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
        }

    def __init__(self, module_name="", filename=None, mode='a', level='ERROR:DEBUG',
        fmt = '[%(levelname)s] %(asctime)s %(message)s',
        backup_count = 5, limit = 1024 * 1024 * 20, when = None):
        """Configure the global logger."""
        global logSubject, g_logger
        Log.globalsLogSubject = logSubject
        self.basePath = Log.globalsLogSubject.basePath
        self.filename = filename

        self.debug_log("Module[%s]: init logger" % module_name)
        self.debug_log("LogBasePath:" + self.basePath)
        LogObserver = Observer(Log.globalsLogSubject)
        LogObserver.update = self.update
        level = level.split(':')

        if len(level) == 1:  # Both set to the same level
            s_level = f_level = level[0]
        else:
            s_level = level[0]  # StreamHandler log level
            f_level = level[1]  # FileHandler log level

        self.config_logger = self.config_logger_default

        self.module_name = module_name
        self.logger = self.init_logger(module_name)
        self.import_log_funcs()
        if module_name != "":
            fmt = ("[module_name:%s], " % module_name) + fmt
        self.update(Log.globalsLogSubject.data)
        self.debug_log("Module[%s]: finish init log file" % self.module_name)

    def debug_log(self, msg):
        if "debug" not in self.globalsLogSubject.data or not self.globalsLogSubject.data['debug']:
            return

        f = open("%s/%s" % (self.basePath, self.debugFile), "a+")
        f.write("module:%s; time:%s; "
                "Msg:%s" % (__name__, datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"), msg+"\r\n"))
        f.close()

    def error_log(self, msg):
        f = open("%s/%s" % (self.basePath, self.errorFile), "a+")
        f.write("module:%s; time:%s; "
                "Msg:%s" % (__name__, datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"), msg+"\r\n"))
        f.close()

    def check_exists(self):
        try:
            if Log.globalsLogSubject.reloadConfig is None or not Log.globalsLogSubject.reloadConfig.check_is_alive():
                Log.globalsLogSubject.restart()
        except:
            error_info = traceback.format_exc()
            self.error_log(error_info)

    # update logger's configuration
    def update(self, data):
        try:
            self.debug_log("Module[%s]: begin update config" % self.module_name)
            level = logging.CRITICAL
            self.config_all = data
            self.update_logger(self.logger.name)
            self.debug_log("Module[%s]: after update config" % self.module_name)
        except Exception as ex:
            self.error_log("Error: %s" % ex)
            self.error_log(traceback.format_exc())

    def update_logger(self, logger_name):
        if "loggers" in self.config_all and logger_name in self.config_all['loggers']:
            self.config_logger = dict(self.config_logger_default, **self.config_all['loggers'][logger_name])
        else:
            if "loggers" in self.config_all and "root" in self.config_all['loggers']:
                self.debug_log("Module[%s]: In the new Configuration "
                               "No Current Module's logger; then use ROOT's Config" % self.module_name)
                self.config_logger = dict(self.config_logger_default, **self.config_all['loggers']["root"])
            else:
                self.debug_log("Module[%s]: In the new Configuration "
                               "No Current Module's logger; "
                               "No ROOT's logger; use the Deault Configuration" % self.module_name)
                self.config_logger = self.config_logger_default

        # get appender
        self.config_appender_list = []
        if "AppenderRef" in self.config_logger:
            appenders = self.config_logger['AppenderRef']
            self.debug_log("LoggerName:[%s]'s appenders: [%s]" % (logger_name,
                                                                  json.dumps(appenders, ensure_ascii=False)))
            for appender_name in appenders:
                if "appenders" in self.config_all and appender_name in self.config_all['appenders']:
                    config_appender = self.config_all['appenders'][appender_name]
                    self.config_appender_list.append(config_appender)
        else:
            self.config_appender_list.append(self.config_appender_default)

        # update logger's parameters
        self.update_logger_config()

    def __get_pop_status(self):
        pop_message = True
        if "additivity" in self.config_logger:
            pop_message = self.config_logger["additivity"]
        return pop_message

    def update_logger_config(self):
        newLogger = self.init_logger(self.module_name)
        newLogger.propagate = self.__get_pop_status()

        self.debug_log("InitLogger:[%s], in update_logger_config" % self.module_name)
        self.debug_log("self.config_appender_list:[%s]" % pprint.pformat(self.config_appender_list))
        # set log's Level
        s_level = self.level_type[self.config_logger['level']]
        # set log's Pattern
        fmt = '[%(levelname)s] %(asctime)s %(message)s'

        # clear old handlers
        self.logger.handlers = []
        newLogger.handlers = []
        for config_appender in self.config_appender_list:
            if "PatternLayout" in config_appender:
                fmt = config_appender['PatternLayout']
            
            log_type = str(config_appender['type']).upper()
            self.debug_log("InitLogger:[%s],Type is [%s]" % (self.module_name, log_type))
            formatter = logging.Formatter(fmt)

            if log_type == 'SYSLOG':
                '''log = logging.getLogger(__name__)
                log.setLevel(logging.DEBUG)
                handler = logging.handlers.SysLogHandler(address = '/dev/log')
                formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
                handler.setFormatter(formatter)
                log.addHandler(handler)'''
                facility_data = 'local1'
                if 'facility' in config_appender:
                    facility_data = config_appender['facility']
                syslog_handler = SysLogHandler(address='/dev/log', facility=facility_data)
                syslog_handler.setLevel(s_level)
                syslog_handler.setFormatter(formatter)
                newLogger.addHandler(syslog_handler)

            if log_type == "FILE":
                filename = self.filename if self.filename else config_appender['FileName']
                backup_count = 5
                limit = 1024 * 1024 * 20

                if "backup_count" in config_appender:
                    backup_count = int(config_appender['backup_count'])
                if "file_size_limit" in config_appender:
                    limit = int(config_appender['file_size_limit'])

                log_path = ""
                if sys.platform == "win32":
                    filename = filename.replace("/", "\\")
                    if filename[1] == ":":
                        log_path = os.path.dirname(filename)
                    else:
                        log_path = dirname(os.path.join(self.basePath, filename))
                        filename = os.path.join(self.basePath, filename)
                else:
                    filename = filename.replace("\\", "/")
                    if filename[0] == "/":
                        log_path = os.path.dirname(filename)
                    else:
                        log_path = dirname(os.path.join(self.basePath, filename))
                        filename = os.path.join(self.basePath, filename)

                if not os.path.exists(log_path):
                    os.makedirs(log_path)
                self.debug_log("Module[%s]: init log file[%s]" % (self.module_name, filename))
                mode = 'a'
                
                when = None
                # set log's appender
                self.add_file_handler(newLogger, s_level, fmt, filename, mode, backup_count, limit, when)

            if log_type == "CONSOLE":
                self.add_stream_handler(newLogger, s_level, fmt)

        # set the New Logger
        self.logger = newLogger

    def add_handler(self, logger, cls, level, fmt, colorful, **kwargs):
        """Add a configured handler to the global logger."""

        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.DEBUG)

        handler = cls(**kwargs)
        handler.setLevel(level)

        if colorful:
            formatter = ColoredFormatter(fmt)
        else:
            formatter = logging.Formatter(fmt)

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.debug_log("Module[%s]: Handlers count:[%s]" % (self.module_name, str(len(logger.handlers))))

        return handler

    def add_stream_handler(self, logger, level, fmt):
        """Add a stream handler to the global logger."""
        return self.add_handler(logger, logging.StreamHandler, level, fmt, True)

    def add_file_handler(self, logger, level, fmt, filename, mode, backup_count, limit, when):
        """Add a file handler to the global logger."""
        kwargs = {'encoding': 'utf-8'}

        # If the filename is not set, use the default filename
        if filename is None:
            filename = getattr(sys.modules['__main__'], '__file__', 'log.py')
            filename = os.path.basename(filename.replace('.py', '.log'))

        kwargs['filename'] = filename

        # Choose the filehandler based on the passed arguments
        if backup_count == 0:  # Use FileHandler
            cls = logging.FileHandler
            kwargs['mode'] = mode
        elif when is None:  # Use RotatingFileHandler
            cls = logging.handlers.RotatingFileHandler
            kwargs['maxBytes'] = limit
            kwargs['backupCount'] = backup_count
            kwargs['mode'] = mode
        else:  # Use TimedRotatingFileHandler
            cls = logging.handlers.TimedRotatingFileHandler
            kwargs['when'] = when
            kwargs['interval'] = limit
            kwargs['backupCount'] = backup_count

        return self.add_handler(logger, cls, level, fmt, False, **kwargs)

    @staticmethod
    def init_logger(module):
        """Reload the global logger."""
        logger = None
        if module == "":
            logger = logging.getLogger()
        else:
            logger = logging.getLogger(module)

        logger.setLevel(logging.DEBUG)
        return logger

    def set_logger(self, module_name="", filename=None, mode='a', level='ERROR:DEBUG',
                   fmt='[%(levelname)s] %(asctime)s %(message)s',
                   backup_count=5, limit=20480, when=None):
        """Configure the global logger."""
        level = level.split(':')

        if len(level) == 1:  # Both set to the same level
            s_level = f_level = level[0]
        else:
            s_level = level[0]  # StreamHandler log level
            f_level = level[1]  # FileHandler log level

        self.logger = self.init_logger(module_name)
        if module_name != "":
            fmt = ("[module_name:%s], " % module_name) + fmt
        self.add_stream_handler(self.logger, s_level, fmt)
        self.add_file_handler(self.logger, f_level, fmt, filename, mode, backup_count, limit, when)

    def import_log_funcs(self):
        """Import the common log functions from the self.logger to the module."""
        # curr_mod = sys.modules[__name__]
        log_funcs = ['isEnabledFor', '_log', 'findCaller', 'makeRecord', 'handle']

        for func_name in log_funcs:
            func = getattr(self.logger, func_name)
            setattr(self, func_name, func)

    def critical(self, msg, *args, **kwargs):
        try:
            msg = support_print_format(msg, args)
            self.check_exists()
            if self.isEnabledFor(CRITICAL):
                self._log(CRITICAL, msg, args, **kwargs)
            if is_py2 and self.config_logger['additivity'] and self.logger.name != 'root':
                record = self.getRecord(CRITICAL, msg, args, **kwargs)
                g_logger.handleRecord(CRITICAL, record)
        except Exception as ex:
            self.error_log("critical:Module[%s]: %s" % (self.module_name, ex))

    def error(self, msg, *args, **kwargs):
        try:
            msg = support_print_format(msg, args)
            self.check_exists()
            if self.isEnabledFor(ERROR):
                self._log(ERROR, msg, args, **kwargs)
            if is_py2 and self.config_logger['additivity'] and self.logger.name != 'root':
                record = self.getRecord(ERROR, msg, args, **kwargs)
                g_logger.handleRecord(CRITICAL, record)
        except Exception as ex:
            self.error_log("error:Module[%s]: %s" % (self.module_name, ex))

    def warning(self, msg, *args, **kwargs):
        try:
            msg = support_print_format(msg, args)
            self.check_exists()
            if self.isEnabledFor(WARNING):
                self._log(WARNING, msg, args, **kwargs)
            if is_py2 and self.config_logger['additivity'] and self.logger.name != 'root':
                record = self.getRecord(WARNING, msg, args, **kwargs)
                g_logger.handleRecord(CRITICAL, record)
        except Exception as ex:
            self.error_log("warning:Module[%s]: %s" % (self.module_name, ex))

    def info(self, msg, *args, **kwargs):
        try:
            msg = support_print_format(msg, args)
            self.check_exists()
            if self.isEnabledFor(INFO):
                self._log(INFO, msg, args, **kwargs)
            if is_py2 and self.config_logger['additivity'] and self.logger.name != 'root':
                record = self.getRecord(INFO, msg, args, **kwargs)
                g_logger.handleRecord(CRITICAL, record)
        except Exception as ex:
            self.error_log("info:Module[%s]: %s" % (self.module_name, ex))

    def debug(self, msg, *args, **kwargs):
        try:
            msg = support_print_format(msg, args)
            self.check_exists()
            if self.isEnabledFor(DEBUG):
                self._log(DEBUG, msg, args, **kwargs)
            if is_py2 and self.config_logger['additivity'] and self.logger.name != 'root':
                record = self.getRecord(DEBUG, msg, args, **kwargs)
                g_logger.handleRecord(CRITICAL, record)
        except Exception as ex:
            self.error_log("debug:Module[%s]: %s" % (self.module_name, ex))

    def getRecord(self, level, msg, args, exc_info=None, extra=None):
        self.debug_log("[additivity is True] ModuleName[%s]: Msg[%s]" % (self.module_name, msg))
        if _srcfile:
            #IronPython doesn't track Python frames, so findCaller raises an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            try:
                fn, lno, func = self.findCaller()
            except ValueError:
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.logger.name, level, fn, lno, msg, args, exc_info, func, extra)

        return record

    def handleRecord(self, level, record):
        if self.isEnabledFor(level):
            self.handle(record)


if g_logger is None:
    g_logger = Log("root")
