# -*- coding: utf-8 -*-
import unittest

from models import Token

__author__ = 'zhouqi'


class TestToken(unittest.TestCase):
    def setUp(self):
        Token(test=1).clean_db()

    def test_login_normal(self):
        user_id, device_id = 1, 0
        token = Token()
        token_key = token.update(user_id, device_id)
        self.assertEqual((user_id, device_id), token.get_user(token_key))

        self.assertNotEqual(token.update(2, 0), token.update(3, 0))

        new_token_key = token.update(user_id, device_id)
        self.assertEqual((-1, -1), token.get_user(token_key))
        self.assertEqual((user_id, device_id), token.get_user(new_token_key))




if __name__ == '__main__':
    unittest.main()
