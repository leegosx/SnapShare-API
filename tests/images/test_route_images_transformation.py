from fastapi.testclient import TestClient
from main import app  # Import your FastAPI application
from unittest.mock import patch
import pytest

client = TestClient(app)


def mock_get_cloudinary_image_transformation(
    user, transformation_type, width, height, effect, overlay_image_url
):
    # Mocked transformation URL based on the inputs
    return "http://mocked.transformed.url"


def mock_create_qr_code_from_url(url):
    # Mocked QR code for the transformed URL
    return "mocked_qr_code_base64"


def mock_add_transform_url_image(image_url, transform_url, current_user, db):
    # Mock database interaction
    pass


@pytest.fixture(autouse=True)
def mock_external_dependencies():
    with patch(
        "src.utils.image_utils.get_cloudinary_image_transformation",
        side_effect=mock_get_cloudinary_image_transformation,
    ), patch(
        "src.utils.qr_code.create_qr_code_from_url",
        side_effect=mock_create_qr_code_from_url,
    ), patch(
        "src.repository.images.add_transform_url_image",
        side_effect=mock_add_transform_url_image,
    ):
        yield


# def test_transform_image_success():
#     response = client.post(
#         "/transform_image/",
#         json={
#             "image_url": "http://example.com/image.jpg",
#             "transformation_type": "resize",
#             "width": 100,
#             "height": 100,
#         },
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["image_url"] == "http://example.com/image.jpg"
#     assert data["image_transformed_url"] == "http://mocked.transformed.url"
#     assert data["qr_code"] == "mocked_qr_code_base64"


# def test_transform_image_invalid_input():
#     response = client.post(
#         "/transform_image/",
#         json={
#             "image_url": "not_a_url",
#             "transformation_type": "resize",
#             "width": 100,
#             "height": 100,
#         },
#     )
#     assert response.status_code == 400


# Additional tests can be added for other scenarios
