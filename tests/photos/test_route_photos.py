import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from tests.photos.test_data_func import test_photo, test_user


def test_create_photo(client, user, monkeypatch):
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        json={"username": test_user["username"], "password": test_user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Prepare the photo data
    photo_data = {
        "image_url": "https://example.com/sunset_beach.jpg",
        "content": "Beautiful sunset at the beach",
        # Add other fields as required by your PhotoCreate schema
    }

    # Create the photo with authentication
    response = client.post(
        "/create_new",
        json=photo_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 200
    ), response.text  # Adjust the status code as per your API design
    data = response.json()
    assert data["image_url"] == photo_data["image_url"]
    assert "id" in data


# def test_update_photo(client, user, monkeypatch):
#     # Authenticate the user
#     login_response = client.post(
#         "/api/auth/login",
#         json={"username": test_user["username"], "password": test_user["password"]},
#     )
#     assert login_response.status_code == 200, login_response.text
#     login_data = login_response.json()
#     user_token = login_data["access_token"]

#     # Prepare the photo update data
#     photo_update_data = {
#         "content": "Updated description of the photo",
#     }

#     # Assuming you have an existing photo ID to update
#     photo_id_to_update = "1"

#     # Update the photo
#     response = client.put(
#         f"/{photo_id_to_update}",
#         json=photo_update_data,
#         headers={"Authorization": f"Bearer {user_token}"},
#     )

#     # Verify the response
#     assert (
#         response.status_code == 200
#     ), response.text  # Adjust the status code as per your API design
#     updated_data = response.json()
#     assert updated_data["content"] == photo_update_data["content"]
#     assert updated_data["id"] == photo_id_to_update


# def test_get_photo(client):
#     # Assuming you have a photo URL to test
#     photo_url_to_retrieve = test_photo["image_url"]

#     # Retrieve the photo
#     response = client.get(f"/{photo_url_to_retrieve}")

#     # Verify the response
#     assert response.status_code == 200, response.text
#     photo_data = response.json()
#     assert photo_data["image_url"] == photo_url_to_retrieve  # Verify the photo data
#     # Add more assertions as necessary, for example, checking other fields of the photo


# def test_get_photos(client, user, monkeypatch):
#     # Authenticate the user
#     login_response = client.post(
#         "/api/auth/login",
#         json={"username": test_user["username"], "password": test_user["password"]},
#     )
#     assert login_response.status_code == 200, login_response.text
#     login_data = login_response.json()
#     user_token = login_data["access_token"]

#     # Retrieve the photos
#     response = client.get(
#         "/photos",  # Replace with your actual endpoint for getting photos
#         headers={"Authorization": f"Bearer {user_token}"},
#     )

#     # Verify the response
#     assert (
#         response.status_code == 200
#     ), response.text  # Adjust the status code as per your API design
#     photos = response.json()
#     # Here you might want to assert specifics about the photos
#     # For example, if you're expecting certain photos to be returned for this user, you can check those
#     assert isinstance(photos, list)  # Check if the response is a list
#     # Add more assertions as needed, based on your application's logic and requirements


# def test_add_tag(client, user, monkeypatch):
#     # Authenticate the user
#     login_response = client.post(
#         "/api/auth/login",
#         json={"username": test_user["username"], "password": test_user["password"]},
#     )
#     assert login_response.status_code == 200, login_response.text
#     login_data = login_response.json()
#     user_token = login_data["access_token"]

#     # Prepare the tag data
#     tag_data = {
#         "image_id": test_photo["image_url"],  # Replace with a valid photo ID
#         "tag": "NewTag",
#     }

#     # Add the tag to the photo
#     response = client.patch(
#         "/add_tags",  # Replace with your actual endpoint for adding tags
#         json=tag_data,
#         headers={"Authorization": f"Bearer {user_token}"},
#     )

#     # Verify the response
#     assert (
#         response.status_code == 200
#     ), response.text  # Adjust the status code as per your API design
#     updated_photo = response.json()
#     # Verify that the tag was added
#     assert any(tag["name"] == tag_data["tag"] for tag in updated_photo["tags"])


# def test_delete_photo(client, user, monkeypatch):
#     # Authenticate the user
#     login_response = client.post(
#         "/api/auth/login",
#         json={"username": test_user["username"], "password": test_user["password"]},
#     )
#     assert login_response.status_code == 200, login_response.text
#     login_data = login_response.json()
#     user_token = login_data["access_token"]

#     # Assuming you have a photo URL to delete
#     photo_url_to_delete = test_photo["image_url"]

#     # Delete the photo
#     response = client.delete(
#         f"/{photo_url_to_delete}", headers={"Authorization": f"Bearer {user_token}"}
#     )

#     # Verify the response
#     assert (
#         response.status_code == 200
#     ), response.text  # Adjust the status code as per your API design
#     # Optionally verify response content if your API returns data upon deletion
#     deleted_data = response.json()
#     assert deleted_data is None
