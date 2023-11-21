import unittest
from unittest.mock import patch, AsyncMock, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

from src.models.user import User
from src.schemas.comment import CommentRequest
from main import app
import unittest
from unittest.mock import MagicMock

from src.routes.comments import (
    read_comments, 
    read_comment,
    create_comment,
    update_comment,
    delete_comment
)

class TestCommentsRoutes(unittest.IsolatedAsyncioTestCase):

    @patch('src.repository.comments.get_comment')
    async def test_read_comment(self, mock_get_comment):
        # Arrange
        mock_db = MagicMock()
        mock_comment = MagicMock()
        mock_get_comment.return_value = mock_comment
        comment_id = 1

        # Act
        result = await read_comment(comment_id, mock_db)

        # Assert
        self.assertEqual(result, mock_comment)
        mock_get_comment.assert_called_with(comment_id, mock_db)

    @patch('src.repository.comments.get_comments')
    @patch('src.repository.images.get_image')
    async def test_read_comments(self, mock_get_image, mock_get_comments):
        # Arrange
        mock_db = MagicMock()
        mock_image = MagicMock()
        mock_comments = [MagicMock(), MagicMock()]
        mock_get_image.return_value = mock_image
        mock_get_comments.return_value = mock_comments
        image_id = 1

        # Act
        result = await read_comments(image_id, mock_db)

        # Assert
        self.assertEqual(result, mock_comments)
        mock_get_image.assert_called_with(image_id, mock_db)
        mock_get_comments.assert_called_with(image_id, mock_db)
    
    
    @patch('src.repository.comments.create_comment')
    @patch('src.repository.images.get_image')
    async def test_create_comment(self, mock_get_image, mock_create_comment):
        # Arrange
        mock_db = MagicMock()
        mock_image = MagicMock()
        mock_comment = MagicMock()
        mock_user = User(id=1, username="testuser", email="test@example.com")
        body = CommentRequest(content="Test comment", user_id=1)
        image_id = 1

        mock_get_image.return_value = mock_image
        mock_create_comment.return_value = mock_comment

        # Act
        result = await create_comment(body, image_id, mock_user, mock_db)

        # Assert
        self.assertEqual(result, mock_comment)
        mock_get_image.assert_called_with(image_id=image_id, db=mock_db)
        mock_create_comment.assert_called_with(body, mock_user, image_id, mock_db)
    
    @patch('src.repository.comments.update_comment')
    @patch('src.repository.comments.get_comment')
    async def test_update_comment(self, mock_get_comment, mock_update_comment):
        # Arrange
        mock_db = MagicMock()
        mock_comment = MagicMock()
        mock_comment.user_id = 1
        mock_updated_comment = MagicMock()
        mock_user = User(id=1, username="testuser", email="test@example.com")
        body = CommentRequest(content="Updated comment", user_id=1)
        comment_id = 1

        mock_get_comment.return_value = mock_comment
        mock_update_comment.return_value = mock_updated_comment

        # Act
        result = await update_comment(body, comment_id, mock_db, mock_user)

        # Assert
        self.assertEqual(result, mock_updated_comment)
        mock_get_comment.assert_called_with(comment_id, mock_db)
        mock_update_comment.assert_called_with(body, comment_id, mock_db)
    
    
    @patch('src.repository.comments.delete_comment')
    async def test_delete_comment(self, mock_delete_comment):
        # Arrange
        mock_db = MagicMock()
        mock_comment = MagicMock()
        mock_delete_comment.return_value = mock_comment
        comment_id = 1

        # Act
        result = await delete_comment(comment_id, mock_db)

        # Assert
        self.assertEqual(result, mock_comment)
        mock_delete_comment.assert_called_with(comment_id, mock_db)

    @patch('src.repository.comments.delete_comment')
    async def test_delete_comment_not_found(self, mock_delete_comment):
        # Arrange
        mock_db = MagicMock()
        mock_delete_comment.return_value = None
        comment_id = 1

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            await delete_comment(comment_id, mock_db)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)