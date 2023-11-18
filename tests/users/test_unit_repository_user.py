import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user import UserBase

from src.repository.users import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    count_users,
    update_token,
    confirmed_email,
    update_avatar,
    update_user,
    change_password,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.body = UserBase(
            username="TestUser", email="test@test.com", password="qwerty"
        )

    async def test_get_authuser_by_email_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_get_authuser_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertIsNone(result)

    async def test_get_authuser_by_username_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_username(
            username=self.user.username, db=self.session
        )
        self.assertEqual(result, self.user)

    async def test_get_authuser_by_username_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_username(
            username=self.user.username, db=self.session
        )
        self.assertIsNone(result)

    async def test_count_users(self):
        users = [User(), User(), User()]
        self.session.query().all.return_value = users
        result = await count_users(db=self.session)
        self.assertEqual(result, users)

    async def test_create_authuser(self):
        result = await create_user(body=self.body, db=self.session)
        self.assertEqual(result.username, self.body.username)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.password, self.body.password)

    async def test_update_token(self):
        self.session.query().filter().first.return_value = self.user
        token = "token"
        await update_token(user=self.user, token=token, db=self.session)
        self.assertTrue(self.user.refresh_token)
        self.assertEqual(self.user.refresh_token, token)

    async def test_confirmed_email(self):
        self.session.query().filter().first.return_value = self.user
        await confirmed_email(email=self.user.email, db=self.session)
        self.assertTrue(self.user.confirmed)

    async def test_update_avatar(self):
        self.session.query().filter().first.return_value = self.user
        url = "http://localhost.jpeg"
        result = await update_avatar(email=self.user.email, url=url, db=self.session)
        self.assertEqual(result.avatar, url)

    async def test_change_password(self):
        new_password = "new_password"

        update_user = await change_password(self.user, new_password, db=self.session)

        self.assertEqual(update_user.password, new_password)
        self.session.commit.assert_called_once()

    @patch("src.services.auth_service.Auth.redis", create=True)
    async def test_update_user(self, mock_redis):
        mock_redis.set.return_value = True
        self.session.query().filter().first.return_value = self.user

        self.user.username = "UpdatedUser"
        self.user.email = "updated@test.com"
        self.user.password = "newpassword"

        result = await update_user(mock_redis, user=self.user, db=self.session)

        self.assertEqual(result.username, "UpdatedUser")
        self.assertEqual(result.email, "updated@test.com")
        self.assertEqual(result.password, "newpassword")


if __name__ == "__main__":
    unittest.main()
