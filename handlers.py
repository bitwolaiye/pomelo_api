# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
import json
import os
from apns import APNs, Frame, Payload
from models import format_records_to_json, User, Piece, Channel, Comment
from settings import notification_key_path, notification_cert_path, image_path

__author__ = 'zhouqi'

version = '0.0.1'
version_info = 'pomelo_api: %s' % version

token_dict = {'abc': 1}
token_key = 'Token'


def check_token(func):
    def checker(handler, *args, **kwargs):
        try:
            headers = handler.request.headers
            if token_key in headers and headers[token_key] in token_dict:
                handler.user_id = token_dict[headers[token_key]]
            else:
                handler.user_id = -1
        except:
            handler.user_id = -1
        func(handler, *args, **kwargs)

    return checker


class BaseHandler(RequestHandler):
    user_id = -1


class DefaultHandler(BaseHandler):
    def get(self):
        self.write(dict(version=version_info))

    def post(self):
        self.write(dict(version=version_info))


class LoginHandler(BaseHandler):
    def post(self):
        self.write({'result': True})


class RegisterHandler(BaseHandler):
    def post(self):
        self.write({'result': True})


class UserProfileHandler(BaseHandler):
    def get(self, user_id):
        user = User()
        self.write(user.get_profile(user_id))


class SelfProfileHandler(BaseHandler):
    def get(self):
        user = User()
        self.write(user.get_self_profile(1))

    def post(self):
        self.write({'result': True})


class ChannelHandler(BaseHandler):
    def get(self):
        channel = Channel()
        self.write({'list': channel.list()})

    def post(self):
        self.write({'result': True})


class ChannelDetailHandler(BaseHandler):
    def get(self, channel_id):
        channel = Channel()
        self.write(channel.detail(channel_id))

    def post(self, channel_id):
        self.write({'result': True})


class ChannelPieceListHandler(BaseHandler):
    def get(self, channel_id):
        page = self.get_argument('page', None)
        row_per_page = self.get_argument('row_per_page', None)

        piece = Piece()
        self.write({'list': piece.list(channel_id, page, row_per_page)})


class PieceHandler(BaseHandler):
    @check_token
    def post(self):
        channel_id = self.get_argument('channel_id')
        piece_text = self.get_argument('piece_text')

        piece = Piece()
        piece_id = piece.create(self.user_id, channel_id, piece_text)
        self.write({'piece_id': piece_id})


class CommentHandler(BaseHandler):
    @check_token
    def post(self, piece_id):
        comment_text = self.get_argument('comment_text')

        comment = Comment()
        comment_id = comment.create(self.user_id, piece_id, comment_text)
        self.write({'comment_id': comment_id})


class CommentListHandler(BaseHandler):
    def get(self, piece_id):
        page = self.get_argument('page', None)
        row_per_page = self.get_argument('row_per_page', None)

        comment = Comment()
        self.write({'list': comment.list(piece_id, page, row_per_page)})


class UploadHandler(BaseHandler):
    @check_token
    def post(self):
        f = self.request.files['image'][0]
        self._save_file(f)
        self.write({'result': True})

    def _save_file(self, f):
        p = image_path + '/1'
        if not os.path.exists(p):
            os.mkdir(p)
        with open(p + '/' + f['filename'], 'wb') as up:
            up.write(f['body'])
