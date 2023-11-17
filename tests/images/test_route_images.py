import sys
import os
import json
from starlette.datastructures import UploadFile
import unittest
from unittest.mock import patch, MagicMock


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


# class TestCreateImage(unittest.TestCase):
#     @patch("cloudinary.uploader.upload")
#     @patch("tests.images.conftest.mock_redis")
#     def test_create_image(
#         client, user, mock_redis, mock_cloudinary_upload
#     ):
#         # Authenticate the user
#         login_response = client.post(
#             "/api/auth/login",
#             data={
#                 "username": user["email"],
#                 "password": user["password"],
#             },
#         )
#         assert login_response.status_code == 200, login_response.text
#         login_data = login_response.json()
#         user_token = login_data["access_token"]

#         # Mock Cloudinary upload response
#         mock_cloudinary_upload.return_value = {
#             "public_id": "test_public_id",
#             "version": "1234",
#         }

#         # Mock file upload
#         mocked_file = MagicMock(spec=UploadFile)
#         mocked_file.filename = "test_image.jpg"
#         mocked_file.file = MagicMock()
#         mocked_file.file.read = MagicMock(return_value=b"fake image data")
#         mocked_file.content_type = "image/jpeg"

#         # Prepare the request with the mock file
#         files = {"file": mocked_file}
#         body_data = {
#             "content": "Beautiful sunset at the beach",
#             "tags": json.dumps([1, 2, 3]),
#         }

#         # Create the image with authentication
#         response = client.post(
#             "/api/images/create_new",
#             files={
#                 "file": (
#                     mocked_file.filename,
#                     mocked_file.file.read(),
#                     mocked_file.content_type,
#                 )
#             },
#             params=body_data,  # Assuming body_data is prepared as before
#             headers={"Authorization": f"Bearer {user_token}"},
#         )

#         # Verify the response
#         assert response.status_code == 201, response.text
#         data = response.json()
#         assert "image_url" in data  # Now the URL is generated in the function
#         assert "id" in data

#         # Retrieve the image
#         response = client.get(f"/api/images/{data['id']}")

#         # Verify the response
#         assert response.status_code == 200, response.text
#         image_data = response.json()
#         assert "image_url" in image_data  # Again, verify the URL is present


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
