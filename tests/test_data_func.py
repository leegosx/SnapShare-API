import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import random
import string
from src.models.photo import Photo, Tag
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

test_photo = {
    "image_url": "https://example.com/waifu.jpg",
    "content": "Your waifu photo",
}


# Helper functions for generating random data
def random_string(length=10):
    """
    The random_string function generates a random string of length 10.
        If you want to change the length, pass in an integer as an argument.
        
    
    :param length: Determine the length of the string that is returned
    :return: A string of random lowercase letters of length 10
    :doc-author: Trelent
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_test_user_and_test_photo(db):
    """
    The create_test_user_and_test_photo function creates a test user and a test photo.
    The function returns the created user.
    
    :param db: Pass the database into the function
    :return: The user object
    :doc-author: Trelent
    """
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
    """
    The create_random_tags function creates a list of random tags and adds them to the database.
        
    
    :param db: Pass in the database session
    :param num_tags: Specify the number of tags that will be created
    :return: A list of tag objects
    :doc-author: Trelent
    """
    tags = []
    for _ in range(num_tags):
        tag = Tag(name=random_string(7))
        db.add(tag)
        tags.append(tag)
    db.commit()
    return tags


def create_random_photos_for_user(db, user, tags, min_photos=3, max_photos=3):
    """
    The create_random_photos_for_user function creates a random number of photos for the given user.
    The number of photos created is between min_photos and max_photos, inclusive.
    Each photo will have one or two tags randomly selected from the list of tags provided.
    
    :param db: Access the database
    :param user: Assign the user_id to the photo
    :param tags: Randomly assign tags to the photos
    :param min_photos: Set the minimum number of photos a user can have
    :param max_photos: Specify the maximum number of photos a user can have
    :return: The user
    :doc-author: Trelent
    """
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