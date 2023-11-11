from typing import Optional, Union

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user import UserBase


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserBase, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Create_user: {e}")
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: UserBase, token: Union[str, None], db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
