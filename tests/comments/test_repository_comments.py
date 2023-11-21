import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
from unittest.mock import MagicMock
from src.models.comment import Comment
from src.repository.comments import create_comment, get_comment, get_comments, delete_comment, update_comment
from src.schemas.comment import CommentRequest



class TestUpdateComment(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = MagicMock()

    # Додайте цей метод в тестовий клас TestUpdateComment
    async def test_get_comment(self):
        comment_id = 1
        expected_comment = MagicMock()
        self.db.query().filter().first.return_value = expected_comment

        result = await get_comment(comment_id, self.db)

        self.assertEqual(result, expected_comment)
        self.db.query().filter().first.assert_called_once_with()

    # Додайте цей метод в тестовий клас TestUpdateComment
    async def test_get_comments(self):
        image_id = 2
        expected_comments = [MagicMock(), MagicMock()]
        self.db.query().filter().limit().all.return_value = expected_comments

        result = await get_comments(image_id, self.db)

        self.assertEqual(result, expected_comments)
        self.db.query().filter().limit().all.assert_called_once_with()

    # Додайте цей метод в тестовий клас TestUpdateComment
    async def test_create_comment(self):
        comment_data = CommentRequest(content="Тестовий коментар")
        user = MagicMock()
        user.id = 1
        image_id = 2
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()

        result = await create_comment(comment_data, user, image_id, self.db)

        self.assertIsNotNone(result)
        self.assertEqual(result.content, "Тестовий коментар")
        self.assertEqual(result.user_id, user.id)
        self.assertEqual(result.image_id, image_id)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(result)

    async def test_update_comment(self):
        comment_id = 1
        comment_request = CommentRequest(content="Оновлений коментар")
        existing_comment = MagicMock()
        self.db.query().filter().first.return_value = existing_comment

        result = await update_comment(comment_request, comment_id, self.db)

        self.assertEqual(result, existing_comment)
        self.assertEqual(existing_comment.content, "Оновлений коментар")
        self.db.query().filter().first.assert_called_once_with()
        self.db.commit.assert_called_once_with()

    # Додайте цей метод в тестовий клас TestUpdateComment
    async def test_delete_comment(self):
        comment_id = 1
        existing_comment = MagicMock()
        self.db.query().filter().first.return_value = existing_comment

        result = await delete_comment(comment_id, self.db)

        self.assertEqual(result, existing_comment)
        self.db.query().filter().first.assert_called_once_with()
        self.db.delete.assert_called_once_with(existing_comment)
        self.db.commit.assert_called_once_with()


if __name__ == '__main__':
    unittest.main(verbosity=2)