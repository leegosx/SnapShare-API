import unittest
from unittest.mock import patch, MagicMock
import re
from src.utils.qr_code import create_qr_code_from_url
from src.utils.image_utils import *


class TestCreateQRCodeFromURL(unittest.TestCase):
    def test_valid_url(self):
        """Test if a valid URL returns a base64 encoded string"""
        test_url = "https://www.example.com"
        result = create_qr_code_from_url(test_url)
        self.assertTrue(isinstance(result, str))
        # Check if the result is a base64 string
        base64_pattern = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$"
        self.assertTrue(re.match(base64_pattern, result))


class TestExtractIDFromURL(unittest.TestCase):
    def test_valid_url(self):
        """Test if the correct ID is extracted from a valid URL."""
        test_url = "http://youtube.com/watch?v=dQw4w9WgXcQ"
        expected_id = "dQw4w9WgXcQ"
        result = extract_id_from_url(test_url)
        self.assertEqual(result, expected_id)

    def test_empty_url(self):
        """Test the function with an empty string."""
        test_url = ""
        expected_id = None
        result = extract_id_from_url(test_url)
        self.assertEqual(result, expected_id)

    def test_non_url_string(self):
        """Test the function with a non-URL string."""
        test_url = "just_a_random_string"
        expected_id = None
        result = extract_id_from_url(test_url)
        self.assertEqual(result, expected_id)

    # Mock User class for testing


class MockUser:
    def __init__(self, username, id):
        self.username = username
        self.id = id


class TestGetCloudinaryPublicID(unittest.TestCase):
    def test_valid_user(self):
        """Test with a user object having both username and id."""
        user = MockUser(username="testuser", id=123)
        expected_public_id = "SnapShare-API/testuser123"
        result = get_cloudinary_public_id(user)
        self.assertEqual(result, expected_public_id)


class MockFile:
    def __init__(self):
        self.file = MagicMock()


class TestPostCloudinaryImage(unittest.TestCase):
    @patch("cloudinary.uploader.upload")
    @patch("cloudinary.CloudinaryImage.build_url")
    def test_valid_file_and_user(self, mock_build_url, mock_upload):
        """Test with valid file and user objects."""
        mock_user = MockUser(username="testuser", id=123)
        mock_file = MockFile()
        mock_upload.return_value = {"version": "12345"}
        mock_build_url.return_value = "http://mocked.url/image"

        result = post_cloudinary_image(mock_file, mock_user)
        self.assertEqual(result, "http://mocked.url/image")

    @patch("cloudinary.uploader.upload", side_effect=Exception("Mocked upload error"))
    def test_error_handling(self, mock_upload):
        """Test error handling when Cloudinary API returns an error."""
        mock_user = MockUser(username="testuser", id=123)
        mock_file = MockFile()

        with self.assertRaises(Exception):
            post_cloudinary_image(mock_file, mock_user)


class TestGetCloudinaryImageTransformation(unittest.TestCase):
    @patch("cloudinary.CloudinaryImage.build_url")
    def test_valid_inputs(self, mock_build_url):
        """Test with all valid arguments."""
        mock_build_url.return_value = "http://mocked.url/transformed_image"
        user = MockUser(username="testuser", id=123)
        result = get_cloudinary_image_transformation(
            user, "resize", 100, 100, None, None
        )
        self.assertEqual(result, "http://mocked.url/transformed_image")

    def test_invalid_transformation_type(self):
        """Test the function's behavior with an unknown transformation type."""
        user = MockUser(username="testuser", id=123)
        with self.assertRaises(KeyError):
            get_cloudinary_image_transformation(
                user, "unknown_type", 100, 100, None, None
            )

    @patch("cloudinary.CloudinaryImage.build_url")
    def test_incomplete_parameters(self, mock_build_url):
        """Test with missing or None parameters."""
        mock_build_url.return_value = "http://mocked.url/transformed_image"
        user = MockUser(username="testuser", id=123)
        result = get_cloudinary_image_transformation(
            user, "resize", None, None, None, None
        )
        self.assertEqual(result, "http://mocked.url/transformed_image")


if __name__ == "__main__":
    unittest.main()
