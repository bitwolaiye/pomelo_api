# -*- coding: utf-8 -*-
import hashlib
import os
import random
import shutil
from datetime import datetime, date

from decimal import Decimal

import rocksdb
import struct

from PIL import Image

from settings import db_host, db_name, db_password, db_user, db_port, image_path
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
    profile_fields = ['user_name', 'user_gender', 'user_avatar']
    self_profile_fields = ['user_name', 'user_gender', 'user_avatar']

    def get_user_id_from_name(self, user_name):
        with connection.gen_db() as db:
            cur = db.cursor()
            cur.execute('select user_id from users where user_name=%s', [user_name])
            res = cur.fetchall()
            if len(res) == 1:
                return res[0][0]
            else:
                return -1

    def login(self, user_id, user_password):
        with connection.gen_db() as db:
            cur = db.cursor()
            cur.execute('select user_password from users where user_id=%s', [user_id])
            res = cur.fetchall()
        password = res[0][0]
        if self.check_password(password, user_password):
            token = Token().update(user_id, 0)
            return token
        else:
            return None

    def check_password(self, password, input_password):
        if password is None or input_password is None:
            return False
        if len(password) == 1 and password == '!':
            return False
        if len(password) == 2 and password == '!!':
            return True
        array = password.split('$')
        if len(array) != 3:
            return False
        hash_method = array[0]
        salt = array[1]
        hashed = array[2]
        h = hashlib.new(hash_method)
        h.update(salt)
        h.update(input_password)
        return h.hexdigest() == hashed

    def gen_password(self, input_password):
        hash_method = 'sha1'
        salt = hex(random.randint(0,16777216))[2:]
        h = hashlib.new(hash_method)
        h.update(salt)
        h.update(input_password)
        return '$'.join([hash_method, salt, h.hexdigest()])

    def register(self, user_name, user_password):
        with connection.gen_db() as db:
            cur = db.cursor()
            cur.execute(
                'insert INTO users(user_name, nick_name, user_password) VALUES (%s, %s, %s) RETURNING user_id;',
                [user_name, user_name, self.gen_password(user_password)])
            res = cur.fetchall()
            user_id = res[0][0]
            db.commit()
        token = Token().update(user_id, 0)
        return user_id, token

    def change_password(self, user_id, user_password, new_password):
        with connection.gen_db() as db:
            cur = db.cursor()
            cur.execute('select user_password from users where user_id=%s', [user_id])
            res = cur.fetchall()
            password = res[0][0]
            if self.check_password(password, user_password):
                cur.execute('update users set user_password=%s WHERE user_id=%s;',
                            [self.gen_password(new_password), user_id])
                db.commit()
                return True
            else:
                return False

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

    def update_profile(self, user_id, user_name=None, user_password=None, user_gender=None, user_avatar=None):
        if user_avatar is not None:
            pre = user_avatar.split('.')[-2][-3:]
            src_path = '/'.join([image_path, 'tmp', pre, user_avatar])
            if os.path.exists(src_path):
                dst_path = '/'.join([image_path, 'avatar', 'origin', pre, user_avatar])
                thumb_path = '/'.join([image_path, 'avatar', 'thumb', pre, user_avatar])
                for p in [dst_path, thumb_path]:
                    sub = p.split('/')
                    for i in xrange(len(sub) - 1):
                        sub_p = '/'.join(sub[:i + 1])
                        if not os.path.exists(sub_p):
                            os.mkdir(sub_p)
                # shutil.move(src_path, dst_path)
                image = Image.open(src_path)
                origin_size = image.size
                if origin_size[0] > origin_size[1]:
                    delta = (origin_size[0] - origin_size[1]) /2
                    image = image.crop((delta, 0, origin_size[0] - delta, origin_size[1]))
                elif origin_size[0] < origin_size[1]:
                    delta = (origin_size[1] - origin_size[0]) /2
                    image = image.crop((0, delta, origin_size[0], origin_size[1] - delta))
                if origin_size[0] > 612:
                    height = origin_size[1] * 1.0 / origin_size[0] * 612
                    width = 612
                    image.thumbnail((width, height))
                image.save(dst_path)
                os.remove(src_path)
                origin_size = image.size
                width, height = origin_size
                if origin_size[0] > 150:
                    height = origin_size[1] * 1.0 / origin_size[0] * 150
                    width = 150
                    image.thumbnail((width, height))
                image.save(thumb_path, 'JPEG')
                sql = 'update users set user_avatar=%s where user_id=%s;'
                with connection.gen_db() as db:
                    cur = db.cursor()
                    cur.execute(sql, [user_avatar, user_id])
                    db.commit()
        return True


