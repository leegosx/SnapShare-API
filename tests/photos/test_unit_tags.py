from contextlib import AbstractContextManager
import sys
import os
from typing import Any
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import datetime
from unittest.mock import MagicMock, AsyncMock

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.repository import photos as repository_photos
from src.schemas.tag import TagResponse
from src.models.photo import Photo, Tag
from src.routes.photos import add_tag

class TestTag(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.current_user = MagicMock()
        self.photo_id = 123
        self.tag_name = "Nature"
        
    async def test_succes_added_tag(self):
        mock_photo = Photo(id=self.photo_id, tags=[], content="Test content")
        repository_photos.get_photo_user = AsyncMock(return_value=mock_photo)

        self.session.query().filter_by().first = MagicMock(return_value=None)

        repository_photos.update_photo = AsyncMock()

        tag_response = TagResponse(id=1, tag=self.tag_name, photo_id=self.photo_id)

        updated_photo = await add_tag(body=tag_response, db=self.session, current_user=self.current_user)

        self.assertIn(self.tag_name, [tag.name for tag in updated_photo.tags])
        self.assertEqual(len(updated_photo.tags), 1)
        repository_photos.update_photo.assert_called_once()

    async def test_add_tag_photo_not_found(self):
        repository_photos.get_photo_user = AsyncMock(return_value=None)
        tag_response = TagResponse(id=1, tag=self.tag_name, photo_id=self.photo_id)
        with self.assertRaises(HTTPException):
            await add_tag(body=tag_response, db=self.session, current_user=self.current_user)

    async def test_add_tag_photo_max_tags(self):
        mock_photo = Photo(id=self.photo_id, tags=[Tag(name="Tag1"), Tag(name="Tag2"), Tag(name="Tag3"), Tag(name="Tag4"), Tag(name="Tag5")], content="Test content")
        repository_photos.get_photo_user = AsyncMock(return_value=mock_photo)
        tag_response = TagResponse(id=1, tag=self.tag_name, photo_id=self.photo_id)
        with self.assertRaises(HTTPException):
            await add_tag(body=tag_response, db=self.session, current_user=self.current_user)
            
    async def test_add_tag_existing_tag(self):
        existing_tag = Tag(name=self.tag_name)
        mock_photo = Photo(id=self.photo_id, tags=[], content="Test content")
        repository_photos.get_photo_user = AsyncMock(return_value=mock_photo)
        self.session.query().filter_by().first = MagicMock(return_value=existing_tag)
        tag_response = TagResponse(id=1, tag=self.tag_name, photo_id=self.photo_id)
        updated_photo = await add_tag(body=tag_response, db=self.session, current_user=self.current_user)
        self.assertIn(existing_tag, updated_photo.tags)
        
if __name__ == '__main__':
    unittest.main()
