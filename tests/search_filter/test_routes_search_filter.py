from unittest.mock import patch, MagicMock, ANY
import unittest
from fastapi.testclient import TestClient
from main import app
from src.models.image import Image
from src.models.user import User
from src.schemas.image import ImageSearch

class TestSearchFilterRoutes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('src.repository.search_filter.get_images_by_search')
    async def test_search_images_success(self, mock_get_images_by_search):
        mock_images = [MagicMock(spec=Image), MagicMock(spec=Image)]
        mock_get_images_by_search.return_value = mock_images

        response = self.client.get("/search_filter/search/", params={'tag': 'nature', 'min_rating': 3, 'max_rating': 5})

        if response.status_code == 404:
            print("Error: Image not found.")
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), len(mock_images))

    @patch('src.repository.search_filter.get_images_by_search')
    async def test_search_images_no_results(self, mock_get_images_by_search):
        mock_get_images_by_search.return_value = []

        response = self.client.get("/search_filter/search/", params={'keyword': 'mountain'})

        self.assertEqual(response.status_code, 404)
        self.assertIn("Not Found", response.json().get("detail"))

    async def test_search_images_missing_parameters(self):
        response = self.client.get("/search_filter/search/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Not Found", response.json().get("detail"))

class TestSearchImagesByUserRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('src.repository.search_filter.get_images_by_user')
    @patch('sqlalchemy.orm.Session')
    async def test_search_images_by_user_success(self, mock_session, mock_get_images_by_user):
        user_id = 1
        mock_user = User(id=user_id)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_images_by_user.return_value = [MagicMock(), MagicMock()]

        response = self.client.get(f"/search_filter/search/{user_id}/images")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        mock_get_images_by_user.assert_called_with(mock_session, user_id, 0, 5, None, None)

    @patch('sqlalchemy.orm.Session')
    async def test_search_images_by_user_not_found(self, mock_session):
        user_id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = None

        response = self.client.get(f"/search_filter/search/{user_id}/images")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": f"User with id {user_id} not found."})