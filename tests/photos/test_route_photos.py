import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_create_photo(client, user, monkeypatch, mock_redis):
    """
    The test_create_photo function tests the following:
    - Authenticates a user and retrieves an access token.
    - Creates a new photo with the authenticated user's access token.
    - Verifies that the response is successful (201 Created).
    - Retrieves the created photo by ID and verifies that it was created successfully.
    
    :param client: Make requests to the flask app
    :param user: Create a user in the database
    :param monkeypatch: Mock the redis cache
    :param mock_redis: Mock the redis cache
    :return: A 201 status code, which is the expected response
    :doc-author: Trelent
    """
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

    created_photo_data = {
        "image_url": "https://example.com/sunset_beach.jpg",
        "content": "Beautiful sunset at the beach",
        "tags": [1, 2],
    }

    # Create the photo with authentication
    response = client.post(
        "/api/photos/create_new",  # Add leading slash to the endpoint path
        json=created_photo_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code
        == 201  # Expecting '201 Created' or appropriate success code
    ), response.text
    data = response.json()
    assert data["image_url"] == created_photo_data["image_url"]
    assert "id" in data

    # Retrieve the photo
    response = client.get(f"/api/photos/{data['id']}")

    # Verify the response
    assert response.status_code == 200, response.text
    photo_data = response.json()
    assert (
        photo_data["image_url"] == created_photo_data["image_url"]
    )  # Verify the photo data
    # Add more assertions as necessary, for example, checking other fields of the photo


def test_update_photo(client, user, monkeypatch, mock_redis):
    """
    The test_update_photo function tests the following:
    - Authenticates a user and obtains an access token.
    - Prepares photo update data.
    - Updates a photo using the obtained access token and verifies that the response is successful.
    
    :param client: Make requests to the api
    :param user: Create a user for the test
    :param monkeypatch: Mock the redis client
    :param mock_redis: Mock the redis connection
    :return: The following:
    :doc-author: Trelent
    """
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Prepare the photo update data
    photo_data = {
        "image_url": "https://example.com/sunset_beach.jpg",
        "content": "Beautiful sunset at the beach",
        "tags": [1, 2],
    }

    # Assuming you have an existing photo ID to update
    photo_id_to_update = 1

    # Update the photo
    response = client.put(
        f"/api/photos/{photo_id_to_update}",
        json=photo_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 200
    ), response.text  # Adjust the status code as per your API design
    updated_data = response.json()
    assert updated_data["image_url"] == photo_data["image_url"]
    assert updated_data["id"] == photo_id_to_update


def test_get_photos(client, user, monkeypatch, mock_redis):
    """
    The test_get_photos function tests the following:
    - User can login and get a token
    - User can use that token to retrieve photos
    
    :param client: Make requests to the flask app
    :param user: Create a user in the database
    :param monkeypatch: Mock the redis connection
    :param mock_redis: Mock the redis cache
    :return: A list of photos
    :doc-author: Trelent
    """
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Retrieve the photos
    response = client.get(
        "/api/photos/",  # Replace with your actual endpoint for getting photos
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 200
    ), response.text  # Adjust the status code as per your API design
    photos = response.json()
    # Here you might want to assert specifics about the photos
    # For example, if you're expecting certain photos to be returned for this user, you can check those
    assert isinstance(photos, list)  # Check if the response is a list
    # Add more assertions as needed, based on your application's logic and requirements


def test_add_tag(client, user, monkeypatch, mock_redis):
    """
    The test_add_tag function tests the following:
    - Authenticates a user using their email and password.
    - Adds a tag to an existing photo.
    
    
    :param client: Make requests to the api
    :param user: Create a new user in the database
    :param monkeypatch: Mock the redis cache
    :param mock_redis: Mock the redis connection
    :return: A 200 status code
    :doc-author: Trelent
    """
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
        "photo_id": 1,  # Replace with a valid photo ID
        "tag": "NewTag",
    }

    # Add the tag to the photo
    response = client.patch(
        "/api/photos/add_tags",  # Replace with your actual endpoint for adding tags
        json=tag_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 200
    ), response.text  # Adjust the status code as per your API design
    updated_photo = response.json()
    # Verify that the tag was added
    assert any(tag["name"] == tag_data["tag"] for tag in updated_photo["tags"])


def test_delete_photo(client, user, monkeypatch, mock_redis):
    """
    The test_delete_photo function tests the DELETE /api/photos/{photo_id} endpoint.
    
    :param client: Make requests to the api
    :param user: Create a user in the database
    :param monkeypatch: Mock the redis
    :param mock_redis: Mock the redis connection
    :return: A 204 status code
    :doc-author: Trelent
    """
    # Authenticate the user
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]

    # Delete the photo
    response = client.delete(
        f"/api/photos/1",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Verify the response
    assert (
        response.status_code == 204
    ), response.text  # Adjust the status code as per your API design
