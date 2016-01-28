# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime
from os import path

import tornado

__author__ = 'zhouqi'

app_port = 8100

db_name = 'pomelo'
db_user = ''
db_port = 5432
db_password = ''
db_host = '127.0.0.1'

url_pre = '/pomelo'

notification_key_path = 'key.pem'
notification_cert_path = 'cert.pem'

image_path = 'images'
log_path = 'log'

settings_fields = ['db_name', 'db_user', 'db_port', 'db_password', 'db_host', 'url_pre',
                   'notification_key_path', 'notification_cert_path', 'image_path']

def load_addition_config():
    try:
        from addition_settings import settings_dict
        for field in settings_fields:
            if field in settings_dict:
                globals()[field] = settings_dict[field]
    except ImportError as ex:
        print(ex)


load_addition_config()

reged_logger = {}


class MyLogFormatter(tornado.log.LogFormatter):
    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


def getLogger(name):
    if not name in reged_logger:
        logpath = path.abspath(path.join(log_path, *name.split('.')))
        if not path.exists(path.dirname(logpath)):
            os.makedirs(path.dirname(logpath))
        from logging import handlers
        handler = handlers.RotatingFileHandler(logpath, maxBytes=10000000, backupCount=10)
        handler.setFormatter(MyLogFormatter(color=False, datefmt='%y-%m-%d %H:%M:%S.%f'))
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        reged_logger[name] = logger
        return logger
    else:
        return reged_logger[name]


access_logger = getLogger('tornado.access')
application_logger = getLogger('tornado.application')
general_logger = getLogger('tornado.general')