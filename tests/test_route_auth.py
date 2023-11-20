import pytest
from datetime import datetime, timedelta
from typing import Optional
from fastapi import status
import unittest
from unittest.mock import MagicMock, patch, ANY
from unittest import mock

from jose import JWTError, jwt
from pytest_mock import mocker

from src.models.user import User
from src.services.auth_service import auth_service
from src.routes.auth import send_email
from src.repository import users as repository_users
from src.conf.config import settings


def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() - timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow() - timedelta(days=14),
                      "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(
        to_encode, settings.secret_key, algorithm='HS256')
    return encoded_refresh_token


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_confirmed_email_is_already_confirmed(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    token_verification = auth_service.create_email_token(
        {"sub": user.get('email')})
    response = client.get(f"/api/auth/confirmed_email?token={token_verification}",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_confirmed_email_bad_request(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()

    token_verification = auth_service.create_email_token(
        {"sub": 'AAA' + user.get('email')})
    response = client.get(f"/api/auth/confirmed_email?token={token_verification}",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error"


def test_confirmed_email_confirmed(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    token_verification = auth_service.create_email_token(
        {"sub": user.get('email')})
    response = client.get(f"/api/auth/confirmed_email?token={token_verification}",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"


def test_refresh_token(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()

    token_verification = current_user.refresh_token
    response = client.get(f"/api/auth/refresh_token",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_refresh_token_could_not_validate_credential(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    token_verification = create_refresh_token({"sub": user.get('email')})
    response = client.get(f"/api/auth/refresh_token",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Could not validate credentials"


def test_refresh_token_invalid_scope_for_token(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    token_verification = auth_service.create_email_token(
        {"sub": user.get('email')})
    response = client.get(f"/api/auth/refresh_token",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid scope for token"


def test_refresh_token_invalid_refresh_token(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()

    token_verification = current_user.refresh_token
    current_user.refresh_token = create_refresh_token(
        {"sub": user.get('email')}, 14)
    session.commit()

    response = client.get(f"/api/auth/refresh_token",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid refresh token"


def test_login_user_ban_status(client, session, user):
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    current_user.confirmed = True
    current_user.ban_status = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Your account is banned"
    print(data["detail"])


def test_protected_endpoint_with_valid_token(client, user, monkeypatch):
    token = auth_service.create_access_token(data={"sub": user.get('email')})

    response = client.get("/api/auth/protected_endpoint", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "This is a protected endpoint"


def test_protected_endpoint_without_token(client):
    response = client.get("/api/auth/protected_endpoint")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_protected_endpoint_with_invalid_token(client):
    with patch("src.routes.auth.repository_users.find_black_list_token") as mock_find_black_list_token:
        mock_find_black_list_token.return_value = True

        response = client.get("/api/auth/protected_endpoint", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Token is blacklisted"

        mock_find_black_list_token.assert_called_once_with("invalid_token", ANY)


def test_protected_endpoint_with_blacklisted_token(client, user, mock_find_black_list_token):
    token = auth_service.create_access_token(data={"sub": user.get('email')})
    mock_find_black_list_token.return_value = True

    response = client.get("/api/auth/protected_endpoint", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Token is blacklisted"

#
# def test_forgot_password(client, user, monkeypatch):
#     mock_send_email = MagicMock()
#     monkeypatch.setattr("src.routes.auth.send_email_reset_password", mock_send_email)
#
#     with patch("src.routes.auth.repository_users.get_user_by_email") as mock_get_user_by_email:
#         mock_get_user_by_email.return_value = user
#         # print(user)
#         test_email = user.get('email')
#
#         response = client.get(f"/api/auth/forgot_password?{test_email}")
#
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert "message" in data
#     assert mock_send_email.called
#     assert mock_get_user_by_email.called_once_with({test_email}, ANY)
