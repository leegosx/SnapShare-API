import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from src.schemas.user import UserBase
from src.models.blacklist import Blacklist
from src.models.user import User
from src.repository import users as repository_users
from src.services.auth_service import auth_service

from src.repository.users import (
    get_user_by_email,
    count_users,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
    change_password,
    save_black_list_token,
    find_black_list_token,
    to_ban_user,
    check_ban_status,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(username='Pavlo', email='pavlo_test@gmail.com',
                         password='1234567', avatar=False, role='moderator',
                         refresh_token='old_token', reset_password_token='reset_token',
                         confirmed=False, ban_status=False)

    async def test_get_user_by_email_found(self):
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email=self.user.email, db=self.session)

        self.assertEqual(result, self.user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email=self.user.email, db=self.session)

        self.assertIsNone(result)

    async def test_count_users(self):
        users = [User(), User(), User()]
        self.session.query().all.return_value = users
        result = await count_users(db=self.session)
        self.assertEqual(result, users)

    async def test_create_user(self):
        body = UserBase(
            username='Stefan',
            email='stefan@meta.com.ua',
            password='1234567',
        )
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)

    async def test_update_token_found(self):
        new_token = "new_token"
        await update_token(self.user, new_token, db=self.session)
        self.assertEqual(self.user.refresh_token, new_token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        test_user = self.session.query().filter().first.return_value
        await confirmed_email(email=test_user.email, db=self.session)
        self.assertTrue(test_user.confirmed)

    async def test_update_avatar(self):
        url = 'https://example.com/avatar.jpg'
        self.session.query().return_value = self.user
        update_user = await update_avatar(email=self.user.email, url=url, db=self.session)
        self.assertEqual(update_user.avatar, url)

    async def test_change_password(self):
        new_password = 'new_password'

        update_user = await change_password(self.user, new_password, db=self.session)

        self.assertEqual(update_user.password, new_password)
        self.session.commit.assert_called_once()

    async def test_to_ban_user(self):
        body = UserBase(
            username="Kiril",
            email="kiril@test.com",
            password="test_password", )

        result = await to_ban_user(body=body, email=body.email, db=self.session)
        self.assertTrue(result.ban_status)

    async def test_check_ban_status(self):
        user = self.user
        result = await check_ban_status(username=user.username, db=self.session)
        self.assertTrue(result)

    # async def test_save_black_list_token(self):
    #     token = "test_token"
    #     user = User(email="test@example.com")
    #
    #     await save_black_list_token(token, user, self.session)
    #
    #     saved_token = self.session.query(Blacklist).filter_by(token=token).first()
    #     self.assertIsNotNone(saved_token)
    #     self.assertEqual(saved_token.email, user.email)


if __name__ == '__main__':
    unittest.main()
