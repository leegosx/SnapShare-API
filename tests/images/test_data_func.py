import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import random
import string
from src.models.image import Image, Tag
from src.models.user import User
from src.services.auth_service import Auth

auth_service = Auth()

test_user = {
    "username": "testuser",
    "email": "tester123@example.com",
    "password": auth_service.get_password_hash("ptn_pnh123"),
    "avatar": "default.jpg",
    "confirmed": True,
}

test_image = {
    "image_url": "https://example.com/waifu.jpg",
    "content": "Your waifu image",
}


# Helper functions for generating random data
def random_string(length=10):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_test_user_and_test_image(db):
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
    image = Image(
        image_url=test_image["image_url"],
        content=test_image["content"],
        user_id=user.id,
        image_transformed_url="https://example.com/transformed_waifu.jpg",
    )
    db.add(image)
    return user


def create_random_tags(db, num_tags=5):
    tags = []
    for _ in range(num_tags):
        tag = Tag(name=random_string(7))
        db.add(tag)
        tags.append(tag)
    db.commit()
    return tags


def create_random_images_for_user(db, user, tags, min_images=3, max_images=3):
    for _ in range(random.randint(min_images, max_images)):
        image = Image(
            image_url="https://example.com/" + random_string(5) + ".jpg",
            content="Random content" + random_string(4),
            user_id=user.id,
        )
        # Assign one or two random tags
        for _ in range(random.randint(1, 2)):
            image.tags.append(random.choice(tags))
        db.add(image)
    db.commit()
