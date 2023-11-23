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

if __name__ == '__main__':
    unittest.main()