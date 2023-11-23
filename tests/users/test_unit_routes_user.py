import unittest
from unittest.mock import patch, MagicMock, AsyncMock, MagicMock
from fastapi import UploadFile
from src.routes.users import update_avatar_user, change_username, read_users_me
from src.schemas.user import Username

class TestUpdateAvatarUser(unittest.TestCase):

    @patch('cloudinary.uploader.upload')
    @patch('src.repository.users.update_avatar')
    @patch('src.services.auth_service.Auth.get_current_user')
    def test_update_avatar_user(self, mock_get_current_user, mock_update_avatar, mock_cloudinary_upload):
        mock_user = MagicMock()
        mock_db = MagicMock()
        mock_get_current_user.return_value = mock_user
        mock_update_avatar.return_value = MagicMock()
        mock_cloudinary_upload.return_value = {'public_id': 'test_public_id', 'version': '1234'}

        mocked_file = MagicMock(spec=UploadFile)
        mocked_file.filename = "test_image.jpg"
        mocked_file.file = MagicMock()
        mocked_file.file.read = MagicMock(return_value=b'fake image data')
        mocked_file.content_type = "image/jpeg"
        
        result = update_avatar_user(file=mocked_file, current_user=mock_user, db=mock_db)

        self.assertIsNotNone(result)

class TestChangeUsername(unittest.IsolatedAsyncioTestCase):

    @patch('src.repository.users.get_user_by_username')
    @patch('src.repository.users.update_user')
    @patch('src.services.auth_service.Auth.get_current_user')
    @patch('src.routes.users.get_db')
    async def test_change_username_success(self, mock_get_db, mock_get_current_user, mock_update_user, mock_get_user_by_username):

        mock_user = MagicMock()
        mock_get_current_user.return_value = mock_user
        mock_get_user_by_username.return_value = None
        mock_update_user.return_value = mock_user
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_user.username = "existing_username"
        new_username = "new_username"

        body = Username(username=new_username)

        result = await change_username(body=body, user=mock_user, db=mock_db)

        self.assertIsNotNone(result)
        self.assertEqual(result.username, new_username)
        
@patch('src.services.auth_service.Auth.get_current_user')  
@patch('src.repository.users.get_user_images')
class TestReadUserMe(unittest.IsolatedAsyncioTestCase):

    async def test_read_users_me(self, mock_get_user_images, mock_get_current_user):
        mock_user = MagicMock()
        
        mock_user.username = "test_username"
        mock_user.email = "test@example.com"
        mock_user.avatar = "test_avatar_url"
        mock_user.role = "test_role"
        mock_get_user_images.return_value = 5
        
        mock_get_current_user.return_value = mock_user
        
        result = await read_users_me(current_user=mock_user, db=MagicMock())
        
        self.assertEqual(result.username, mock_user.username)
        self.assertEqual(result.email, mock_user.email)
        self.assertEqual(result.avatar, mock_user.avatar)
        self.assertEqual(result.role, mock_user.role)
        self.assertEqual(result.uploaded_images, 5)

        
if __name__ == '__main__':
    unittest.main()
