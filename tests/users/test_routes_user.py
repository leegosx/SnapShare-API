import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from io import BytesIO
from tests.users.test_data_func import *
from unittest.mock import MagicMock, patch
from fastapi import UploadFile
from src.services.auth_service import Auth

auth_service = Auth()

def test_read_users_me(client, testuser, monkeypatch, mock_redis_for_testuser):
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": testuser["email"],
            "password": testuser["password"],
        },
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]
    response = client.get(
        "/api/users/me/",  
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == testuser["email"]
    
    
def test_read_users_me_unauth(client, user, monkeypatch, mock_redis):
    response = client.get("api/users/me/")
    assert response.status_code == 401


def test_read_users_me_invalid_token(client, user, monkeypatch):
    # Arrange
    monkeypatch.setattr(auth_service, "get_current_user", lambda: None)
    
    # Act
    response = client.get("api/users/me/")

    # Assert
    assert response.status_code == 401
    
def test_get_user_profile_success(client, testuser, session):
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": testuser["email"],
            "password": testuser["password"],
        },
    )
    assert login_response.status_code == 200, login_response.text
    login_data = login_response.json()
    user_token = login_data["access_token"]
    response = client.get(
        f"/api/users/profile/{testuser['username']}",
        headers={"Authorization": f"Bearer {user_token}"
            }
        )

    data = response.json()

    assert response.status_code == 200
    # assert data['email'] == testuser['email']
    assert data['username'] == testuser['username']
    assert data['avatar'] == testuser['avatar']

def test_get_user_profile_not_found(client):
    response = client.get("/profile/nonexistent@example.com")
    assert response.status_code == 404

def test_change_username_unauth(client, user, session, mock_redis):
    response = client.patch(
        f"/api/users/change/{user['username']}",
        json={"username": "new_username"},
    )
    
    assert response.status_code == 401, response.text