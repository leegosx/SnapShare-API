import cloudinary
import cloudinary.uploader

from fastapi import UploadFile
from src.conf.config import settings
from src.models.user import User

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


# Transformation mapping (can be defined outside the function)
TRANSFORMATION_MAPPING = {
    "resize": lambda width, height: {"width": width, "height": height, "crop": "limit"},
    "crop": lambda width, height: {"width": width, "height": height, "crop": "crop"},
    "effect": lambda effect: {"effect": effect},
    "overlay": lambda overlay_url: {"overlay": extract_id_from_url(overlay_url)},
    "face_detect": lambda width, height: {
        "width": width,
        "height": height,
        "crop": "thumb",
        "gravity": "face",
    },
}


def extract_id_from_url(url):
    return url.split("/")[-1].split(".")[0]


def get_cloudinary_public_id(user: User):
    return f"SnapShare-API/{user.username}{user.id}"


def post_cloudinary_image(file: UploadFile, user: User):
    public_id = get_cloudinary_public_id(user)
    r = cloudinary.uploader.upload(file.file, public_id=public_id, owerwrite=True)
    return cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )

def get_cloudinary_image_transformation(
    user: User, transformation_type, width, height, effect, overlay_image_url
):
    # Get the transformation
    transformation = TRANSFORMATION_MAPPING[transformation_type](
        width, height, effect, overlay_image_url
    )
    return cloudinary.CloudinaryImage(get_cloudinary_public_id(user)).build_url(
        transformation=transformation
    )
