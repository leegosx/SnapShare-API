import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import random
import string
from src.models.photo import Photo, Tag
from src.models.user import User

test_user = {
    "username": "testuser",
    "email": "tester123@example.com",
    "password": "ptn_pnh123",
    "avatar": "default.jpg",
    "confirmed": True,
}

test_photo = {
    "image_url": "https://example.com/waifu.jpg",
    "content": "Your waifu photo",
}


# Helper functions for generating random data
def random_string(length=10):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_test_user_and_test_photo(db):
    user = User(
        username=test_user["username"],
        email=test_user["email"],
        password=test_user["password"],
        avatar=test_user["avatar"],
        confirmed=test_user["confirmed"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    photo = Photo(
        image_url=test_photo["image_url"],
        content=test_photo["content"],
        user_id=user.id,
    )
    return user


def create_random_tags(db, num_tags=5):
    tags = []
    for _ in range(num_tags):
        tag = Tag(name=random_string(7))
        db.add(tag)
        tags.append(tag)
    db.commit()
    return tags


def create_random_photos_for_user(db, user, tags, min_photos=3, max_photos=5):
    for _ in range(random.randint(min_photos, max_photos)):
        photo = Photo(
            image_url="https://example.com/" + random_string(5) + ".jpg",
            content="Random content" + random_string(4),
            user_id=user.id,
        )
        # Assign one or two random tags
        for _ in range(random.randint(1, 2)):
            photo.tags.append(random.choice(tags))
        db.add(photo)
    db.commit()
