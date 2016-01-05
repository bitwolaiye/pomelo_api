# -*- coding: utf-8 -*-
import os
from tornado import web
from tornado.ioloop import IOLoop
from handlers import DefaultHandler
from settings import app_port, url_pre

__author__ = 'zhouqi'

routs = [
    (r"/api/v1/user/([0-9]+)/item", UserItemListHandler),
    (r"/api/v1/user/([0-9]+)/item/([0-9]+)", UserItemHandler),
    (r"/api/v1/user/([0-9]+)/item/([0-9]+)/order", UserItemOrderHandler),
    (r"/api/v1/user/([0-9]+)/item/([0-9]+)/order/([0-9]+)", UserItemOrderHandler),
    (r"/api/v1/index/gen/([0-9]+)", IndexGenHandler),
    (r"/api/v1/device/([0-9a-zA-Z]+)/notification", DeviceNotificationHandler),
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