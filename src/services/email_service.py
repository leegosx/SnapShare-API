from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth_service import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Rest API App",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three arguments:
            -email: the user's email address, which is used as a unique identifier for each account.
            -username: the username of the account that was just created. This is displayed in 
                confirmation message sent to them via email. 
            -host: this is used as part of URL that will be sent out in order for users to confirm their accounts.
    
    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username to the template
    :param host: str: Create the link to confirm the email
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_email_reset_password(token: str, email: EmailStr, username: str):
    """
    The send_email_reset_password function sends an email to the user with a link to reset their password.
        Args:
            token (str): The token that will be used in the URL for resetting the password.
            email (EmailStr): The user's email address, which is where they will receive the message.
            username (str): The username of the person who requested a new password.
    
    :param token: str: Pass the token to the template
    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the template
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        message = MessageSchema(
            subject="Reset password ",
            recipients=[email],
            template_body={"username": username, "token": token},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password_template.html")
    except ConnectionErrors as err:
        print(err)
