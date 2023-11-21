import sys
import os
import unittest
import asyncio
from unittest.mock import patch, MagicMock, Mock
from fastapi import UploadFile, HTTPException
from src.routes.images import create_image
from src.models.image import Image


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class TestCreateImage(unittest.TestCase):
    @patch("tests.images.conftest.cloudinary.config")
    @patch("cloudinary.uploader.upload")
    @patch("cloudinary.CloudinaryImage")
    def test_create_image(self, mock_cloudinary_image, mock_upload, mock_config):
        # Mocking file upload
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_image.jpg"
        mock_file.file = MagicMock()

        # Mocking user and database session
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_user.id = "123"
        mock_db = MagicMock()

        # Mocking Cloudinary upload and URL generation
        mock_upload.return_value = {"public_id": "test_public_id", "version": "123456"}
        mock_cloudinary_image.return_value.build_url.return_value = (
            "http://mocked_url.com"
        )

        # Mocking ImageCreate and expected response
        mock_image_create = MagicMock()
        expected_response = MagicMock()

        # Call the function
        response = asyncio.run(
            create_image(
                file=mock_file, body=mock_image_create, user=mock_user, db=mock_db
            )
        )

        # Assertions
        self.assertIsInstance(response, Image)  # Assuming Image is the expected type
        mock_upload.assert_called_once_with(
            mock_file.file, public_id="SnapShare-API/testuser123", owerwrite=True
        )
        mock_cloudinary_image.assert_called_once_with("SnapShare-API/testuser123")

    @patch("tests.images.conftest.cloudinary.config")
    @patch("cloudinary.uploader.upload")
    @patch("cloudinary.CloudinaryImage")
    def test_create_image_with_too_many_tags(self, mock_cloudinary_image, mock_upload, mock_config):
        # Mocking file upload
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test_image.jpg"
        mock_file.file = MagicMock()

        # Mocking user and database session
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_user.id = "123"
        mock_db = MagicMock()

        # Mocking ImageCreate with too many tags
        mock_image_create = MagicMock()
        mock_image_create.tags = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6']  # More than 5 tags

        # Assert that HTTPException is raised
        with self.assertRaises(HTTPException) as context:
            asyncio.run(
                create_image(
                    file=mock_file, body=mock_image_create, user=mock_user, db=mock_db
                )
            )

        # Check if the correct exception is raised
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Maximum number of tags is 5")

def test_update_image(client, user, monkeypatch, mock_redis):
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Prepare the image update data
    image_data = {
        "image_url": "https://example.com/sunset_beach.jpg",
        "content": "Beautiful sunset at the beach",
        "tags": [1, 2],
    }

    # Assuming you have an existing image ID to update
    image_id_to_update = 1

    # Update the image
    response = client.put(
        f"/api/images/{image_id_to_update}",
        json=image_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 200
    ), response.text  # Adjust the status code as per your API design
    updated_data = response.json()
    assert updated_data["image_url"] == image_data["image_url"]
    assert updated_data["id"] == image_id_to_update


