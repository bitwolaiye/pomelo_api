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


def format_sql_fields(l, sections):
    def format(obj, table_names):
        return reduce(lambda x, y: x + y,
                      [['.'.join([table_names[i], each]) for each in l[s:e + 1]] for i, (s, e) in
                       enumerate(sections)], [])

    return format


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


class Channel(object):
    chance_detail_fields = ['channel_id', 'channel_name', 'channel_user_id', 'user_name',
                            'user_gender']
    chance_detail_sql_fields = format_sql_fields(chance_detail_fields, [(0, 2), (3, 4)])

    chance_list_fields = ['channel_id', 'channel_name', 'channel_user_id', 'user_name',
                            'user_gender']
    chance_list_sql_fields = format_sql_fields(chance_list_fields, [(0, 2), (3, 4)])

    def detail(self, channel_id):
        channel_id = int(channel_id)

        with connection.gen_db() as  db:
            cur = db.cursor()
            sql = 'select ' + ', '.join(self.chance_detail_sql_fields(['a', 'b'])) + \
                  ' FROM channels a,users b where a.channel_user_id=b.user_id and channel_id=%s'
            cur.execute(sql, [channel_id])
            res = cur.fetchall()
        return format_records_to_json(self.chance_detail_fields, res)[0]

    def list(self):
        with connection.gen_db() as  db:
            cur = db.cursor()
            sql = 'select ' + ', '.join(self.chance_detail_sql_fields(['a', 'b'])) + \
                  ' FROM channels a,users b where a.channel_user_id=b.user_id'
            cur.execute(sql)
            res = cur.fetchall()
        return format_records_to_json(self.chance_detail_fields, res)


class Piece(object):
    piece_list_fields = ['piece_id', 'piece_text', 'user_id', 'user_name', 'user_gender']
    piece_list_sql_fields = format_sql_fields(piece_list_fields, [(0, 2), (3, 4)])

    def create(self, user_id, channel_id, piece_text, piece_pic=None, piece_voice=None,
               piece_video=None):
        user_id = int(user_id)
        channel_id = int(channel_id)

        with connection.gen_db() as db:
            cur = db.cursor()
            sql = 'insert into pieces(channel_id, user_id, piece_text, piece_time) VALUES (%s, %s, %s, now()) RETURNING piece_id;'
            cur.execute(sql, (channel_id, user_id, piece_text))
            return cur.fetchone()[0]

    def list(self, channel_id, page=None, row_per_page=None):
        if page is None: page = 1
        if row_per_page is None: row_per_page = 20

        channel_id = int(channel_id)
        page = int(page)
        row_per_page = int(row_per_page)

        with connection.gen_db() as db:
            cur = db.cursor()
            sql = 'select ' + ', '.join(self.piece_list_sql_fields(['a', 'b'])) + \
                  ' from pieces a, users b where a.user_id=b.user_id and channel_id=%s ' \
                  ' order by piece_id desc LIMIT %s OFFSET %s;'
            cur.execute(sql, [channel_id, row_per_page, (page - 1) * row_per_page])
            res = cur.fetchall()
        return format_records_to_json(self.piece_list_fields, res)
