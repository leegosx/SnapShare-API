import os
import sys
import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.routes.comments import router
from src.schemas.comment import CommentRequest, CommentResponse
from src.models.comment import Comment
from src.services.auth_service import auth_service
from src.database.db import get_db
from src.repository import comments as repository_comments

class TestCommentRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(router)
        cls.db = MagicMock(spec=Session)
        cls.auth_service = auth_service()

    def test_read_comments(self):
        response = self.client.get("/comments/all/?image_id=1")
        self.assertEqual(response.status_code, 200)

    def test_read_comment(self):
        response = self.client.get("/comments/get/1/")
        self.assertEqual(response.status_code, 200)

    def test_create_comment(self):
        # Assuming you have a valid token for the current user
        token = self.auth_service.create_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Assuming you have a valid image_id and CommentRequest
        data = {"content": "Test comment"}
        response = self.client.post("/comments/add_comments/?image_id=1", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)
        comment_response = CommentResponse(**response.json())
        self.assertIsInstance(comment_response, CommentResponse)

    def test_update_comment(self):
        # Assuming you have a valid token for the current user
        token = self.auth_service.create_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Assuming you have a valid comment_id and CommentRequest
        comment_id = 1
        data = {"content": "Updated comment"}
        response = self.client.put(f"/comments/update/{comment_id}/", json=data, headers=headers)
        self.assertEqual(response.status_code, 200)
        comment_response = CommentResponse(**response.json())
        self.assertIsInstance(comment_response, CommentResponse)

    def test_delete_comment(self):
        # Assuming you have a valid token with admin or moderator role
        token = self.auth_service.create_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Assuming you have a valid comment_id
        comment_id = 1
        response = self.client.delete(f"/comments/remove/{comment_id}/", headers=headers)
        self.assertEqual(response.status_code, 200)
        comment_response = CommentResponse(**response.json())
        self.assertIsInstance(comment_response, CommentResponse)

if __name__ == '__main__':
    unittest.main(verbosity=2)
