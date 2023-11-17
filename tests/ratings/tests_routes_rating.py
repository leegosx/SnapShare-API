import unittest
from unittest.mock import patch, MagicMock, AsyncMock, MagicMock
from fastapi import UploadFile
from src.routes.ratings import (
    get_rating,
    get_all_ratings,
    remove_rating,
    add_rating
)
from src.schemas.rating import RatingRequest
    