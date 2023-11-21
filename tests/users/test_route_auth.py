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
    """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

    :param data: dict: Pass the data that will be encoded into the token
    :param expires_delta: Optional[float]: Set the expiration time of the token
    :return: A jwt token with the payload
    :doc-author: Trelent
    """
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
    """
    The test_create_user function tests the /api/auth/signup endpoint.
    It does so by creating a user and then checking that the response is 201 (created)
    and that the email address of the created user matches what was sent in.

    :param client: Make requests to the api
    :param user: Pass the user data to the test function
    :param monkeypatch: Mock the send_email function
    :return: A 201 status code and the user's email address
    :doc-author: Trelent
    """
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
    """
    The test_repeat_create_user function tests that a user cannot be created twice.
    It does this by creating a user, then attempting to create the same user again.
    The second attempt should fail with an HTTP 409 status code.

    :param client: Make requests to the api
    :param user: Pass in the user object created by the fixture
    :return: A 409 status code and a message about the account already existing
    :doc-author: Trelent
    """
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    """
    The test_login_user_not_confirmed function tests that a user cannot login if they have not confirmed their email.
    The test_login_user_not_confirmed function takes in the client and user fixtures as parameters.
    The response variable is assigned to the result of calling client's post method with &quot;/api/auth/login&quot; as an argument,
    and data={&quot;username&quot;: user.get('email'), &quot;password&quot;: user.get('password')} as keyword arguments.

    :param client: Make requests to the application
    :param user: Get the user data from the fixture
    :return: A 401 status code and the message &quot;email not confirmed&quot;
    :doc-author: Trelent
    """
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    """
    The test_login_user function tests the login endpoint.
    It does this by first creating a user, then confirming that user's account.
    Then it sends a POST request to the /api/auth/login endpoint with the email and password of that user as data in JSON format.
    The response is checked for status code 200 (OK) and then its JSON content is checked for token_type &quot;bearer&quot;.

    :param client: Make requests to the application
    :param session: Create a new user in the database
    :param user: Pass in the user fixture
    :return: A bearer token that can be used to authenticate the user
    :doc-author: Trelent
    """
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
    """
    The test_login_wrong_password function tests the login endpoint with a wrong password.
    It should return a 401 status code and an error message.

    :param client: Make requests to the flask application
    :param user: Pass the user fixture into the test function
    :return: A 401 status code and an error message
    :doc-author: Trelent
    """
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    """
    The test_login_wrong_email function tests that the login endpoint returns a 401 status code and an error message when
    the user enters an invalid email address. The test_login_wrong_email function takes in two arguments: client, which is
    a fixture that allows us to make requests to our application, and user, which is a fixture that contains the data for
    our test user.

    :param client: Make requests to the flask application
    :param user: Create a user in the database
    :return: 401 status code and invalid email message
    :doc-author: Trelent
    """
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_confirmed_email_is_already_confirmed(client, user, monkeypatch):
    """
    The test_confirmed_email_is_already_confirmed function tests the confirmed_email endpoint.
    It checks that if a user tries to confirm their email again, they will get an error message saying that their email is already confirmed.

    :param client: Make requests to the application
    :param user: Create a user in the database
    :param monkeypatch: Mock the send_email function
    :return: A message
    :doc-author: Trelent
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    token_verification = auth_service.create_email_token(
        {"sub": user.get('email')})
    response = client.get(f"/api/auth/confirmed_email/{token_verification}",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_confirmed_email_bad_request(client, user, session, monkeypatch):
    """
    The test_confirmed_email_bad_request function tests the confirmed_email endpoint.
    It does this by first creating a mock of the send_email function, which is used in the confirmed_email endpoint.
    Then it sets up a user with an unconfirmed email address and commits that to our database session.
    Next, it creates a token for verification using auth_service's create_email token method and passes in an invalid email address (AAA + valid email).
    Finally, we make sure that when we call client on /api/auth/confirmed-mail?token={token} with our invalid token as part of the query string,
    we

    :param client: Make a request to the api
    :param user: Create a user in the database
    :param session: Create a session for the test
    :param monkeypatch: Mock the send_email function
    :return: A 400 error and the message &quot;verification error&quot;
    :doc-author: Trelent
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()

    token_verification = auth_service.create_email_token(
        {"sub": 'AAA' + user.get('email')})
    response = client.get(f"/api/auth/confirmed_email/{token_verification}",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error"


def test_confirmed_email_confirmed(client, user, monkeypatch):
    """
    The test_confirmed_email_confirmed function tests the confirmed_email endpoint.
    It does so by creating a mock email token, and then sending it to the endpoint.
    The test checks that the response is 200 OK, and that it contains a message saying &quot;Email confirmed&quot;.

    :param client: Make requests to the api
    :param user: Create a user in the database
    :param monkeypatch: Mock the send_email function
    :return: A 200 status code and the message &quot;email confirmed&quot;
    :doc-author: Trelent
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    token_verification = auth_service.create_email_token(
        {"sub": user.get('email')})
    response = client.get(f"/api/auth/confirmed_email/{token_verification}",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"


def test_refresh_token(client, session, user, monkeypatch):
    """
    The test_refresh_token function tests the refresh_token endpoint.
    It does this by first creating a mock of the send_email function, which is used in the refresh_token endpoint.
    Then it queries for a user with an email that matches one of our test users and assigns it to current_user.
    Next, we assign token verification to be equal to current user's refresh token (which is generated when they sign up).
    Finally, we make a get request on /api/auth/refresh-token using our authorization header containing our bearer token as well as passing in data from one of our test users.

    :param client: Make requests to the application
    :param session: Create a new session for the test
    :param user: Create a user in the database
    :param monkeypatch: Mock the send_email function
    :return: A token type of bearer
    :doc-author: Trelent
    """
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
    """
    The test_refresh_token_could_not_validate_credential function tests the /api/auth/refresh_token endpoint.
    The test_refresh_token_could_not_validate_credential function is a unit test that checks if the refresh token could not validate credentials.

    :param client: Make a request to the api
    :param user: Create a user in the database
    :param monkeypatch: Mock the send_email function
    :return: A 401 error code and the message &quot;could not validate credentials&quot;
    :doc-author: Trelent
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    token_verification = create_refresh_token({"sub": user.get('email')})
    response = client.get(f"/api/auth/refresh_token",
                          headers={"Authorization": f"Bearer {token_verification}"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Could not validate credentials"


def test_refresh_token_invalid_scope_for_token(client, user, monkeypatch):
    """
    The test_refresh_token_invalid_scope_for_token function tests the refresh_token endpoint.
    It does this by first creating a token with an invalid scope, and then attempting to use that token to access the refresh_token endpoint.
    The test asserts that the response status code is 401 (Unauthorized), and also asserts that the detail field of data returned in JSON format is &quot;Invalid scope for token&quot;.


    :param client: Create a client that can be used to make requests to the application
    :param user: Get the user's email address
    :param monkeypatch: Mock the send_email function
    :return: A 401 status code, the text of which is invalid scope for token
    :doc-author: Trelent
    """
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
    """
    The test_refresh_token_invalid_refresh_token function tests the refresh_token endpoint with an invalid refresh token.
    The test_refresh_token_invalid_refresh_token function is a unit test that uses the pytest framework to verify that when a user attempts to use an invalid refresh token, they will receive a 401 status code and &quot;Invalid refresh token&quot; error message.

    :param client: Send a request to the api
    :param session: Create a new session for the test
    :param user: Create a user in the database
    :param monkeypatch: Mock the send_email function
    :return: A 401 status code and an error message
    :doc-author: Trelent
    """
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
    """
    The test_login_user_ban_status function tests the login endpoint with a banned user.
        It first queries the database for the current_user, sets their confirmed and ban_status attributes to True, commits those changes to the database, then sends a POST request to /api/auth/login with that user's email and password as data.
        The response is checked for status code 403 (Forbidden) and its JSON payload is checked for detail &quot;Your account is banned&quot;.


    :param client: Make a request to the api
    :param session: Create a new user in the database
    :param user: Create a user in the database
    :return: 403 status code and &quot;your account is banned&quot; message
    :doc-author: Trelent
    """
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
    """
    The test_protected_endpoint_with_valid_token function tests that a user with a valid token can access the protected endpoint.
    It does this by creating an access token for the user, then making a request to the /api/auth/protected_endpoint endpoint using
    the created token as an Authorization header. The response is checked to ensure it has status code 200 and contains
    a message of &quot;This is a protected endpoint&quot;.

    :param client: Make requests to the flask application
    :param user: Create a valid token
    :param monkeypatch: Mock the current_user function in auth
    :return: A 200 status code and a message
    :doc-author: Trelent
    """
    token = auth_service.create_access_token(data={"sub": user.get('email')})

    response = client.get("/api/auth/protected_endpoint", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "This is a protected endpoint"


def test_protected_endpoint_without_token(client):
    """
    The test_protected_endpoint_without_token function tests that the /api/auth/protected_endpoint endpoint returns a 401 Unauthorized response when no token is provided.

    :param client: Make a request to the api
    :return: A 401 status code and a message
    :doc-author: Trelent
    """
    response = client.get("/api/auth/protected_endpoint")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_protected_endpoint_with_invalid_token(client):
    """
    The test_protected_endpoint_with_invalid_token function tests the /api/auth/protected_endpoint endpoint.
    It does so by first patching the find_black_list_token function in src.routes.auth.repository_users to return True,
    which means that the token is blacklisted and therefore invalid for use with this endpoint (and any other).
    The test then makes a GET request to /api/auth/protected_endpoint using an Authorization header containing an invalid token,
    and asserts that it receives a 401 Unauthorized response from Flask-RESTx.

    :param client: Make a request to the flask application
    :return: The status code 401 and the message &quot;token is blacklisted&quot;
    :doc-author: Trelent
    """
    with patch("src.routes.auth.repository_users.find_black_list_token") as mock_find_black_list_token:
        mock_find_black_list_token.return_value = True

        response = client.get("/api/auth/protected_endpoint", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Token is blacklisted"

        mock_find_black_list_token.assert_called_once_with("invalid_token", ANY)


def test_protected_endpoint_with_blacklisted_token(client, user, mock_find_black_list_token):
    """
    The test_protected_endpoint_with_blacklisted_token function tests that a blacklisted token is not allowed to access the protected endpoint.
    It does this by first creating a valid token, then mocking the find_black_list_token function to return True (meaning it's blacklisted).
    Then it makes an HTTP request with the mocked token and asserts that we get back an unauthorized response.

    :param client: Make a request to the api
    :param user: Create a user in the database
    :param mock_find_black_list_token: Mock the find_black_list_token function
    :return: A 401 status code and a message that the token is blacklisted
    :doc-author: Trelent
    """
    token = auth_service.create_access_token(data={"sub": user.get('email')})
    mock_find_black_list_token.return_value = True

    response = client.get("/api/auth/protected_endpoint", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Token is blacklisted"
