import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.database.db import get_db
from main import app

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_read_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "RestApi is working, all okay!"})

    def test_healthchecker(self):
        # Test when the database connection is successful
        response = self.client.get("/api/healthchecker")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Welcome to FastApi! Database connected correctly"})

    # @patch('src.database.db.get_db')
    # def test_healthchecker_database_error(self, mock_get_db):
    #     # Simulate database connection failure
    #     mock_get_db.side_effect = Exception("Database connection failed")

    #     # Test when the database connection fails
    #     response = self.client.get("/api/healthchecker")

    #     # Check that the response status code is 500 (Internal Server Error)
    #     self.assertEqual(response.status_code, 500)

    #     # Optionally, you can check the response JSON for details
    #     expected_response = {"detail": "Error connecting to the database"}
    #     self.assertEqual(response.json(), expected_response)

    # def test_healthchecker_database_error(self):
    #     # Test when the database connection fails
    #     response = self.client.get("/api/healthchecker")

    #     # Check that the response status code is 500 (Internal Server Error)
    #     self.assertEqual(response.status_code, 500)

    #     # Optionally, you can check the response JSON for details
    #     expected_response = {"detail": "Error connecting to the database"}
    #     self.assertEqual(response.json(), expected_response)

    # def test_healthchecker_database_error(self):
    #     # Перекриваємо функцію get_db, щоб вона завжди викликала помилку
    #     app.dependency_overrides[get_db] = MagicMock(side_effect=Exception("Error connecting to the database"))

    #     # Тестуємо, чи викликається Exception при спробі з'єднатися з базою даних
    #     with self.assertRaises(Exception):
    #         response = self.client.get("/api/healthchecker")

    #     # Повертаємо функцію get_db в її оригінальний стан
    #     app.dependency_overrides.pop(get_db, None)

    # def tearDown(self):
    #     # Clean up any changes made during the tests
    #     app.dependency_overrides[get_db] = get_db

if __name__ == '__main__':
    # Run the tests
    unittest.main()

