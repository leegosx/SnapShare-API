from typing import Optional, Union

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user import UserBase


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


async def count_users(db: Session) -> list:
    users = db.query(User).all()
    return users


async def create_user(body: UserBase, db: Session) -> User:
    users_check = await count_users(db)
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(f"Create_user: {e}")

    if len(users_check) == 0:
        user_data = body.dict()
        user_data["role"] = "admin"
        new_user = User(**user_data, avatar=avatar)
    else:
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


async def change_password(user: User, new_password: str, db: Session):
    user.password = new_password
    db.commit()
    return user
