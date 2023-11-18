import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.models.comment import Comment
from src.schemas.comment import CommentRequest, CommentResponse
from src.routes.comments import router
from src.database.db import get_db

class TestCreateCommentRoute(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.db = next(get_db())  # Отримання сесії БД

    async def test_create_comment_route(self):
        comment_data = {"content": "Test comment"}

        # Виклик маршруту POST через TestClient
        response = self.client.post(
            "/comments/",
            json={
                "body": comment_data,
                "image_id": 1  # Замініть це на реальний image_id
            }
        )

        # Перевірка відповіді
        self.assertEqual(response.status_code, 200)
        new_comment = response.json()
        self.assertIsNotNone(new_comment)
        # Додаткові перевірки...

    async def test_get_comment_route(self):
        comment_id = 1  # Замініть це на реальний comment_id

        # Виклик маршруту GET через TestClient
        response = self.client.get(f"/comments/{comment_id}")

        # Перевірка відповіді
        self.assertEqual(response.status_code, 200)
        comment = response.json()
        self.assertIsNotNone(comment)
        # Додаткові перевірки...

    async def test_get_comments_route(self):
        image_id = 1  # Замініть це на реальний image_id

        # Виклик маршруту GET через TestClient
        response = self.client.get(f"/comments/all?image_id={image_id}")

        # Перевірка відповіді
        self.assertEqual(response.status_code, 200)
        comments = response.json()
        self.assertIsNotNone(comments)
        # Додаткові перевірки...

    async def test_update_comment_route(self):
        comment_id = 1  # Замініть це на реальний comment_id
        comment_data = {"content": "Updated comment"}

        # Виклик маршруту PUT через TestClient
        response = self.client.put(
            f"/comments/{comment_id}",
            json={
                "body": comment_data
            }
        )

        # Перевірка відповіді
        self.assertEqual(response.status_code, 200)
        updated_comment = response.json()
        self.assertIsNotNone(updated_comment)
        # Додаткові перевірки...

    async def test_delete_comment_route(self):
        comment_id = 1  # Замініть це на реальний comment_id

        # Виклик маршруту DELETE через TestClient
        response = self.client.delete(f"/comments/{comment_id}")

        # Перевірка відповіді
        self.assertEqual(response.status_code, 200)
        deleted_comment = response.json()
        self.assertIsNotNone(deleted_comment)
        # Додаткові перевірки...

if __name__ == '__main__':
    unittest.main(verbosity=2)