import unittest
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

    def test_healthchecker_database_error(self):
        # Test when the database connection fails
        with self.assertRaises(Exception) as context:
            response = self.client.get("/api/healthchecker")

        # Optionally, you can check the exception message or other details
        self.assertEqual(context.exception.response.status_code, 500)
        self.assertEqual(context.exception.response.json(), {"detail": "Error connecting to the database"})

    def tearDown(self):
        # Clean up any changes made during the tests
        app.dependency_overrides.clear()

if __name__ == '__main__':
    # TODO: Uncomment the following lines to run the application
    # uvicorn.run(app="main:app", reload=True, host="127.0.0.1", port=8001)

    # Run the tests
    unittest.main()





# import unittest
# from fastapi.testclient import TestClient
# from src.database.db import get_db
# from main import app

# class TestMain(unittest.TestCase):
#     def setUp(self):
#         self.client = TestClient(app)

#     def test_read_root(self):
#         response = self.client.get("/")
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {"message": "RestApi is working, all okay!"})

#     def test_healthchecker(self):
#         # Test when the database connection is successful
#         response = self.client.get("/api/healthchecker")
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), {"message": "Welcome to FastApi! Database connected correctly"})

#         # TODO: Add more tests to cover additional scenarios
#         # Test when the database connection fails

#     def test_healthchecker_database_error(self):
#         # Define a context manager to temporarily override the get_db dependency
#         class OverrideGetDB:
#             def __enter__(self):
#                 app.dependency_overrides[get_db] = self.mock_get_db
#                 return self

#             def __exit__(self, exc_type, exc_value, traceback):
#                 app.dependency_overrides.pop(get_db, None)

#             def mock_get_db(self):
#                 raise Exception("Simulated database error")

#         # Use the context manager to override get_db only for this test
#         with self.assertRaises(Exception) as context:
#             with OverrideGetDB():
#                 response = self.client.get("/api/healthchecker")

#         # Optionally, you can check the exception message or other details
#         self.assertEqual(str(context.exception), "Simulated database error")

#     def tearDown(self):
#         # Clean up any changes made during the tests
#         app.dependency_overrides.clear()

# if __name__ == '__main__':
#     unittest.main()
