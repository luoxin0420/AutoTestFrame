#!/usr/bin/env python
# -*- coding:utf-8 -*-


import logging
from logging.handlers import TimedRotatingFileHandler
import threading
from library import configuration
import os

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30
#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class LogSignleton(object):

    def __init__(self, log_config):
        pass

    def __new__(cls, log_config):

        mutex=threading.Lock()
        mutex.acquire() # 上锁，防止多线程下出问题
        if not hasattr(cls, 'instance'):
            cls.instance = super(LogSignleton, cls).__new__(cls)
            config = configuration.configuration()
            config.fileConfig(log_config)
            print os.path.abspath(log_config)
            cls.instance.log_filename = config.getValue('LOGGING', 'log_file')
            cls.instance.max_bytes_each = int(config.getValue('LOGGING', 'max_bytes_each'))
            cls.instance.backup_count = int(config.getValue('LOGGING', 'backup_count'))
            cls.instance.fmt = config.getValue('LOGGING', 'fmt')
            cls.instance.log_level_in_console = int(config.getValue('LOGGING', 'log_level_in_console'))
            cls.instance.log_level_in_logfile = int(config.getValue('LOGGING', 'log_level_in_logfile'))
            cls.instance.logger_name = config.getValue('LOGGING', 'logger_name')
            cls.instance.console_log_on = int(config.getValue('LOGGING', 'console_log_on'))
            cls.instance.logfile_log_on = int(config.getValue('LOGGING', 'logfile_log_on'))
            cls.instance.logger = logging.getLogger(cls.instance.logger_name)
            cls.instance.__config_logger()
        mutex.release()
        return cls.instance

    def get_logger(self):

        return self.logger

    def formatter_message(self, message, use_color = True):
        if use_color:
            message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
        else:
            message = message.replace("$RESET", "").replace("$BOLD", "")
        return message

    def __config_logger(self):

        fmt = self.fmt.replace('|','%')
        formatter = logging.Formatter(fmt)

        if self.console_log_on == 1: # 如果开启控制台日志
            FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
            COLOR_FORMAT = self.formatter_message(FORMAT, True)
            color_formatter = ColoredFormatter(COLOR_FORMAT)
            console = logging.StreamHandler()
            console.setFormatter(color_formatter)
            self.logger.addHandler(console)
            self.logger.setLevel(self.log_level_in_console)

        if self.logfile_log_on == 1: # 如果开启文件日志
            #rt_file_handler = RotatingFileHandler(self.log_filename, maxBytes=self.max_bytes_each, backupCount=self.backup_count)
            rt_file_handler = TimedRotatingFileHandler(self.log_filename, when='D', interval=1, backupCount=self.backup_count)
            rt_file_handler.setFormatter(formatter)
            self.logger.addHandler(rt_file_handler)
            self.logger.setLevel(self.log_level_in_logfile)


class ColoredFormatter(logging.Formatter):

    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)






