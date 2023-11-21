import unittest
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.repository.tags import get_tags, get_tag, create_tag, update_tag, remove_tag
from src.models.image import Tag
from src.schemas.tag import TagRequest

class TestRepositoryTags(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        engine = create_engine('sqlite:///:memory:')
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()
        Tag.metadata.create_all(bind=engine)

    async def test_get_tags(self):
        # Створіть дані для тестування
        tag1 = Tag(name="tag1")
        tag2 = Tag(name="tag2")
        self.db.add_all([tag1, tag2])
        self.db.commit()

        # Викликайте функцію, яку ви тестуєте
        result = await get_tags(0, 1, self.db)

        # Перевірте результат тесту
        self.assertEqual([tag.name for tag in result], ["tag1"])

    async def test_get_tag(self):
        # Створіть дані для тестування
        tag = Tag(name="tag1")
        self.db.add(tag)
        self.db.commit()

        # Викликайте функцію, яку ви тестуєте
        result = await get_tag(tag.id, self.db)

        # Перевірте результат тесту
        self.assertEqual(result.name, "tag1")

    async def test_create_tag(self):
        # Викликайте функцію, яку ви тестуєте
        body = TagRequest(name="tag1")
        result = await create_tag(body, self.db)

        # Перевірте результат тесту
        self.assertEqual(result.name, "tag1")

    async def test_update_tag(self):
        # Створіть дані для тестування
        tag = Tag(name="tag1")
        self.db.add(tag)
        self.db.commit()

        # Викликайте функцію, яку ви тестуєте
        body = TagRequest(name="tag2")
        result = await update_tag(tag.id, body, self.db)

        # Перевірте результат тесту
        self.assertEqual(result.name, "tag2")

    async def test_remove_tag(self):
        # Створіть дані для тестування
        tag = Tag(name="tag1")
        self.db.add(tag)
        self.db.commit()

        # Викликайте функцію, яку ви тестуєте
        result = await remove_tag(tag.id, self.db)

        # Перевірте результат тесту
        self.assertEqual(result.name, "tag1")

if __name__ == '__main__':
    unittest.main()
