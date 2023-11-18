from contextlib import AbstractContextManager
import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import datetime
from unittest.mock import MagicMock, AsyncMock

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.repository import images as repository_images
from src.schemas.tag import TagResponse
from src.models.image import Image, Tag
from src.routes.images import add_tag


class TestTag(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.current_user = MagicMock()
        self.image_id = 123
        self.tag_name = "Nature"

    async def test_succes_added_tag(self):
        mock_image = Image(
            id=self.image_id,
            image_url="https://example.com/sunset_beach.jpg",
            tags=[],
            content="Test content",
        )
        repository_images.get_image_user = AsyncMock(return_value=mock_image)

        self.session.query().filter_by().first = MagicMock(return_value=None)

        repository_images.update_image = AsyncMock()

        tag_response = TagResponse(id=1, tag=self.tag_name, image_id=self.image_id)

        updated_image = await add_tag(
            body=tag_response, db=self.session, current_user=self.current_user
        )

        self.assertIn(self.tag_name, [tag.name for tag in updated_image.tags])
        self.assertEqual(len(updated_image.tags), 1)
        repository_images.update_image.assert_called_once()

    async def test_add_tag_image_not_found(self):
        repository_images.get_image_user = AsyncMock(return_value=None)
        tag_response = TagResponse(id=1, tag=self.tag_name, image_id=self.image_id)
        with self.assertRaises(HTTPException):
            await add_tag(
                body=tag_response, db=self.session, current_user=self.current_user
            )

    async def test_add_tag_image_max_tags(self):
        mock_image = Image(
            id=self.image_id,
            image_url="https://example.com/sunset_beach.jpg",
            tags=[
                Tag(name="Tag1"),
                Tag(name="Tag2"),
                Tag(name="Tag3"),
                Tag(name="Tag4"),
                Tag(name="Tag5"),
            ],
            content="Test content",
        )
        repository_images.get_image_user = AsyncMock(return_value=mock_image)
        tag_response = TagResponse(id=1, tag=self.tag_name, image_id=self.image_id)
        with self.assertRaises(HTTPException):
            await add_tag(
                body=tag_response, db=self.session, current_user=self.current_user
            )

    async def test_add_tag_existing_tag(self):
        existing_tag = Tag(name=self.tag_name)
        mock_image = Image(
            id=self.image_id,
            image_url="https://example.com/sunset_beach.jpg",
            tags=[],
            content="Test content",
        )
        repository_images.get_image_user = AsyncMock(return_value=mock_image)
        self.session.query().filter_by().first = MagicMock(return_value=existing_tag)
        tag_response = TagResponse(id=1, tag=self.tag_name, image_id=self.image_id)
        updated_image = await add_tag(
            body=tag_response, db=self.session, current_user=self.current_user
        )
        self.assertIn(existing_tag, updated_image.tags)


if __name__ == "__main__":
    unittest.main()
