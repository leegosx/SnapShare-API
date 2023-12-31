import pickle
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

from main import app
from src.models.base import Base
from src.models.user import User
from src.database.db import get_db
from tests.users.test_data_func import create_test_user

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        # Create random users
        user = create_test_user(db)

        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool",
            "email": "deadpool@example.com",
            "password": "123456789",
            "ban_status": "False"}


@pytest.fixture(scope="function")
def mock_redis(monkeypatch):
    # Create a fake user object as you would expect it to be after unpickling
    fake_user = {"username": "deadpool", "email": "deadpool@example.com", "password": "123456789"}

    # Mock Redis get method to return a pickled fake user
    monkeypatch.setattr(
        "redis.StrictRedis.get",
        lambda self, name: pickle.dumps(fake_user)
        if name == f"user:{fake_user['email']}"
        else None,
    )

    # Mock Redis set method to do nothing
    monkeypatch.setattr("redis.StrictRedis.set", lambda *args, **kwargs: None)


class TestUser:
    def __init__(self, id, username, email, avatar, role, password, confirmed):
        self.id = id
        self.username = username
        self.email = email
        self.avatar = avatar
        self.role = role
        self.password = password
        self.confirmed = confirmed


@pytest.fixture(scope="module")
def testuser():
    return {
        "username": "testuser",
        "email": "tester123@example.com",
        "avatar": "default.jpg",
        "role": "user",
        "uploaded_photos": 3,
        "password": "ptn_pnh123",
        "confirmed": True,
    }


@pytest.fixture(scope="function")
def mock_redis_for_testuser(monkeypatch):
    # Create a fake user object as you would expect it to be after unpickling
    fake_user = {
        "username": "testuser",
        "email": "tester123@example.com",
        "avatar": "default.jpg",
        "role": "user",
        "uploaded_photos": 3,
        "password": "ptn_pnh123",
        "confirmed": True,
    }

    # Mock Redis get method to return a pickled fake user
    monkeypatch.setattr(
        "redis.StrictRedis.get",
        lambda self, name: pickle.dumps(fake_user)
        if name == f"user:{fake_user['email']}"
        else None,
    )

    # Mock Redis set method to do nothing
    monkeypatch.setattr("redis.StrictRedis.set", lambda *args, **kwargs: None)


@pytest.fixture(scope="module")
def token(client, user):
    response = client.post("/api/auth/login", data={"username": user["email"], "password": user["password"]})
    assert response.status_code == 200, response.text
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="module")
def mock_save_black_list_token():
    async def mock_save_black_list_token_async(token, current_user, db):
        return MagicMock()

    return mock_save_black_list_token_async


@pytest.fixture(scope="module")
def logged_in_user(client, user):
    response = client.post("/api/auth/login", data={"username": user["email"], "password": user["password"]})
    assert response.status_code == 200, response.text
    data = response.json()
    return data["access_token"]


@pytest.fixture
def mock_find_black_list_token(monkeypatch):
    with patch("src.routes.auth.repository_users.find_black_list_token") as mock_find_black_list_token:
        yield mock_find_black_list_token
