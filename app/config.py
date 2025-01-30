from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# .env 파일 경로 로드
folder_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(folder_path, ".env"))


class Settings(BaseSettings):
    # 기본 애플리케이션 설정
    app_name: str
    database_url: str
    redis_host: str = "redis"
    redis_port: int = 6379
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    openai_api_key: str

    # GCP 설정
    gcp_bucket_name: str = os.getenv("GCP_BUCKET_NAME")
    gcp_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Celery 설정
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = os.getenv("CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP",
                                                                "True") == "True"
    CELERY_FORCE_ROOT: bool = os.getenv("CELERY_FORCE_ROOT", "False") == "True"
    CELERY_BROKER_CONNECTION_RETRY: bool = os.getenv("CELERY_BROKER_CONNECTION_RETRY", "True") == "True"
    CELERY_BROKER_CONNECTION_MAX_RETRIES: int | None = (
        int(os.getenv("CELERY_BROKER_CONNECTION_MAX_RETRIES")) if os.getenv(
            "CELERY_BROKER_CONNECTION_MAX_RETRIES") else None
    )
    CELERY_BROKER_CONNECTION_RETRY_INTERVAL: int = int(os.getenv("CELERY_BROKER_CONNECTION_RETRY_INTERVAL", 5))

    class Config:
        env_file = ".env"
        extra = "allow"


# Redis 설정
class RedisSettings:
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    refresh_token_expire_minutes: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")
    )


# Google API 클래스
class GoogleConfig:
    API_KEY: str = os.getenv("API_KEY")
    CLIENT_ID: str = os.getenv("CLIENT_ID")
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")
    REDIRECT_URI: str = "http://api.algorify.net/googleauth/callback"
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    YOUTUBE_API_URL: str = "https://www.googleapis.com/youtube/v3/"

    def print_config(self):
        print(f"Google Client ID: {self.CLIENT_ID}")


settings = Settings()
google_config = GoogleConfig()
