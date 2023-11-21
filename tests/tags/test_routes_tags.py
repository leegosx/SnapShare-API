import unittest
from unittest.mock import patch, AsyncMock, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

from src.models.image import Image, Tag
from src.schemas.tag import TagRequest
from main import app
import unittest
from unittest.mock import MagicMock

from src.routes.tags import (
    read_tags,
    read_tag,
    create_tag,
    update_tag,
    remove_tag
)

class TestTagsRoutes(unittest.IsolatedAsyncioTestCase):
    @patch('src.repository.tags.get_tags')
    async def test_read_tags(self, mock_get_tags):
        mock_db = MagicMock()
        mock_tags = [MagicMock(), MagicMock()]
        mock_get_tags.return_value = mock_tags
        skip = 0
        limit = 10

        result = await read_tags(skip, limit, mock_db)

        self.assertEqual(result, mock_tags)
        mock_get_tags.assert_called_with(skip, limit, mock_db)

    @patch('src.repository.tags.get_tag')
    async def test_read_tag(self, mock_get_tag):
        mock_db = MagicMock()
        tag_id = 1
        mock_tag = MagicMock()
        mock_get_tag.return_value = mock_tag

        result = await read_tag(tag_id, mock_db)

        self.assertEqual(result, mock_tag)
        mock_get_tag.assert_called_with(tag_id, mock_db)

    
    @patch('src.repository.tags.create_tag')
    async def test_create_tag(self, mock_create_tag):
        mock_db = MagicMock()
        body = TagRequest(name="example")
        mock_tag = MagicMock()
        mock_create_tag.return_value = mock_tag

        result = await create_tag(body, mock_db)

        self.assertEqual(result, mock_tag)
        mock_create_tag.assert_called_with(body, mock_db)

    @patch('src.repository.tags.update_tag')
    async def test_update_tag(self, mock_update_tag):
        mock_db = MagicMock()
        tag_id = 1
        body = TagRequest(name="updated example")
        mock_updated_tag = MagicMock()
        mock_update_tag.return_value = mock_updated_tag

        result = await update_tag(body, tag_id, mock_db)

        self.assertEqual(result, mock_updated_tag)
        mock_update_tag.assert_called_with(tag_id, body, mock_db)
        
    @patch('src.repository.tags.remove_tag')
    async def test_remove_tag(self, mock_remove_tag):
        mock_db = MagicMock()
        tag_id = 1
        mock_tag = MagicMock()
        mock_remove_tag.return_value = mock_tag

        result = await remove_tag(tag_id, mock_db)

        self.assertEqual(result, mock_tag)
        mock_remove_tag.assert_called_with(tag_id, mock_db)
