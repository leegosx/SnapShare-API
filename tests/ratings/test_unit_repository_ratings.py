import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.schemas.rating import RatingRequest, RatingResponse
from src.models.rating import Rating
from src.models.image import Image
from src.models.user import User
from src.repository.ratings import (
    get_rating,
    get_ratings,
    add_rating,
    remove_rating
)

class TestAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.mock_rating = MagicMock(spec=Rating)
        self.mock_user = MagicMock(spec=User)
        self.mock_image = MagicMock(spec=Image)
        
    async def test_get_ratings_with_image_id_and_user_id(self):
        test_image_id = 1
        test_user_id = 1
        expected_ratings = [MagicMock(spec=Rating), MagicMock(spec=Rating)]
    
        self.session.query().filter().all.return_value = expected_ratings

        ratings = await get_ratings(self.session, test_image_id, test_user_id)

        self.session.query.assert_called_with(Rating)
        self.assertEqual(ratings, expected_ratings)

    async def test_get_rating(self):
        test_rating_id = 1
        expected_rating = MagicMock(spec=Rating)

        self.session.query().filter().first.return_value = expected_rating

        rating = await get_rating(test_rating_id, self.session)

        self.session.query.assert_called_with(Rating)
        self.assertEqual(rating, expected_rating)

    async def test_add_rating(self):
        test_rating_request = RatingRequest(rating=5)
        test_image_id = 1
        test_user_id = 1

        new_rating = await add_rating(test_rating_request, test_image_id, test_user_id, self.session)

        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(new_rating)

        self.assertEqual(new_rating.rating_score, test_rating_request.rating)
        self.assertEqual(new_rating.user_id, test_user_id)
        self.assertEqual(new_rating.image_id, test_image_id)


    async def test_remove_rating_existing_rating(self):
        test_rating_id = 1
        rating_to_remove = MagicMock(spec=Rating)

        self.session.query().filter().first.return_value = rating_to_remove

        result = await remove_rating(test_rating_id, self.session)

        self.session.delete.assert_called_once_with(rating_to_remove)
        self.session.commit.assert_called_once()
        self.assertEqual(result, rating_to_remove)
    
if __name__ == '__main__':
    print(TestAsync.setUp)
    unittest.main()