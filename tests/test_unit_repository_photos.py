import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.models.photo import Photo
from src.models.user import User
from src.schemas.photo import PhotoCreate, PhotoUpdate
from src.repository.photos import (
    create_photo,
    update_photo,
    delete_photo,
    get_photo,
    get_photos,
)


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User, id=1)


    async def test_create_photo(self):
        photo_data = PhotoCreate(
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
            user_id=self.user.id,
            tags=[1, 2, 3],  # Example tags, adjust as necessary for your tests
        )
        new_photo = Photo(
            image_url=photo_data.image_url,
            content=photo_data.content,
            user_id=photo_data.user_id,
            tags=photo_data.tags,  # Assuming your Photo model also has a tags field
        )
        self.session.add(new_photo)
        self.session.commit.return_value = None
        self.session.refresh(new_photo)
        result = await create_photo(photo_data, self.user, self.session)
        self.assertEqual(result.image_url, photo_data.image_url)
        self.assertEqual(result.content, photo_data.content)
        self.assertEqual(result.user_id, photo_data.user_id)
        self.assertEqual(result.tags, photo_data.tags)

    # async def test_update_photo_found(self):
    #     photo_data = PhotoUpdate(description="Updated Description")
    #     photo = Photo(
    #         id=1,
    #         user_id=self.user.id,
    #         url="http://testurl.com/image.jpg",
    #         description="Test Description",
    #     )
    #     self.session.execute.return_value.scalars().first.return_value = photo
    #     self.session.commit.return_value = None
    #     self.session.refresh(photo)
    #     result = await update_photo(
    #         photo_id=1, photo_data=photo_data, current_user=self.user, db=self.session
    #     )
    #     self.assertEqual(result.description, photo_data.description)

    # async def test_update_photo_not_found(self):
    #     photo_data = PhotoUpdate(description="Updated Description")
    #     self.session.execute.return_value.scalars().first.return_value = None
    #     result = await update_photo(
    #         photo_id=1, photo_data=photo_data, current_user=self.user, db=self.session
    #     )
    #     self.assertIsNone(result)

    # async def test_delete_photo_found(self):
    #     photo = Photo(
    #         id=1,
    #         user_id=self.user.id,
    #         url="http://testurl.com/image.jpg",
    #         description="Test Description",
    #     )
    #     self.session.execute.return_value.scalars().first.return_value = photo
    #     self.session.delete.return_value = None
    #     self.session.commit.return_value = None
    #     result = await delete_photo(photo_id=1, current_user=self.user, db=self.session)
    #     self.assertEqual(result, photo)

    # async def test_delete_photo_not_found(self):
    #     self.session.execute.return_value.scalars().first.return_value = None
    #     result = await delete_photo(photo_id=1, current_user=self.user, db=self.session)
    #     self.assertIsNone(result)

    # async def test_get_photo(self):
    #     photo = Photo(
    #         id=1, url="http://testurl.com/image.jpg", description="Test Description"
    #     )
    #     self.session.execute.return_value.scalars().first.return_value = photo
    #     result = await get_photo(photo_id=1, db=self.session)
    #     self.assertEqual(result, photo)

    # async def test_get_photos(self):
    #     photos = [
    #         Photo(
    #             id=1,
    #             user_id=self.user.id,
    #             url="http://testurl.com/image.jpg",
    #             description="Test Description",
    #         )
    #     ]
    #     self.session.execute.return_value.scalars().all.return_value = photos
    #     result = await get_photos(current_user=self.user, db=self.session)
    #     self.assertEqual(result, photos)


if __name__ == "__main__":
    unittest.main()
