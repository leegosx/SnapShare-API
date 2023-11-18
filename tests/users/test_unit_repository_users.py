# import unittest
# from unittest.mock import MagicMock

# from sqlalchemy.orm import Session
# from src.schemas.user import UserBase
# from src.models.user import User

# from src.repository.users import (
#     get_user_by_email,
#     count_users,
#     create_user,
#     update_token,
#     confirmed_email,
#     update_avatar,
#     change_password,
# )


# class TestUsers(unittest.IsolatedAsyncioTestCase):

#     def setUp(self):
#         self.session = MagicMock(spec=Session)
#         self.user = User(username='Pavlo', email='pavlo_test@gmail.com',
#                          password='1234567', avatar=False,  role='moderator',
#                          refresh_token='old_token', confirmed=False)

#     async def test_get_user_by_email_found(self):
#         self.session.query().filter().first.return_value = self.user
#         result = await get_user_by_email(email=self.user.email, db=self.session)

#         self.assertEqual(result, self.user)

#     async def test_get_user_by_email_not_found(self):
#         self.session.query().filter().first.return_value = None
#         result = await get_user_by_email(email=self.user.email, db=self.session)

#         self.assertIsNone(result)

#     async def test_count_users(self):
#         users = [User(), User(), User()]
#         self.session.query().all.return_value = users
#         result = await count_users(db=self.session)
#         self.assertEqual(result, users)

#     async def test_create_user(self):
#         body = UserBase(
#             username='Stefan',
#             email='stefan@meta.com.ua',
#             password='1234567',
#         )
#         result = await create_user(body=body, db=self.session)
#         self.assertEqual(result.username, body.username)
#         self.assertEqual(result.email, body.email)
#         self.assertEqual(result.password, body.password)

#     async def test_update_token_found(self):
#         new_token = "new_token"
#         await update_token(self.user, new_token, db=self.session)
#         self.assertEqual(self.user.refresh_token, new_token)
#         self.session.commit.assert_called_once()

#     async def test_confirmed_email(self):
#         self.session.query().return_value = self.user
#         await confirmed_email(email=self.user.email, db=self.session)
#         self.assertTrue(self.user.email)

#     async def test_update_avatar(self):
#         url = 'https://example.com/avatar.jpg'
#         self.session.query().return_value = self.user
#         update_user = await update_avatar(email=self.user.email, url=url, db=self.session)
#         self.assertEqual(update_user.avatar, url)

#     async def test_change_password(self):
#         new_password = 'new_password'

#         update_user = await change_password(self.user, new_password, db=self.session)

#         self.assertEqual(update_user.password, new_password)
#         self.session.commit.assert_called_once()


# if __name__ == '__main__':
#     unittest.main()
