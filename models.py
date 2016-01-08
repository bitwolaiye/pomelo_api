# -*- coding: utf-8 -*-
from datetime import datetime, date

from decimal import Decimal

from settings import db_host, db_name, db_password, db_user, db_port
from utils.connection import Connection

__author__ = 'zhouqi'


def ensure_type(obj):
    """
    确保对象能被json序列化
    :param obj: 对象
    :return: 可被json序列化的对象
    """
    if obj.__class__ is datetime:
        return obj.isoformat().split('.')[0] + '.000Z'
    elif obj.__class__ is date:
        return str(obj)
    elif obj.__class__ is Decimal:
        return str(obj)
    else:
        return obj


def format_records_to_json(fields, res, aliases=None):
    """
    format pg records to json obj
    :param fields:query fields
    :param res: pg records
    :param aliases: json field alias
    :return: [{}, ... {}]
    """

    def _to_alias(aliases, i, default):
        if aliases is None or len(aliases) <= i or aliases[i] is None:
            return default
        else:
            return aliases[i]

    result = []
    for row in res:
        result.append(
                dict([(_to_alias(aliases, index, field), ensure_type(row[index]))
                      for index, field in enumerate(fields)]))
    return result


connection = Connection(host=db_host, database=db_name, user=db_user, port=db_port,
                        password=db_password)


class BaseModel(object):
    pass


class User(object):
    profile_fields = ['user_name', 'user_gender']
    self_profile_fields = ['user_name', 'user_gender']

    def login(self, user_id):
        with connection.gen_db() as db:
            cur = db.cursor()
            cur.execute('select * from users where user_id=%s', [user_id])
            cur.fetchall()
        return 'token'

    def register(self):
        user_id = 10000
        return user_id, 'token'

    def get_profile(self, user_id):
        with connection.gen_db() as db:
            cur = db.cursor()
            sql = 'select ' + ', '.join(self.profile_fields) \
                  + ' from users where user_id=%s'
            cur.execute(sql, [user_id])
            res = cur.fetchall()
        return format_records_to_json(self.profile_fields, res)[0]

    def get_self_profile(self, user_id):
        with connection.gen_db() as db:
            cur = db.cursor()
            sql = 'select ' + ', '.join(self.self_profile_fields) \
                  + ' from users where user_id=%s'
            cur.execute(sql, [user_id])
            res = cur.fetchall()
        return format_records_to_json(self.self_profile_fields, res)[0]