@patch("src.utils.image_utils.get_cloudinary_image_transformation")
def test_transform_image(mock_cloudinary_transformation, mock_redis, client, user):
    # Setup the mock return value
    mock_cloudinary_transformation.return_value = (
        "https://example.com/transformed_image.jpg"
    )
    # Authenticate user and get token
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Prepare transformation data
    image_data = {
        "image_url": "https://example.com/waifu.jpg",
        "transformation_type": "resize",
        "width": 100,
        "height": 100,
    }

    # Send request to transform image
    response = client.post(
        "/api/images/transform_image/",
        params={
            "image_url": image_data["image_url"],
            "transformation_type": image_data["transformation_type"],
            "width": image_data["width"],
            "height": image_data["height"],
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert response.status_code == 200, response.text
    transformed_data = response.json()
    assert transformed_data["image_url"] == image_data["image_url"]
    assert transformed_data["image_transformed_url"] != None
    assert transformed_data["qr_code"] != None

    # Prepare transformation data
    image_data = {
        "image_url": "https://example.com/waifu.jpg",
        "transformation_type": "crop",
        "width": 100,
        "height": 100,
    }

    # Send request to transform image
    response = client.post(
        "/api/images/transform_image/",
        params={
            "image_url": image_data["image_url"],
            "transformation_type": image_data["transformation_type"],
            "width": image_data["width"],
            "height": image_data["height"],
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert response.status_code == 200, response.text
    transformed_data = response.json()
    assert transformed_data["image_url"] == image_data["image_url"]
    assert transformed_data["image_transformed_url"] != None
    assert transformed_data["qr_code"] != None

    # Prepare transformation data
    image_data = {
        "image_url": "https://example.com/waifu.jpg",
        "transformation_type": "effect",
        "effect": "blur",
    }

    # Send request to transform image
    response = client.post(
        "/api/images/transform_image/",
        params={
            "image_url": image_data["image_url"],
            "transformation_type": image_data["transformation_type"],
            "effect": image_data["effect"],
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert response.status_code == 200, response.text
    transformed_data = response.json()
    assert transformed_data["image_url"] == image_data["image_url"]
    assert transformed_data["image_transformed_url"] != None
    assert transformed_data["qr_code"] != None

    # Prepare transformation data
    image_data = {
        "image_url": "https://example.com/waifu.jpg",
        "transformation_type": "overlay",
    }

    # Send request to transform image
    response = client.post(
        "/api/images/transform_image/",
        params={
            "image_url": image_data["image_url"],
            "transformation_type": image_data["transformation_type"],
            "overlay_public_id": "https://res.cloudinary.com/dyltcsbtk/image/upload/c_fill,h_250,w_250/v1700416105/SnapShare-API/TolbyOwl6",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert response.status_code == 200, response.text
    transformed_data = response.json()
    assert transformed_data["image_url"] == image_data["image_url"]
    assert transformed_data["image_transformed_url"] != None
    assert transformed_data["qr_code"] != None

    # Prepare transformation data
    image_data = {
        "image_url": "https://example.com/waifu.jpg",
        "transformation_type": "face_detect",
        "width": 100,
        "height": 100,
    }

    # Send request to transform image
    response = client.post(
        "/api/images/transform_image/",
        params={
            "image_url": image_data["image_url"],
            "transformation_type": image_data["transformation_type"],
            "width": image_data["width"],
            "height": image_data["height"],
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert response.status_code == 200, response.text
    transformed_data = response.json()
    assert transformed_data["image_url"] == image_data["image_url"]
    assert transformed_data["image_transformed_url"] != None
    assert transformed_data["qr_code"] != None


def test_get_images(client, user, monkeypatch, mock_redis):
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Retrieve the images
    response = client.get(
        "/api/images/",  # Replace with your actual endpoint for getting images
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 200
    ), response.text  # Adjust the status code as per your API design
    images = response.json()
    # Here you might want to assert specifics about the images
    # For example, if you're expecting certain images to be returned for this user, you can check those
    assert isinstance(images, list)  # Check if the response is a list
    # Add more assertions as needed, based on your application's logic and requirements


@patch("src.repository.images.get_image")
def test_get_transform_image_url(mock_get_image, client):
    # Mocking a transformed image
    mock_image = Mock()
    mock_image.image_url = "https://example.com/waifu.jpg"
    mock_image.image_transformed_url = "https://example.com/transformed_waifu.jpg"
    mock_image.qr_code = "Some QR Code Data"
    mock_get_image.return_value = mock_image

    # Test valid image retrieval
    response = client.get("/api/images/transformed_image/1")
    assert response.status_code == 200
    data = response.json()
    assert data["image_url"] == mock_image.image_url
    assert data["image_transformed_url"] == mock_image.image_transformed_url
    assert data["qr_code"] != None

    # Test image not found scenario
    mock_get_image.return_value = None
    response = client.get("/api/images/transformed_image/2")
    assert response.status_code == 404


def test_add_tag(client, user, monkeypatch, mock_redis):
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Prepare the tag data
    tag_data = {
        "id": -1,
        "image_id": 1,  # Replace with a valid image ID
        "tag": "NewTag",
    }

    # Add the tag to the image
    response = client.patch(
        "/api/images/add_tags",  # Replace with your actual endpoint for adding tags
        json=tag_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 200
    ), response.text  # Adjust the status code as per your API design
    updated_image = response.json()
    # Verify that the tag was added
    assert any(tag["name"] == tag_data["tag"] for tag in updated_image["tags"])


def test_delete_image(client, user, monkeypatch, mock_redis):
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Delete the image
    response = client.delete(
        f"/api/images/1",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 204
    ), response.text  # Adjust the status code as per your API design
