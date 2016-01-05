# -*- coding: utf-8 -*-
import logging

import psycopg2
from psycopg2 import extensions

__author__ = 'zhouqi'


class Connection(object):
    def __init__(self, host, database, user=None, password=None, port=None):
        self.host = host
        self.database = database
        args = "dbname=%s" % self.database
        if host is not None:
            args += " host=%s" % host
        if user is not None and len(user) > 0:
            args += " user=%s" % user
        if password is not None and len(password) > 0:
            args += " password=%s" % password
        if port is not None:
            args += " port=%s" % port
        self._db = None
        self._db_args = args
        try:
            self.reconnect()
        except Exception:
            logging.error("Cannot connect to PostgreSQL on %s", self.host,
                          exc_info=True)

    def __enter__(self):
        return self

    def __exit__(self):
        self._db.rollback()

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = psycopg2.connect(self._db_args)

    def _ensure_connected(self):
        # PostgreSQL by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if self._db is None:
            self.reconnect()

        if self._db.closed:
            return self.reconnect()
        else:
            status = self._db.get_transaction_status()
            if status == extensions.TRANSACTION_STATUS_UNKNOWN:
                return self.reconnect()
            elif status != extensions.TRANSACTION_STATUS_IDLE:
                self._db.rollback()
                return self._db
            else:
                return self._db

    def gen_db(self):
        self._ensure_connected()
        return self._db
