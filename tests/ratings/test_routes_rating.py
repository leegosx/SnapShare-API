import unittest
from unittest.mock import patch, AsyncMock, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

from src.models.rating import Rating
from src.models.user import User
from src.schemas.rating import RatingRequest
from main import app
import unittest
from unittest.mock import MagicMock

from src.routes.ratings import (
    get_rating,
    get_ratings,
    get_by_photo_ratings,
    remove_rating,
    add_rating
)

class TestRatingsRoutes(unittest.IsolatedAsyncioTestCase):
    @patch('src.repository.ratings.get_ratings')
    @patch('src.repository.images.get_image')
    async def test_get_by_photo_ratings_success(self, mock_get_image, mock_get_ratings):
        mock_db = MagicMock()
        image_id = 1
        mock_image = MagicMock()
        mock_ratings = [MagicMock(rating_score=5), MagicMock(rating_score=4)]
        
        mock_get_image.return_value = mock_image
        mock_get_ratings.return_value = mock_ratings

        result = await get_by_photo_ratings(image_id, mock_db)

        self.assertEqual(len(result), len(mock_ratings))
        self.assertAlmostEqual(result[0].average_rating, sum(r.rating_score for r in mock_ratings) / len(mock_ratings))
        mock_get_image.assert_called_with(image_id, mock_db)
        mock_get_ratings.assert_called_with(mock_db, image_id=image_id)

    @patch('src.repository.ratings.get_ratings')
    @patch('src.repository.images.get_image')
    async def test_get_by_photo_ratings_image_not_found(self, mock_get_image, mock_get_ratings):
        mock_db = MagicMock()
        image_id = 1
    
        mock_get_image.return_value = None

        with self.assertRaises(HTTPException) as context:
            await get_by_photo_ratings(image_id, mock_db)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    
    @patch('src.repository.ratings.get_ratings')
    @patch('src.repository.images.get_image')
    async def test_get_by_photo_ratings_no_ratings_found(self, mock_get_image, mock_get_ratings):
        mock_db = MagicMock()
        image_id = 1
        mock_image = MagicMock()
    
        mock_get_image.return_value = mock_image
        mock_get_ratings.return_value = []

        with self.assertRaises(HTTPException) as context:
            await get_by_photo_ratings(image_id, mock_db)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        
    @patch('src.repository.ratings.get_rating')
    async def test_get_rating_success(self, mock_get_rating):
        mock_db = MagicMock()
        rating_id = 1
        mock_rating = MagicMock()
        mock_get_rating.return_value = mock_rating

        result = await get_rating(rating_id, mock_db)

        self.assertEqual(result, mock_rating)
        mock_get_rating.assert_called_with(rating_id, mock_db)
        
    @patch('src.repository.ratings.get_rating')
    async def test_get_rating_not_found(self, mock_get_rating):
        mock_db = MagicMock()
        rating_id = 1
        mock_get_rating.return_value = None

        with self.assertRaises(HTTPException) as context:
            await get_rating(rating_id, mock_db)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)


    @patch('src.repository.ratings.remove_rating')
    async def test_remove_rating_success(self, mock_remove_rating):
        mock_db = MagicMock()
        rating_id = 1
        mock_rating = MagicMock()
        mock_remove_rating.return_value = mock_rating

        result = await remove_rating(rating_id, mock_db)

        self.assertEqual(result, mock_rating)
        mock_remove_rating.assert_called_with(rating_id, mock_db)

    
    @patch('src.repository.ratings.remove_rating')
    async def test_remove_rating_not_found(self, mock_remove_rating):
        mock_db = MagicMock()
        rating_id = 1
        mock_remove_rating.return_value = None

        with self.assertRaises(HTTPException) as context:
            await remove_rating(rating_id, mock_db)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    
    @patch('src.repository.ratings.add_rating')
    @patch('src.repository.ratings.get_ratings')
    @patch('src.repository.images.get_image')
    async def test_add_rating_success(self, mock_get_image, mock_get_ratings, mock_add_rating):
        mock_db = MagicMock()
        image_id = 1
        user_id = 2
        mock_image = MagicMock(user_id=3)
        mock_ratings = []
        body = RatingRequest(rating=5)
        current_user = User(id=user_id)

        mock_get_image.return_value = mock_image
        mock_get_ratings.return_value = mock_ratings
        mock_add_rating.return_value = MagicMock()

        result = await add_rating(body, image_id, mock_db, current_user)

        self.assertIsNotNone(result)
        mock_get_image.assert_called_with(image_id, mock_db)
        mock_get_ratings.assert_called_with(mock_db, image_id=image_id, user_id=user_id)
        mock_add_rating.assert_called_with(body, image_id, user_id, mock_db)

    @patch('src.repository.ratings.get_ratings')
    @patch('src.repository.images.get_image')
    async def test_add_rating_image_not_found(self, mock_get_image, mock_get_ratings):
        mock_db = MagicMock()
        image_id = 1
        user_id = 2
        body = RatingRequest(rating=5)
        current_user = User(id=user_id)

        mock_get_image.return_value = None

        with self.assertRaises(HTTPException) as context:
            await add_rating(body, image_id, mock_db, current_user)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    @patch('src.repository.ratings.get_all_ratings')
    async def test_get_all_ratings_success(self, mock_get_all_ratings):
        mock_db = MagicMock()
        skip = 0
        limit = 100
        mock_ratings = [MagicMock(spec=Rating), MagicMock(spec=Rating)]
        mock_get_all_ratings.return_value = mock_ratings

        result = await get_ratings(skip, limit, mock_db)

        self.assertEqual(len(result), len(mock_ratings))
        mock_get_all_ratings.assert_called_with(skip, limit, mock_db)

    @patch('src.repository.ratings.get_all_ratings')
    async def test_get_all_ratings_no_ratings_found(self, mock_get_all_ratings):
        mock_db = MagicMock()
        skip = 0
        limit = 100
        mock_get_all_ratings.return_value = []

        with self.assertRaises(HTTPException) as context:
            await get_ratings(skip, limit, mock_db)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "No ratings found")