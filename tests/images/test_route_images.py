import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_create_image(client, user, monkeypatch, mock_redis):
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    created_image_data = {
        "image_url": "https://example.com/sunset_beach.jpg",
        "content": "Beautiful sunset at the beach",
        "tags": [1, 2],
    }

    # Create the image with authentication
    response = client.post(
        "/api/images/create_new",  # Add leading slash to the endpoint path
        json=created_image_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code
        == 201  # Expecting '201 Created' or appropriate success code
    ), response.text
    data = response.json()
    assert data["image_url"] == created_image_data["image_url"]
    assert "id" in data

    # Retrieve the image
    response = client.get(f"/api/images/{data['id']}")

    # Verify the response
    assert response.status_code == 200, response.text
    image_data = response.json()
    assert (
        image_data["image_url"] == created_image_data["image_url"]
    )  # Verify the image data
    # Add more assertions as necessary, for example, checking other fields of the image


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
        'id':-1,
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
