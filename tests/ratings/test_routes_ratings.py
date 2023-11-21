import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from src.database.db import get_db
from src.models.user import User
from src.models.image import Image
from src.schemas.rating import RatingRequest
from ratings.test_data_func import create_test_user

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def test_add_rating(client, session):
    # Створіть тестового користувача та отримайте його токен
    user_data = {
        "id": 1,
        "email": "user@example.com",
        "username": "user",
        "role": "user",
    }
    create_test_user(session, user_id=user_data["id"], email=user_data["email"], username=user_data["username"], role=user_data["role"])
    token = auth_service.create_access_token(data={"sub": str(user_data["id"])})
    headers = {"Authorization": f"Bearer {token}"}

    # Створіть тестовий запис зображення
    image = Image(image_url="example.jpg", content="Some description", user_id=user_data["id"])
    session.add(image)
    session.commit()

    # Викличте API для додавання рейтингу
    response = client.post(
        "/api/rating/add",
        json={"rating": 5},
        params={"image_id": image.id},
        headers=headers,
    )

    # Перевірте, чи статус коду відповідає очікуваному результату
    assert response.status_code == 201
