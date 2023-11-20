import cloudinary
import cloudinary.uploader

from fastapi import UploadFile
from src.conf.config import settings
from src.models.user import User
from urllib.parse import urlparse, parse_qs

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


def extract_id_from_url(url):
    """
    Extracts the  ID from URL.

    Example:
        >>> extract_id_from_url("http://youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'

    :param url: URL
    :return: ID as a string
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("v", [None])[0]


def get_cloudinary_public_id(user: User):
    """
    The get_cloudinary_public_id function takes a user object and returns the public id of that user's profile picture.
    The public id is used to identify the image in Cloudinary, which is where we store our images.

    :param user: User: Specify the type of parameter that is being passed in
    :return: A string in the format of snapshare-api/usernameid
    :doc-author: Trelent
    """
    return f"SnapShare-API/{user.username}{user.id}"


def post_cloudinary_image(file: UploadFile, user: User):
    """
    The post_cloudinary_image function takes a file and user as arguments.
    It then calls the get_cloudinary_public_id function to generate a public id for the image.
    The post_cloudinary_image function then uploads the image to Cloudinary using that public id, overwriting any existing images with that same public id.
    Finally, it returns an url for accessing this uploaded image.

    :param file: UploadFile: Get the file from the request
    :param user: User: Get the user's id
    :return: A url to the image
    :doc-author: Trelent
    """
    public_id = get_cloudinary_public_id(user)
    r = cloudinary.uploader.upload(file.file, public_id=public_id, owerwrite=True)
    return cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )


def get_cloudinary_image_transformation(
    user: User, transformation_type, width, height, effect, overlay_image_url
):
    """
    The get_cloudinary_image_transformation function takes in a user, transformation_type, width, height, effect and overlay_image_url.
    It then returns the cloudinary image url with the specified transformation applied to it.

    :param user: User: Get the user object
    :param transformation_type: Determine which transformation function to use
    :param width: Specify the width of the image
    :param height: Set the height of the image
    :param effect: Add an effect to the image
    :param overlay_image_url: Add an image to the transformation
    :return: A url
    :doc-author: Trelent
    """
    # Define base transformation
    transformation = {}

    # Apply specific transformation based on type
    if transformation_type == "resize":
        transformation.update({"width": width, "height": height, "crop": "limit"})
    elif transformation_type == "crop":
        transformation.update({"width": width, "height": height, "crop": "crop"})
    elif transformation_type == "effect":
        transformation.update({"effect": effect})
    elif transformation_type == "overlay":
        overlay_public_id = extract_id_from_url(overlay_image_url)
        transformation.update({"overlay": overlay_public_id})
    elif transformation_type == "face_detect":
        transformation.update(
            {"width": width, "height": height, "crop": "thumb", "gravity": "face"}
        )
    else:
        raise KeyError
    return cloudinary.CloudinaryImage(get_cloudinary_public_id(user)).build_url(
        transformation=transformation
    )
