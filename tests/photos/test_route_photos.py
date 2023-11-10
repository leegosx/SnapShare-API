import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.photo import Photo
from src.models.user import User
from src.schemas.photo import PhotoCreate, PhotoUpdate

# Your fixtures from conftest.py go here (async_session, client, etc.)


@pytest.mark.asyncio
async def test_create_photo(
    client: AsyncClient, async_session: AsyncSession, test_user
):
    # Assuming test_user is a fixture that provides a user dict
    photo_data = {
        "image_url": "http://example.com/test_photo.jpg",
        "content": "Test Description",
        "user_id": test_user["id"],  # Assuming this ID exists in your test database
        "tags": [],
    }

    response = await client.post("/photos/create_new", json=photo_data)
    assert response.status_code == 200
    data = response.json()
    assert data["image_url"] == photo_data["image_url"]
    assert data["content"] == photo_data["content"]
    # Add more assertions as necessary


@pytest.mark.asyncio
async def test_update_photo(
    client: AsyncClient, async_session: AsyncSession, test_user
):
    # First, you need to have a photo created to update it
    photo = Photo(
        image_url="http://example.com/photo.jpg",
        content="A description",
        user_id=test_user["id"],
    )
    async_session.add(photo)
    await async_session.commit()

    update_data = {"content": "Updated Description"}
    response = await client.put(f"/photos/{photo.id}", json=update_data)
    assert response.status_code == 200
    updated_photo_data = response.json()
    assert updated_photo_data["content"] == update_data["content"]
    # Add more assertions as necessary


@pytest.mark.asyncio
async def test_delete_photo(
    client: AsyncClient, async_session: AsyncSession, test_user
):
    # First, you need to have a photo created to delete it
    photo = Photo(
        image_url="http://example.com/photo.jpg",
        content="A description",
        user_id=test_user["id"],
    )
    async_session.add(photo)
    await async_session.commit()

    response = await client.delete(f"/photos/{photo.id}")
    assert response.status_code == 200
    # Verify the photo is deleted, e.g., by trying to fetch it from the db


@pytest.mark.asyncio
async def test_get_photo(client: AsyncClient, async_session: AsyncSession, test_user):
    # First, you need to have a photo created to retrieve it
    photo = Photo(
        image_url="http://example.com/photo.jpg",
        content="A description",
        user_id=test_user["id"],
    )
    async_session.add(photo)
    await async_session.commit()

    response = await client.get(f"/photos/{photo.id}")
    assert response.status_code == 200
    photo_data = response.json()
    assert photo_data["image_url"] == photo.image_url
    # Add more assertions as necessary


@pytest.mark.asyncio
async def test_get_photos(client: AsyncClient, async_session: AsyncSession, test_user):
    # First, you need to have some photos created to retrieve them
    for _ in range(3):
        photo = Photo(
            image_url="http://example.com/photo.jpg",
            content="A description",
            user_id=test_user["id"],
        )
        async_session.add(photo)
    await async_session.commit()

    response = await client.get("/photos/")
    assert response.status_code == 200
    photos_data = response.json()
    assert len(photos_data) == 3
    # Add more assertions as necessary
