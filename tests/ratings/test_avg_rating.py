import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from sqlalchemy.orm import Session
from src.models.image import Image
from src.models.rating import Rating
from src.repository import images as repository_images
from src.repository import ratings as repository_ratings
from unittest.mock import MagicMock

class TestAvarageRatings(unittest.TestCase):
    async def test_average_rating(self):
        mock_image = Image(id=1)
        mock_get_image = MagicMock(return_value=mock_image)
        mock_get_ratings = MagicMock(return_value=[Rating(rating=5), Rating(rating=3)])

        rating_avg = await repository_images.average_rating(1, mock_get_image, mock_get_ratings)

        self.assertEqual(rating_avg, 4.0)

if __name__ == "__main__":
    unittest.main()