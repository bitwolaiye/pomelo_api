# -*- coding: utf-8 -*-
__author__ = 'zhouqi'

app_port = 8000

db_name = 'pomelo'
db_user = ''
db_port = 5432
db_password = ''
db_host = '127.0.0.1'

url_pre = '/item'

notification_key_path = 'key.pem'
notification_cert_path = 'cert.pem'

settings_fields = ['db_name', 'db_user', 'db_port', 'db_password', 'db_host', 'url_pre',
                   'notification_key_path', 'notification_cert_path']
