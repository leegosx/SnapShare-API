from sqlalchemy.orm import Session
from src.database.db import get_db

def test_get_db():
    # Arrange
    fake_session = Session()

    # Act
    db = next(get_db())

    # Assert
    assert isinstance(db, Session)

    # Clean up
    db.close()