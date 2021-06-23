config = {
    'monitorInterval': 10,  # auto reload time interval [secs]
    'loggers': {
        'LogDemo': {
            'level': "DEBUG",
            'additivity': False,
            'AppenderRef': ['LogDemo']
        },
        'root': {
            'level': "INFO",
            'AppenderRef': ['output_root']
        }
    },
    'appenders': {
        'output_root': {
            'type': "file",
            'FileName': "log/run.log",  # log file name
            'backup_count': 5,  # files count use backup log
            'file_size_limit': 1024 * 1024 * 20,  # single log file size, default :20MB
            'PatternLayout': "%(asctime)s [%(process)d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s"
        },
        'LogTest': {
            'type': "file",
            'FileName': "log/LogTest.log",
            'PatternLayout': "%(asctime)s [%(process)d][%(levelname)s][%(filename)s:%(lineno)d] %(message)s"
        },
        'console': {
            'type': "console",
            'target': "console",
            'PatternLayout': "[%(levelname)s] %(asctime)s %(message)s"
        }
    }
}
