import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.orm import Session
from src.models.photo import Photo, Tag
from src.models.user import User
from src.schemas.photo import PhotoCreate, PhotoUpdate
from src.repository.photos import (
    create_photo,
    update_photo,
    delete_photo,
    get_photo,
    get_photos,
    get_photo_user,
)


class TestPhotos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """
        The setUp function is called before each test function.
        It creates a mock session object, a mock user object, and three mock tag objects.
        The session object is used to create the TagManager instance that will be tested.
        
        :param self: Represent the instance of the class
        :return: A list of tags
        :doc-author: Trelent
        """
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User, id=1)
        self.tags = [
            MagicMock(spec=Tag, id=i, name=i, _sa_instance_state=MagicMock())
            for i in range(1, 4)
        ]

    async def test_create_photo(self):
        """
        The test_create_photo function tests the create_photo function.
        It does this by creating a PhotoCreate object with actual data, and then calling the create_photo function with that data.
        Then it asserts that the result of calling create_photo has all of the expected attributes.
        
        :param self: Access the attributes and methods of a class in python
        :return: Nothing
        :doc-author: Trelent
        """
        # Instantiate PhotoCreate with actual data
        photo_data = PhotoCreate(
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
            user_id=self.user.id,
            tags=[tag.id for tag in self.tags],  # Use actual ids if possible
        )

        # Call the function under test
        result = await create_photo(photo_data, {"id": 1}, self.session)

        # Make assertions
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        # Assert that the result has the expected attributes
        self.assertEqual(result.image_url, photo_data.image_url)
        self.assertEqual(result.content, photo_data.content)
        self.assertEqual(result.user_id, self.user.id)

    async def test_update_photo_not_found(self):
        """
        The test_update_photo_not_found function tests the update_photo function when a photo is not found.
        
        :param self: Access the attributes and methods of the class in python
        :return: None when the photo is not found
        :doc-author: Trelent
        """
        photo_data = PhotoUpdate(
            image_url="http://testurl.com/image.jpg", content="Updated Description"
        )
        # Mock the query to return None for first()
        self.session.query().filter().first.return_value = None

        # Call the function under test
        result = await update_photo(
            15,
            photo_data=photo_data,
            current_user={"id": self.user.id},
            db=self.session,
        )

        # Check that the result is None when the photo is not found
        self.assertIsNone(result)

    async def test_update_photo_found(self):
        """
        The test_update_photo_found function tests the update_photo function when a photo is found.
        It does this by creating a PhotoUpdate object with image_url and content attributes, then creates
        a Photo object with id, user_id, image_url and content attributes. It then sets the return value of 
        the scalars method to be equal to the photo object created above. The commit method is set to return None 
        and refresh is called on the photo object created above.
        
        :param self: Access the class attributes and methods
        :return: A result with the updated photo content
        :doc-author: Trelent
        """
        photo_data = PhotoUpdate(
            image_url="http://testurl.com/image.jpg", content="Updated Description"
        )
        photo = Photo(
            id=1,
            user_id=self.user.id,
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
        )
        self.session.execute.return_value.scalars.return_value.first.return_value = (
            photo
        )
        self.session.commit.return_value = None
        self.session.refresh(photo)
        result = await update_photo(
            photo.id,
            photo_data=photo_data,
            current_user={"id": self.user.id},
            db=self.session,
        )
        self.assertEqual(result.content, photo_data.content)

    async def test_delete_photo_found(self):
        """
        The test_delete_photo_found function tests the delete_photo function when a photo is found.
        It mocks the correct method chain, calls the function under test, and checks that 
        the result is equal to the photo object.
        
        :param self: Represent the instance of the class
        :return: The photo object, but the delete_photo function returns none
        :doc-author: Trelent
        """
        photo = Photo(
            id=1,
            user_id=self.user.id,
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
        )
        # Mock the correct method chain
        self.session.query().filter().first.return_value = photo
        self.session.delete.return_value = None
        self.session.commit.return_value = None

        # Call the function under test
        result = await delete_photo(
            photo_id=photo.image_url, current_user={"id": self.user.id}, db=self.session
        )

        # Check that the result is the photo object
        self.assertEqual(result, photo)

    async def test_delete_photo_not_found(self):
        """
        The test_delete_photo_not_found function tests the delete_photo function when a photo is not found.
        
        :param self: Access the attributes and methods of the class in python
        :return: None when there is no photo with the specified id
        :doc-author: Trelent
        """
        self.session.query().filter().first.return_value = None
        result = await delete_photo(
            photo_id=1, current_user={"id": self.user.id}, db=self.session
        )
        self.assertIsNone(result)

    async def test_get_photo(self):
        """
        The test_get_photo function tests the get_photo function in the photos.py file.
        It does this by creating a Photo object and assigning it to photo, then using
        the mock session's query method to return that photo when called with filter().first()
        
        :param self: Access the class attributes and methods
        :return: The photo object
        :doc-author: Trelent
        """
        photo = Photo(
            id=1,
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
        )
        self.session.query().filter().first.return_value = photo
        result = await get_photo(photo_id=1, db=self.session)
        self.assertEqual(result, photo)

    async def test_get_photos(self):
        """
        The test_get_photos function tests the get_photos function.
        It does this by mocking out the database session and returning a list of photos.
        The test then checks that the result from calling get_photos matches what was returned from our mock.
        
        :param self: Access the instance of the class
        :return: A list of photos
        :doc-author: Trelent
        """
        photos = [
            Photo(
                id=1,
                user_id=self.user.id,
                image_url="http://testurl.com/image.jpg",
                content="Test Description",
            )
        ]
        # Correctly mock the query chain
        self.session.query().filter().offset().limit().all.return_value = photos

        # Call the function under test
        result = await get_photos(
            skip=0, limit=100, current_user={"id": self.user.id}, db=self.session
        )

        # Check that the result matches the expected photos list
        self.assertEqual(result, photos)


    async def test_get_photo_user(self):
        """
        The test_get_photo_user function tests the get_photo_user function.
        It does this by mocking a photo and a user, then calling the get_photo_user function with those mocks.
        The test asserts that the result of calling get_photo is equal to our mock photo.
        
        :param self: Access the instance of the class
        :return: The mock photo
        :doc-author: Trelent
        """
        # Setup
        photo_id = 1
        mock_photo = Photo(id=photo_id, user_id=1)  # Replace with appropriate attributes
        db = MagicMock(spec=Session)
        current_user = MagicMock()
        current_user.id = 1  # Set this to the id of the user who owns the mock photo

        # Mock the database query
        db.query.return_value.filter.return_value.first.return_value = mock_photo

        # Test Execution
        result = await get_photo_user(photo_id, db, current_user)

        # Assertions
        self.assertEqual(result, mock_photo)
        db.query.assert_called_with(Photo)


if __name__ == "__main__":
    unittest.main()
