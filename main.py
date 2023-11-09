from sqlalchemy.orm import Session
from sqlalchemy import text

from fastapi import FastAPI, Depends, HTTPException, status

from src.database.db import get_db
from src.routes.photos import photos

app = FastAPI()

app.include_router(photos.router, prefix="/api")

@app.get("/", name="Корінь проекту")
def read_root():
    """
    The read_root function is a view function that returns the root of the API.
    It's purpose is to provide a simple way for users to test if their connection
    to the API is working properly.

    :return: A dictionary
    """
    return {"message": "RestApi is working, all okay!"}


@app.get("/api/healthchecker")
def healthchecher(db: Session = Depends(get_db)):
    """
    The healthchecher function is used to check the health of the application.
    It returns a message if everything is ok, or an error otherwise.

    :param db: Session: Pass the database connection to the function
    :return: A dict with a message
    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcom to FastApi! Database connected correctly"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
