# -*- encoding: utf-8 -*-
"""
日志模块
"""
import logging
from logging import handlers


LOG_FILENAME = 'seckill.log'
logger = logging.getLogger()


def set_logger(platfrom):
    """
    记录日志
    """
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('{pf} - %(asctime)s - %(process)d-%(threadName)s - '
                                  '%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'.format(pf=platfrom))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    file_handle = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8"
    )
    file_handle.setFormatter(formatter)
    logger.addHandler(file_handle)


set_logger('京东')