class Channel(object):
    chance_detail_fields = ['channel_id', 'channel_name', 'channel_avatar', 'channel_user_id', 'user_name',
                            'user_gender', 'user_avatar']
    chance_detail_sql_fields = format_sql_fields(chance_detail_fields, [(0, 3), (4, 6)])

    chance_list_fields = ['channel_id', 'channel_name', 'channel_avatar', 'channel_user_id', 'user_name',
                            'user_gender', 'user_avatar']
    chance_list_sql_fields = format_sql_fields(chance_list_fields, [(0, 3), (4, 6)])

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
    piece_list_fields = ['piece_id', 'piece_text', 'piece_time', 'comment_cnt', 'like_cnt', 'user_id', 'user_name', 'user_gender', 'user_avatar']
    piece_list_sql_fields = format_sql_fields(piece_list_fields, [(0, 5), (6, 8)])

    def create(self, user_id, channel_id, piece_text, piece_pic=None, piece_voice=None,
               piece_video=None):
        user_id = int(user_id)
        channel_id = int(channel_id)

        with connection.gen_db() as db:
            cur = db.cursor()
            sql = "insert into pieces(channel_id, user_id, piece_text, piece_time) VALUES (%s, %s, %s, now() AT TIME ZONE 'UTC-0') RETURNING piece_id;"
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


class Comment(object):
    comment_list_fields = ['comment_id', 'comment_text', 'comment_time', 'like_cnt', 'user_id', 'user_name', 'user_gender', 'user_avatar']
    comment_list_sql_fields = format_sql_fields(comment_list_fields, [(0, 4), (5, 7)])

    def create(self, user_id, piece_id, comment_text, comment_pic=None, comment_voice=None,
               comment_video=None):
        user_id = int(user_id)
        piece_id = int(piece_id)

        with connection.gen_db() as db:
            cur = db.cursor()
            sql = "insert into comments(piece_id, user_id, comment_text, comment_time) VALUES (%s, %s, %s, now() AT TIME ZONE 'UTC-0') RETURNING comment_id;"
            cur.execute(sql, (piece_id, user_id, comment_text))
            sql = 'update pieces SET comment_cnt=comment_cnt+1 WHERE piece_id=%s;'
            cur.execute(sql, (piece_id, ))
            return cur.fetchone()[0]

    def list(self, piece_id, page=None, row_per_page=None):
        if page is None: page = 1
        if row_per_page is None: row_per_page = 20

        piece_id = int(piece_id)
        page = int(page)
        row_per_page = int(row_per_page)

        with connection.gen_db() as db:
            cur = db.cursor()
            sql = 'select ' + ', '.join(self.comment_list_sql_fields(['a', 'b'])) + \
                  ' from comments a, users b where a.user_id=b.user_id and piece_id=%s ' \
                  ' order by comment_id desc LIMIT %s OFFSET %s;'
            cur.execute(sql, [piece_id, row_per_page, (page - 1) * row_per_page])
            res = cur.fetchall()
        return format_records_to_json(self.comment_list_fields, res)


class PieceLike(object):
    def like(self, piece_id, user_id, status=1):
        if status not in [1, -1]:
            return False
        with connection.gen_db() as db:
            cur = db.cursor()
            res = cur.execute('select status from piece_likes WHERE piece_id=%s and user_id=%s;', [piece_id, user_id]).fetchall()
            if len(res) == 1:
                cur_status = res[0][1]
                if status == cur_status:
                    pass
                else:
                    if status == 1:
                        cur.execute('update piece_likes set status=%s WHERE piece_id=%s and user_id=%s;', [status, piece_id, user_id])
                        cur.execute('update pieces set like_cnt=like_cnt+1 WHERE piece_id=%s', [piece_id])
                    else:
                        cur.execute('update piece_likes set status=%s WHERE piece_id=%s and user_id=%s;', [status, piece_id, user_id])
                        cur.execute('update pieces set like_cnt=like_cnt-1 WHERE piece_id=%s', [piece_id])
            else:
                if status == 1:
                    cur.execute('insert INTO piece_likes(piece_id, user_id, status) VALUES (%s, %s, %s);', [piece_id, user_id, status])
                    cur.execute('update pieces set like_cnt=like_cnt+1 WHERE piece_id=%s', [piece_id])
            db.commit()
        return True


