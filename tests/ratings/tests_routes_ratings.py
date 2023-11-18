import unittest
from unittest.mock import patch, MagicMock, AsyncMock, MagicMock
from fastapi import UploadFile
from src.routes.ratings import (
    get_rating,
    get_all_ratings,
    remove_rating,
    add_rating
)
from src.schemas.rating import RatingRequest
    

class MockImage:
    def __init__(self, id=1, user_id=1, title="Test Image", description="A test image"):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description

class MockRating:
    def __init__(self, id=1, user_id=1, image_id=1, rating=5):
        self.id = id
        self.user_id = user_id
        self.image_id = image_id
        self.rating = rating

class MockUser:
    def __init__(self, id=1, username="testuser", email="test@example.com"):
        self.id = id
        self.username = username
        self.email = email
   
    
def test_get_all_ratings(client, mocker):
    mocker.patch('src.repository.images.get_image', return_value=MockImage())
    mocker.patch('src.repository.ratings.get_ratings', return_value=[MockRating()])

    response = client.get("/rating/all?image_id=1")
    assert response.status_code == 200


def test_get_rating(client, mocker):
    mocker.patch('src.repository.ratings.get_rating', return_value=MockRating())

    response = client.get("/rating/1")
    assert response.status_code == 200


def test_remove_rating(client, mocker):
    mocker.patch('src.repository.ratings.remove_rating', return_value=MockRating())

    response = client.delete("/rating/1")
    assert response.status_code == 204

def test_add_rating(client, mocker):
    mocker.patch('src.repository.images.get_image', return_value=MockImage())
    mocker.patch('src.repository.ratings.get_ratings', return_value=[])
    mocker.patch('src.repository.ratings.add_rating', return_value=MockRating())

    response = client.post("/rating/add", json={"rating": 5, "image_id": 1})
    assert response.status_code == 201

if __name__ == "__main__":
    unittest.main()