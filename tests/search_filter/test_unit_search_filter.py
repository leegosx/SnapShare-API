import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
from src.models.image import Image, Tag
from src.models.user import User
from src.models.rating import Rating
from src.repository.search_filter import get_images_by_search, get_images_by_user

class TestSearchFilter(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(bind=engine)
        SessionClass = sessionmaker(bind=engine)
        self.db = SessionClass()

        user = User(
            username="test_user",
            email="test@example.com",
            password="test_password",
            avatar="test_avatar"
        )
        tag = Tag(name="test_tag")
        image = Image(
            image_url="test_image_url",
            content="test_content",
            user=user,
            tags=[tag],
            created_at=datetime.now()
        )
        rating = Rating(user=user, image=image, rating_score=4)
        self.db.add_all([user, tag, image, rating])
        self.db.commit()

    async def test_get_images_by_search(self):

        # Arrange
        tag = "test_tag"
        keyword = "test_content"
        min_rating = 3
        max_rating = 5
        start_date = "2023-11-20"
        end_date = datetime.now()

        # Act
        result = await get_images_by_search(
            self.db,
            tag=tag,
            keyword=keyword,
            min_rating=min_rating,
            max_rating=max_rating,
            start_date=start_date,
            end_date=end_date
        )

        print("Query parameters:")
        print(f"Tag: {tag}")
        print(f"Keyword: {keyword}")
        print(f"Min Rating: {min_rating}")
        print(f"Max Rating: {max_rating}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        print("Query result:")

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].tags[0].name, tag)
        self.assertEqual(result[0].content, keyword)
        self.assertGreaterEqual(result[0].ratings[0].rating_score, min_rating)
        self.assertLessEqual(result[0].ratings[0].rating_score, max_rating)


    def tearDown(self):
        self.db.close()

class TestGetImagesByUser(unittest.TestCase):
    @patch('src.repository.search_filter.get_rating_score')
    @patch('sqlalchemy.orm.Session')
    async def test_get_images_by_user(self, mock_session, mock_get_rating_score):
        # Підготовка даних
        user_id = 1
        mock_images = [MagicMock(spec=Image), MagicMock(spec=Image)]
        mock_session.query.return_value.filter.return_value = mock_session.query.return_value
        mock_session.query.return_value.join.return_value = mock_session.query.return_value
        mock_session.query.return_value.group_by.return_value = mock_session.query.return_value
        mock_session.query.return_value.having.return_value = mock_session.query.return_value
        mock_session.query.return_value.all.return_value = mock_images
        mock_get_rating_score.return_value = 4.5

        result = await get_images_by_user(mock_session, user_id)

        self.assertEqual(len(result), len(mock_images))
        for image_response in result:
            self.assertEqual(image_response.user_id, user_id)
            self.assertEqual(image_response.average_rating, mock_get_rating_score.return_value)

        mock_session.query.assert_called_with(Image)
        mock_session.query.return_value.filter.assert_called_with(Image.user_id == user_id)

if __name__ == '__main__':
    unittest.main()
