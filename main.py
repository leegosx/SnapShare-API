from sqlalchemy.orm import Session
from sqlalchemy import text

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status

from src.database.db import get_db
from src.routes import images, auth, users, tags, comments
from src.routes import ratings

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(images.router, prefix="/api")
app.include_router(comments.router, prefix='/api')
app.include_router(tags.router, prefix='/api')
app.include_router(ratings.router, prefix='/api')
app.include_router(users.router, prefix='/api')


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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastApi! Database connected correctly"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, host="127.0.0.1", port=8000)
