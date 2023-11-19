import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.orm import Session
from src.models.image import Image, Tag
from src.models.user import User
from src.schemas.image import ImageCreate, ImageUpdate
from src.repository.images import (
    create_image,
    update_image,
    delete_image,
    get_image,
    get_images,
    get_image_user,
)


class Testimages(unittest.IsolatedAsyncioTestCase):
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

    async def test_create_image(self):
        """
        The test_create_image function tests the create_image function.
        It does this by creating a ImageCreate object with actual data, and then calling the create_image function with that data.
        Then it asserts that the result of calling create_image has all of the expected attributes.

        :param self: Access the attributes and methods of a class in python
        :return: Nothing
        :doc-author: Trelent
        """
        # Instantiate ImageCreate with actual data
        image_data = ImageCreate(
            content="Test Description",
            user_id=self.user.id,
            tags=[str(tag.id) for tag in self.tags],  # Use actual ids if possible
        )

        # Call the function under test
        result = await create_image("http://testurl.com/image.jpg",image_data, User(id=1), self.session)

        # Make assertions
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        # Assert that the result has the expected attributes
        # self.assertEqual(result.image_url, image_data.image_url)
        self.assertEqual(result.content, image_data.content)
        self.assertEqual(result.user_id, self.user.id)

    async def test_update_image_not_found(self):
        """
        The test_update_image_not_found function tests the update_image function when a image is not found.

        :param self: Access the attributes and methods of the class in python
        :return: None when the image is not found
        :doc-author: Trelent
        """
        image_data = ImageUpdate(
            image_url="http://testurl.com/image.jpg", content="Updated Description"
        )
        # Mock the query to return None for first()
        self.session.query().filter().first.return_value = None

        # Call the function under test
        result = await update_image(
            15,
            image_data=image_data,
            current_user=User(id=self.user.id),
            db=self.session,
        )

        # Check that the result is None when the image is not found
        self.assertIsNone(result)

    async def test_update_image_found(self):
        """
        The test_update_image_found function tests the update_image function when a image is found.
        It does this by creating a ImageUpdate object with image_url and content attributes, then creates
        a image object with id, user_id, image_url and content attributes. It then sets the return value of
        the scalars method to be equal to the image object created above. The commit method is set to return None
        and refresh is called on the image object created above.

        :param self: Access the class attributes and methods
        :return: A result with the updated image content
        :doc-author: Trelent
        """
        image_data = ImageUpdate(
            image_url="http://testurl.com/image.jpg", content="Updated Description"
        )
        image = Image(
            id=1,
            user_id=self.user.id,
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
        )
        self.session.execute.return_value.scalars.return_value.first.return_value = (
            image
        )
        self.session.commit.return_value = None
        self.session.refresh(image)
        result = await update_image(
            image.id,
            image_data=image_data,
            current_user=User(id=self.user.id),
            db=self.session,
        )
        self.assertEqual(result.content, image_data.content)

    async def test_delete_image_found(self):
        """
        The test_delete_image_found function tests the delete_image function when a image is found.
        It mocks the correct method chain, calls the function under test, and checks that
        the result is equal to the image object.

        :param self: Represent the instance of the class
        :return: The image object, but the delete_image function returns none
        :doc-author: Trelent
        """
        image = Image(
            id=1,
            user_id=self.user.id,
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
        )
        # Mock the correct method chain
        self.session.query().filter().first.return_value = image
        self.session.delete.return_value = None
        self.session.commit.return_value = None

        # Call the function under test
        result = await delete_image(
            image_id=image.image_url,
            current_user=User(id=self.user.id),
            db=self.session,
        )

        # Check that the result is the image object
        self.assertEqual(result, image)

    async def test_delete_image_not_found(self):
        """
        The test_delete_image_not_found function tests the delete_image function when a image is not found.

        :param self: Access the attributes and methods of the class in python
        :return: None when there is no image with the specified id
        :doc-author: Trelent
        """
        self.session.query().filter().first.return_value = None
        result = await delete_image(
            image_id=1, current_user=User(id=self.user.id), db=self.session
        )
        self.assertIsNone(result)

    async def test_get_image(self):
        """
        The test_get_image function tests the get_image function in the images.py file.
        It does this by creating a image object and assigning it to image, then using
        the mock session's query method to return that image when called with filter().first()

        :param self: Access the class attributes and methods
        :return: The image object
        :doc-author: Trelent
        """
        image = Image(
            id=1,
            image_url="http://testurl.com/image.jpg",
            content="Test Description",
        )
        self.session.query().filter().first.return_value = image
        result = await get_image(image_id=1, db=self.session)
        self.assertEqual(result, image)

    async def test_get_images(self):
        """
        The test_get_images function tests the get_images function.
        It does this by mocking out the database session and returning a list of images.
        The test then checks that the result from calling get_images matches what was returned from our mock.

        :param self: Access the instance of the class
        :return: A list of images
        :doc-author: Trelent
        """
        images = [
            Image(
                id=1,
                user_id=self.user.id,
                image_url="http://testurl.com/image.jpg",
                content="Test Description",
            )
        ]
        # Correctly mock the query chain
        self.session.query().filter().offset().limit().all.return_value = images

        # Call the function under test
        result = await get_images(
            skip=0, limit=100, current_user=User(id=self.user.id), db=self.session
        )

        # Check that the result matches the expected images list
        self.assertEqual(result, images)

    async def test_get_image_user(self):
        """
        The test_get_image_user function tests the get_image_user function.
        It does this by mocking a image and a user, then calling the get_image_user function with those mocks.
        The test asserts that the result of calling get_image is equal to our mock image.

        :param self: Access the instance of the class
        :return: The mock image
        :doc-author: Trelent
        """
        # Setup
        image_id = 1
        mock_image = Image(
            id=image_id, user_id=1
        )  # Replace with appropriate attributes
        db = MagicMock(spec=Session)
        current_user = MagicMock()
        current_user.id = 1  # Set this to the id of the user who owns the mock image

        # Mock the database query
        db.query.return_value.filter.return_value.first.return_value = mock_image

        # Test Execution
        result = await get_image_user(image_id, db, current_user)

        # Assertions
        self.assertEqual(result, mock_image)
        db.query.assert_called_with(Image)


if __name__ == "__main__":
    unittest.main()