class CommentLike(object):
    def like(self, comment_id, user_id, status=1):
        if status not in [1, -1]:
            return False
        with connection.gen_db() as db:
            cur = db.cursor()
            res = cur.execute('select status from comment_likes WHERE comment_id=%s and user_id=%s;', [comment_id, user_id]).fetchall()
            if len(res) == 1:
                cur_status = res[0][1]
                if status == cur_status:
                    pass
                else:
                    if status == 1:
                        cur.execute('update comment_likes set status=%s WHERE comment_id=%s and user_id=%s;', [status, comment_id, user_id])
                        cur.execute('update comments set like_cnt=like_cnt+1 WHERE comment_id=%s', [comment_id])
                    else:
                        cur.execute('update comment_likes set status=%s WHERE comment_id=%s and user_id=%s;', [status, comment_id, user_id])
                        cur.execute('update comments set like_cnt=like_cnt-1 WHERE comment_id=%s', [comment_id])
            else:
                if status == 1:
                    cur.execute('insert INTO comment_likes(comment_id, user_id, status) VALUES (%s, %s, %s);', [comment_id, user_id, status])
                    cur.execute('update comments set like_cnt=like_cnt+1 WHERE comment_id=%s', [comment_id])
            db.commit()
        return True


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Token():
    __metaclass__ = Singleton
    db_file = 'db/data/token.db'
    test_db_file = 'db/data/test_token.db'
    test_flag = False
    _token_key_pre = b't'
    _user_key_pre = b'u'

    def __init__(self, *args, **kwargs):
        if 'test' in kwargs:
            Token.test_flag = True
            self.db = rocksdb.DB(Token.test_db_file, rocksdb.Options(create_if_missing=True))
        else:
            self.db = rocksdb.DB(Token.db_file, rocksdb.Options(create_if_missing=True))

    def clean_db(self):
        if Token.test_flag:
            self.db = None
            shutil.rmtree(self.test_db_file)
            self.db = rocksdb.DB(Token.test_db_file, rocksdb.Options(create_if_missing=True))

    def get_user(self, token):
        num = base62_decode(token)
        r = self.db.get(self._token_key_pre + struct.pack('<Q', num))
        if r is not None:
            return struct.unpack('<Q', r[:8])[0], struct.unpack('<Q', r[8:16])[0]
        else:
            return -1, -1

    def get_number(self, user_id, device_id):
        key = struct.pack('<Q', user_id) + struct.pack('<Q', device_id)
        return struct.unpack('<Q', self.db.get(self._user_key_pre + key))[0]

    def exists(self, user_id, device_id):
        return self.db.get(self._user_key_pre + struct.pack('<Q', user_id) + struct.pack('<Q', device_id)) is not None

    def exists_number(self, num):
        return self.db.get(self._token_key_pre + struct.pack('<Q', num)) is not None

    def gen_number(self, user_id, device_id):
        if self.exists(user_id, device_id):
            pass
        ran = random.randint(0, 1<<64-1)
        while self.exists_number(ran):
            ran = random.randint(0, 1<<64-1)
        return ran

    def update(self, user_id, device_id):
        if self.exists(user_id, device_id):
            num = self.get_number(user_id, device_id)
            self.db.delete(self._token_key_pre + struct.pack('<Q', num))
            self.db.delete(self._user_key_pre + struct.pack('<Q', user_id) + struct.pack('<Q', device_id))
        num = self.gen_number(user_id, device_id)
        self.db.put(self._token_key_pre + struct.pack('<Q', num), struct.pack('<Q', user_id) + struct.pack('<Q', device_id))
        self.db.put(self._user_key_pre + struct.pack('<Q', user_id) + struct.pack('<Q', device_id), struct.pack('<Q', num))
        return base62_encode(num)


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num


