from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


folder_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=folder_path + "/.env")


class Settings(BaseSettings):
    app_name: str
    database_url: str
    redis_host: str = "redis"
    redis_port: int = 6379
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM", "HS256")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()


class RedisSettings:
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    access_token_expire_minutes = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    refresh_token_expire_minutes = float(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))


class GoogleConfig:
    API_KEY = os.getenv("API_KEY")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = "http://localhost:8000/oauth/callback"
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/"

    print(f"Client ID: {CLIENT_ID}")
