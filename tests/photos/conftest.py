

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI

from main import app  # Import your FastAPI app instance
from src.models.base import Base
from src.database.db import get_db
from src.services.auth_service import Auth
from src.models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def async_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_session = TestingSessionLocal()
    try:
        yield async_session
    finally:
        await async_session.close()


@pytest.fixture(scope="function")
async def override_get_db(async_session):
    async def _get_db_override():
        async with async_session() as session:
            yield session

    return _get_db_override


@pytest.fixture
def app_with_overrides(override_get_db):
    # Dependency overrides
    app.dependency_overrides[get_db] = override_get_db

    # Create a mock user or use a fixture for a real user
    test_user = User(id=1, username="testuser", email="test@example.com")

    async def get_current_user_override():
        return test_user

    app.dependency_overrides[Auth.get_current_user] = get_current_user_override

    return app


@pytest.fixture
async def client(app=app) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }
