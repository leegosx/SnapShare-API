from pydantic_settings import BaseSettings
from src.schemas.user import EmailStr
from dotenv import load_dotenv


class Settings(BaseSettings):
    sqlalchemy_database_url: str = (
        "postgresql+psycopg2://user:password@localhost:5432/postgres"
    )
    postgres_user: str = "POSTGRES_USER"
    postgres_password: str = "POSTGRES_PASSWORD"
    postgres_host: str = "POSTGRES_HOST"
    postgres_db: str = "POSTGRES_DB"
    secret_key: str = "SECRET_KEY"
    algorithm: str = "ALGORITHM"
    mail_username: str = "MAIL_USERNAME"
    mail_password: str = "MAIL_PASSWORD"
    mail_from: EmailStr = "JOHN.DOE@EXAMPLE.COM"
    mail_port: int = 0
    mail_server: str = "MAIL_SERVER"
    redis_host: str = "REDIS_HOST"
    redis_port: int = 0
    cloudinary_name: str = "CLOUDINARY_NAME"
    cloudinary_api_key: int = 0
    cloudinary_api_secret: str = "CLOUDINARY_API_SECRET"


# Load .env file before initializing Settings
load_dotenv(".env", encoding="utf-8")


settings = Settings()
