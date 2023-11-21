from typing import List
import uuid
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.user import UserBase, UserResponse, TokenModel, ResetPasswordModel
from src.repository import users as repository_users
from src.services.auth_service import auth_service, get_token_user
from src.services.email_service import send_email, send_email_reset_password

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserBase,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The signup function creates a new user in the database.
        It takes an email, username and password as input parameters.
        The function returns a JSON object containing the newly created user's information.

    :param body: UserBase: Specify the data type of the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A dict with the user and a detail message
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
        The access token can be used to make authenticated requests for data from our API.

    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Get the database session from the dependency injection container
    :return: A dict with the access token and refresh token
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    user_status = await repository_users.check_ban_status(body.username, db)
    if user_status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Your account is banned"
        )

    # Generate JWT
    access_token = await auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=7200
    )
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    # Check if refresh token is blacklisted
    if await repository_users.find_black_list_token(access_token, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has been blacklisted",
        )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/logout")
async def logout(
    token: str = Depends(get_token_user),
    current_user: UserBase = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Save token of user to table blacklists
    """
    The logout function is used to logout a user.
        It takes in the token of the user and returns a message that says &quot;User logged out successfully&quot;.

    :param token: str: Get the token of the user
    :param current_user: UserBase: Get the user who is logged in
    :param db: Session: Pass the database session to the function
    :return: A dictionary with the status code, detail and token
    :doc-author: Trelent
    """
    await repository_users.save_black_list_token(token, current_user, db)

    return {
        "status_code": status.HTTP_200_OK,
        "detail": "User logged out successfully",
        "token": token,
    }


@router.get("/protected_endpoint")
async def some_protected_endpoint(
    token: str = Depends(get_token_user), db: Session = Depends(get_db)
):
    """
    The some_protected_endpoint function is a protected endpoint that requires the user to be authenticated.
    The token is passed in as an authorization header, and the function will return a message if it was successful.

    :param token: str: Get the token from the request header
    :param db: Session: Get a database session
    :return: A message if the token is not blacklisted
    :doc-author: Trelent
    """
    if await repository_users.find_black_list_token(token, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted"
        )

    return {"message": "This is a protected endpoint"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns a new access_token, refresh_token, and token type.


    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the request header
    :param db: Session: Access the database
    :return: A dictionary with the access token, refresh token and token type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do not exist,
        an HTTP 400 error is raised. If they do exist but their account has already been confirmed,
        then a message saying so will be returned. Otherwise (if they are found in our database
        and their account has not yet been confirmed), we call repository_users' confirmed_email function
         with that email as its

    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A dictionary with the message key and value
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get("/forgot_password")
async def forgot_password(
    email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    The forgot_password function is used to send a reset password token to the user's email.
        The function takes in an email and returns a message with the reset password token.
    
    
    :param email: str: Get the email of the user who wants to reset his password
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param db: Session: Get the database session
    :return: A dict
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found user."
        )
    reset_password_token = uuid.uuid1()
    background_tasks.add_task(
        send_email_reset_password,
        str(reset_password_token),
        user.email,
        user.username,
    )
    user.reset_password_token = reset_password_token
    db.commit()

    return {
        "message": f"Reset password token has been sent to your e-email.{reset_password_token}"
    }


@router.patch("/reset_password")
async def reset_password(body: ResetPasswordModel, db: Session = Depends(get_db)):
    """
    The reset_password function is used to reset a user's password.
        It takes in the ResetPasswordModel as its body, which contains the email of the user, their new password and confirmation of that new password.
        The function then checks if there is a user with that email address in our database. If not, it raises an HTTPException with status code 404 and detail &quot;Not found user.&quot;
        Next it checks if the reset_password_token matches what was sent by our frontend application (this token should be stored on local storage). If not, it raises an HTTPException with status code 404 and detail &quot;Password reset
    
    :param body: ResetPasswordModel: Get the email, reset_password_token and password from the request body
    :param db: Session: Pass the database connection to the function
    :return: A json response, which is a subclass of response
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found user."
        )

    if body.reset_password_token != user.reset_password_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password reset tokens doesn't match.",
        )

    if body.password != body.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="New password is not match."
        )

    body.password = auth_service.get_password_hash(body.password)
    user.password = body.password
    user.reset_password_token = None
    db.commit()

    return JSONResponse(
        content={"message": "Your password was successfully changed"}, status_code=200
    )
