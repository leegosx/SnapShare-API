import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from src.routes.auth import logout
from src.schemas.user import UserBase


class TestLogout(unittest.IsolatedAsyncioTestCase):

    async def test_logout(self):
        token = "test_token"
        current_user = UserBase(username="test_user", email="test@example.com", password="test_password")

        db_session = MagicMock(spec=Session)
        with patch('src.repository.users.save_black_list_token', autospec=True) as mock_save_black_list_token:
            result = await logout(token=token, current_user=current_user, db=db_session)

            mock_save_black_list_token.assert_called_once_with(token, current_user, db_session)

            expected_result = {
                "status_code": 200,
                "detail": "User logged out successfully",
                "token": token
            }
            self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main(exit=False)
