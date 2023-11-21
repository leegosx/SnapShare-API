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
        """
        The test_save_black_list_token function tests the save_black_list_token function.
        It creates a user and token, then saves them to the database using save_black_list_token.
        Then it queries for that token in the database and asserts that it exists.

        :param self: Access the class attributes and methods
        :return: The token and user
        :doc-author: Trelent
        """
        user = User()
        token = "test_token"
        user.email = "test@example.com"

        await save_black_list_token(token, user, self.session)

        saved_token = self.session.query(Blacklist).filter_by(token=token).first()
        self.assertIsNotNone(saved_token)
        self.assertEqual(saved_token.email, user.email)

    async def test_find_black_list_token_found(self):
        """
        The test_find_black_list_token_found function tests the find_black_list_token function.
            The test is successful if the expected token is returned.

        :param self: Represent the instance of the class
        :return: The expected_blacklist
        :doc-author: Trelent
        """
        expected_token = "test_token"
        expected_blacklist = Blacklist(token=expected_token, email="test@example.com")
        self.session.query(Blacklist).filter(Blacklist.token == expected_token).first.return_value = expected_blacklist

        result = await find_black_list_token(expected_token, self.session)

        self.assertEqual(result, expected_blacklist)

    async def test_find_black_list_token_not_found(self):
        """
        The test_find_black_list_token_not_found function tests the find_black_list_token function.
        The test is successful if the result of calling find_black_list token with a token that does not exist in the database
        is None.

        :param self: Represent the instance of the class
        :return: None
        :doc-author: Trelent
        """
        expected_token = "test_token"
        self.session.query(Blacklist).filter(Blacklist.token == expected_token).first.return_value = None

        result = await find_black_list_token(expected_token, self.session)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main(exit=False)
