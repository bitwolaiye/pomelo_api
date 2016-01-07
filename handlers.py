# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
import json
from apns import APNs, Frame, Payload
from models import format_records_to_json
from settings import notification_key_path, notification_cert_path

__author__ = 'zhouqi'

version = 'pomelo_api: 0.0.1'


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        pass


class DefaultHandler(BaseHandler):
    def get(self):
        self.write(dict(version=version))

    def post(self):
        self.write(dict(version=version))


class LoginHandler(BaseHandler):
    def post(self):
        self.write({'result': True})


class RegisterHandler(BaseHandler):
    def post(self):
        self.write({'result': True})


class UserProfileHandler(BaseHandler):
    def get(self, user_id):
        self.write({'result': True})


class SelfProfileHandler(BaseHandler):
    def get(self):
        self.write({'result': True})

    def post(self):
        self.write({'result': True})


class ChannelHandler(BaseHandler):
    def post(self):
        self.write({'result': True})

class ChannelDetailHandler(BaseHandler):
    def get(self, channel_id):
        self.write({'result': True})

    def post(self, channel_id):
        self.write({'result': True})

class ChannelPieceListHandler(BaseHandler):
    def get(self, channel_id):
        self.write({'result': True})

class PieceHandler(BaseHandler):
    def post(self):
        self.write({'result': True})

class UploadHandler(BaseHandler):
    def post(self):
        self.write({'result': True})
