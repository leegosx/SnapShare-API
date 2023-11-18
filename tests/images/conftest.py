import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


import cloudinary
import pytest
import pickle
from main import app

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings


from src.database.db import get_db
from src.models.base import Base
from src.models.user import User
from tests.images.test_data_func import *


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


@pytest.fixture(scope="function")
def mock_redis(monkeypatch):
    # Create a fake user object as you would expect it to be after unpickling
    fake_user = User(
        username="testuser",
        email="tester123@example.com",
        password="ptn_pnh123",
        id=1,
        confirmed=True,
    )

    # Mock Redis get method to return a pickled fake user
    monkeypatch.setattr(
        "redis.StrictRedis.get",
        lambda self, name: pickle.dumps(fake_user)
        if name == f"user:{fake_user.email}"
        else None,
    )

    # Mock Redis set method to do nothing
    monkeypatch.setattr("redis.StrictRedis.set", lambda *args, **kwargs: None)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        # Create random users
        user = create_test_user_and_test_image(db)

        # Create random tags
        tags = create_random_tags(db)

        # Create random images for each user
        create_random_images_for_user(db, user, tags)

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
    return {
        "username": "testuser",
        "email": "tester123@example.com",
        "password": "ptn_pnh123",
        "id": 1,
        "confirmed": True,
    }
