# -*- coding: utf-8 -*-
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