# test_blacklist.py

import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.models.blacklist import Blacklist
from src.models.user import User
from src.repository.users import save_black_list_token, find_black_list_token


class TestBlacklist(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

        expected_blacklist = Blacklist(token="test_token", email="test@example.com")
        self.session.query(Blacklist).filter_by(token="test_token").first.return_value = expected_blacklist

    async def test_save_black_list_token(self):
        user = User()
        token = "test_token"
        user.email = "test@example.com"

        await save_black_list_token(token, user, self.session)

        saved_token = self.session.query(Blacklist).filter_by(token=token).first()
        self.assertIsNotNone(saved_token)
        self.assertEqual(saved_token.email, user.email)

    async def test_find_black_list_token_found(self):
        expected_token = "test_token"
        expected_blacklist = Blacklist(token=expected_token, email="test@example.com")
        self.session.query(Blacklist).filter(Blacklist.token == expected_token).first.return_value = expected_blacklist

        result = await find_black_list_token(expected_token, self.session)

        self.assertEqual(result, expected_blacklist)

    async def test_find_black_list_token_not_found(self):
        expected_token = "test_token"
        self.session.query(Blacklist).filter(Blacklist.token == expected_token).first.return_value = None

        result = await find_black_list_token(expected_token, self.session)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main(exit=False)
