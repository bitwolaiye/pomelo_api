# -*- coding: utf-8 -*-
import os
from tornado import web
from tornado.ioloop import IOLoop
from handlers import DefaultHandler, UploadHandler, PieceHandler, ChannelHandler, \
    ChannelDetailHandler, ChannelPieceListHandler, SelfProfileHandler, UserProfileHandler, \
    RegisterHandler, LoginHandler, CommentHandler, CommentListHandler, PieceLikeHandler, \
    CommentLikeHandler, ChangePasswordHandler, MessageHandler
from settings import app_port, url_pre

__author__ = 'zhouqi'

routs = [
    (r"/api/v1/user/login", LoginHandler),
    (r"/api/v1/user/register", RegisterHandler),
    (r"/api/v1/user/password", ChangePasswordHandler),
    (r"/api/v1/user/([0-9]+)", UserProfileHandler),
    (r"/api/v1/user", SelfProfileHandler),

    (r"/api/v1/channel/([0-9]+)/piece/list", ChannelPieceListHandler),
    (r"/api/v1/channel/([0-9]+)", ChannelDetailHandler),
    (r"/api/v1/channel", ChannelHandler),

    (r"/api/v1/piece/([0-9]+)/comment/list", CommentListHandler),
    (r"/api/v1/piece/([0-9]+)/comment", CommentHandler),
    (r"/api/v1/piece/([0-9]+)/like", PieceLikeHandler),
    (r"/api/v1/piece", PieceHandler),

    (r"/api/v1/message", MessageHandler),

    (r"/api/v1/comment/([0-9]+)/like", CommentLikeHandler),

    (r"/api/v1/upload", UploadHandler),

    (r"/", DefaultHandler),
]

new_routs = []
for r in routs:
    new_routs.append(tuple([url_pre + r[0]] + list(r[1:])))

application = web.Application(new_routs, debug=True)

if __name__ == "__main__":
    with open('.pid', 'w') as f:
        f.write(str(os.getpid()))
    application.listen(app_port)
    IOLoop.instance().start()