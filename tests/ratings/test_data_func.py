import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import random
import string
from src.models.image import Image, Tag
from src.models.user import User
from src.services.auth_service import Auth
from src.models.rating import Rating

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
    "content": "Your waifu image",
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


def create_test_user(db):
    """
    The create_test_user_and_test_photo function creates a test user and a test image.
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


def create_random_photos_for_user(db, user_id, min_images=3, max_images=3):
    """
    The create_random_photos_for_user function creates a random number of photos for the given user.
    The number of photos created is between min_photos and max_photos, inclusive.
    Each image will have one or two tags randomly selected from the list of tags provided.
    
    :param db: Access the database
    :param user: Assign the user_id to the image
    :param tags: Randomly assign tags to the photos
    :param min_photos: Set the minimum number of photos a user can have
    :param max_photos: Specify the maximum number of photos a user can have
    :return: The user
    :doc-author: Trelent
    """
    images = []
    for _ in range(random.randint(min_images, max_images)):
        image = Image(
            image_url="https://example.com/" + random_string(5) + ".jpg",
            content="Random content" + random_string(4),
            user_id=user_id,
        )
        db.add(image)
        images.append(image)
    db.commit()
    return images
    
def create_test_rating(db, user_id, image_id, rating_score):
    """
    The create_test_rating function creates a test rating for the given user and image.

    :param db: Access the database
    :param user: Assign the user_id to the rating
    :param image: Assign the image_id to the rating
    :return: The rating
    :doc-author: Trelent
    """
    new_rating = Rating(user_id=user_id, image_id=image_id, rating_score=rating_score)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating.id