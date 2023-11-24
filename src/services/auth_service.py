import pickle
from typing import Optional

import redis as redis_db
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository.users import get_user_by_email
from src.repository import users as repository_users
from src.conf.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_token_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    The get_token_user function is a dependency that will be used by the get_current_user function.
    It takes in a token and returns the user associated with it.

    :param token: str: Pass the token from the http request to this function
    :param db: Session: Access the database
    :return: The token, which is a string
    """
    return token


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    # ALGORITHM = settings.algorithm
    ALGORITHM = 'HS256'
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis = redis_db.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Represent the instance of the class
        :param plain_password: Pass in the password that is entered by the user
        :param hashed_password: Check the password against the hashed version of it
        :return: A boolean value, true if the password is correct and false if it is not

        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Make the function a method of the user class
        :param password: str: Get the password from the user
        :return: A hash of the password

        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary containing the claims to be encoded in the JWT.
                expires_delta (Optional[float]): An optional parameter specifying how long, in seconds,
                    the access token should last before expiring. If not specified, it defaults to 15 minutes.

        :param self: Access the class attributes
        :param data: dict: Pass the data that will be encoded in the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A jwt access token

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the user's data
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A token that is encoded with the user's data and a scope of refresh_token

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    def create_email_token(self, data: dict):

        """
        The create_email_token function takes in a dictionary of data and returns an encoded JWT token.
        The function first creates a copy of the data dictionary, then adds three key-value pairs to it:
        iat (issued at), exp (expiration date), and scope. The iat value is set to datetime.utcnow(),
        the exp value is set to datetime.utcnow() + timedelta(days=7) which means that the token will expire in 7 days,
        and the scope value is set to &quot;email_token&quot;. Then we use jwt's encode method with our SECRET_KEY

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into a jwt
        :return: A token that is encoded with the user's email address,

        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"}
        )
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def decode_refresh_token(self, refresh_token: str):

        """
        The decode_refresh_token function is used to decode the refresh token.
            The function will first try to decode the refresh token using JWT. If it succeeds,
            then it will check if the scope of that token is 'refresh_token'. If so, then we know
            that this is a valid refresh token and we can return its email address (which was stored in sub).

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user

        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be used in the UserController class.
        It takes in a token and database session as parameters, and returns the user object associated with
        the email address stored within the JWT token. If no user exists for that email address, or if there is an error decoding
        the JWT token, then it raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Get the token from the authorization header
        :param db: Session: Pass the database session to the function
        :return: A user object

        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception

            # Check blacklist token
            black_list_token = await repository_users.find_black_list_token(token, db)
            if black_list_token:
                raise credentials_exception

        except JWTError as e:
            raise credentials_exception

        user = self.redis.get(f"user:{email}")
        if user is None:
            print("GET USER FROM POSTGRES")
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.redis.set(f"user:{email}", pickle.dumps(user))
            self.redis.expire(f"user:{email}", 900)
        else:
            print("GET USER FROM CACHE")
            user = pickle.loads(user)
        return user
    
    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
        If the scope of the payload is not &quot;email_token&quot;, then it raises an HTTPException. If there is a JWTError, then it also raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Pass in the token that we want to decode
        :return: The email that was encoded in the jwt token

        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
