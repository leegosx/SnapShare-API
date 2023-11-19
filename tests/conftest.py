import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

from main import app
from src.models.base import Base
from src.database.db import get_db
from src.repository import users as repository_users

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
            }


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


