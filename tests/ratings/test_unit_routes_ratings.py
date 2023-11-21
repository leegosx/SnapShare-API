# import unittest
# from fastapi.testclient import TestClient
# from sqlalchemy.orm import Session
# from src.models.user import User
# from src.database.db import get_db
# from main import app
# from src.services.auth_service import auth_service
# from src.repository import ratings as repository_ratings
# from src.repository import users as repository_users  # Додайте імпорт репозиторію користувачів

# class TestRating(unittest.TestCase):
#     def setUp(self):
#         self.client = TestClient(app)

#     def test_add_rating(self):
#         # Test case: Successfully add a rating
#         # Use the testuser fixture defined in conftest.py
#         user_data = {
#             "id": 1,
#             "username": "testuser",
#             "email": "tester123@example.com",
#             "avatar": "default.jpg",
#             "role": "admin",
#             "uploaded_photos": 3,
#             "password": "ptn_pnh123",
#             "confirmed": True,
#         }

#         # Замість створення тестового користувача в коді тесту, використовуйте збережений в conftest.py testuser
#         # user = repository_users.create_user(db, **user_data)  # Позначено як коментар, оскільки ми вже маємо testuser

#         token = auth_service.create_access_token(data={"sub": str(user_data["id"])})
#         headers = {"Authorization": f"Bearer {token}"}

#         # Send the request with the rating in the request body
#         response = self.client.post(
#             "/api/rating/add",
#             json={"rating": 5, "image_id": 1},
#             headers=headers,
#         )

#         # Check if the request was successful (status code 201)
#         self.assertEqual(response.status_code, 201)

#         # Optionally, check the response content
#         rating_data = response.json()
#         self.assertEqual(rating_data["user_id"], user_data["id"])
#         self.assertEqual(rating_data["image_id"], 1)
#         self.assertEqual(rating_data["rating_score"], 5)

#         # You can also retrieve the created rating from the database and assert its values
#         with get_db() as db:  # Use get_db() to obtain a database session
#             created_rating = repository_ratings.get_rating(rating_data["id"], db)
#             self.assertIsNotNone(created_rating)
#             self.assertEqual(created_rating.user_id, user_data["id"])
#             self.assertEqual(created_rating.image_id, 1)
#             self.assertEqual(created_rating.rating_score, 5)

#         # TODO: Add more test cases for add_rating to cover different scenarios

#     def tearDown(self):
#         # Clean up any changes made during the tests
#         app.dependency_overrides.clear()

# if __name__ == '__main__':
#     unittest.main()
