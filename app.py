# -*- coding: utf-8 -*-
import os
from tornado import web
from tornado.ioloop import IOLoop
from handlers import DefaultHandler, UploadHandler, PieceHandler, ChannelHandler, \
    ChannelDetailHandler, ChannelPieceListHandler, SelfProfileHandler, UserProfileHandler, \
    RegisterHandler, LoginHandler
from settings import app_port, url_pre

__author__ = 'zhouqi'

routs = [
    (r"/api/v1/user/login", LoginHandler),
    (r"/api/v1/user/register", RegisterHandler),
    (r"/api/v1/user/([0-9]+)/profile", UserProfileHandler),
    (r"/api/v1/user/profile", SelfProfileHandler),

    (r"/api/v1/channel/([0-9]+)/piece/list", ChannelPieceListHandler),
    (r"/api/v1/channel/([0-9]+)", ChannelDetailHandler),
    (r"/api/v1/channel", ChannelHandler),

    (r"/api/v1/piece", PieceHandler),

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