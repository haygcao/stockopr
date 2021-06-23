# -*- coding: utf-8 -*-
import pprint
import traceback

__author__ = 'root'
import logging
import os
import sys
import threading
import time
from datetime import datetime

from .observer_model import Subject
from .modules_dynamic_load import ModulesDynamicLoad


class ThreadReloadConfig(threading.Thread):
    LogSubjectObj = None

    @staticmethod
    def __debug_log(msg):
        print("module:%s; time:%s; Msg:%s" % (__name__,
                                              datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"),
                                              msg+"\r\n"))

    def __init__(self, log_subject_object):
        self.errorFile = "log4pythoh_err.log"
        self.__is_py2 = True if sys.version_info.major == 2 else False
        threading.Thread.__init__(self, name="ThreadReloadConfig")
        self.LogSubjectObj = log_subject_object

    def check_is_alive(self):
        if self.__is_py2:
            return self.isAlive()
        else:
            return self.is_alive()

    @staticmethod
    def var_dump(obj):
        import pprint
        output = pprint.saferepr(obj)
        return output

    def error_log(self, msg):
        f = open("%s/%s" % (self.LogSubjectObj.basePath, self.errorFile), "a+")
        f.write("module:%s; time:%s;"
                " Msg:%s" % (__name__, datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"), msg+"\r\n"))
        f.close()

    def run(self):
        while True:
            try:
                # reload new log config
                self.LogSubjectObj.load_config()

                # notification all observers
                self.LogSubjectObj.notify_observers()

                time_sleep = 5
                if int(self.LogSubjectObj.data['monitorInterval']) > 5:
                    time_sleep = int(self.LogSubjectObj.data['monitorInterval'])
                time.sleep(time_sleep)
            except Exception as ex:
                self.error_log("SubjectConfiguration: %s" % pprint.pformat(self.LogSubjectObj.configuration))
                self.error_log("critical: %s" % ex)
                self.error_log("TrackInfo: %s" % traceback.format_exc())


class LogSubject(Subject):
    debugFile = "log4py.debug"
    reloadConfig = None
    daemonFlag = True
    timer_log = 0
    timer_interval = 3
    configuration = None
    time_load_config = 0
    configurationFile = "log4p.py"
    basePath = ""
    t1 = 0
    config_all_default = {
        'debug': False,
        'monitorInterval': 5,
        'loggers': {
            'root': {
                'level': "ERROR",
                'additivity': False,
                'AppenderRef': 'console'
            }
        },
        'appenders': {
            'console': {
                'type': "console",
                'target': "console",
                'PatternLayout': "[%(levelname)s] %(asctime)s %(message)s"
            }
        }
    }

    @staticmethod
    def __get_script_dir():
        return os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        super(LogSubject, self).__init__()
        self.basePath = os.path.split(os.path.realpath(sys.argv[0]))[0]
        self.basePath = os.getcwd()
        self.__config_file_path = os.path.join(self.basePath, self.configurationFile)
        self.module_loader = ModulesDynamicLoad()
        self.__init_config = {
            'monitorInterval': 60,
            'loggers': {
                'root': {
                    'level': "DEBUG",
                    'additivity': False,
                    'AppenderRef': ['default']
                }
            },

            'appenders': {
                'console': {
                    'type': "console",
                    'target': "console",
                    'PatternLayout': "%(asctime)s [%(process)d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s"
                },
                'default': {
                    'type': "file",
                    'FileName': "logs/default.log",
                    'PatternLayout': "%(asctime)s [%(process)d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s"
                }
            }
        }
        self.data = {}
        self.start()
        self.debug_log("Finish Start logger thread...")

    def debug_log(self, msg):
        if ("debug" not in self.data) or self.data['debug'] is False:
            return
        f = open(os.path.join(self.basePath, self.debugFile), "a+")
        f.write("module:%s; time:%s; Msg:%s" % (__name__,
                                                datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"),
                                                msg+"\r\n"))
        f.close()

    def restart(self):
        self.debug_log("Enter to Restart")
        self.reloadConfig = ThreadReloadConfig(self)
        self.reloadConfig.setDaemon(True)
        self.reloadConfig.start()
        self.debug_log("Leave to Restart")

    def check_config_exists(self):
        is_exists = False
        if os.path.exists(self.__config_file_path):
            is_exists = True
        return is_exists

    def load_config(self):
        load_success = False
        if self.check_config_exists():
            if self.configuration is None:
                self.configuration = self.module_loader.load(self.__config_file_path)
                self.data = dict(self.config_all_default, **self.configuration.config)
            else:
                self.configuration = self.module_loader.reload(self.configuration)
                self.data = dict(self.config_all_default, **self.configuration.config)
                self.notify_observers()
            load_success = True
        return load_success

    def start(self):
        if self.check_config_exists():
            self.load_config()
            self.reloadConfig = ThreadReloadConfig(self)
            self.reloadConfig.setDaemon(True)
            self.reloadConfig.start()
        else:
            self.debug_log("Configuration File Not Found[%s]!! Use default Configuration..." % self.__config_file_path)
            self.data = self.__init_config

    @staticmethod
    def update_root():
        g_logger = logging.getLogger("root")


if __name__ == '__main__':
    log = LogSubject()
    log.start()
