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

    # Celery 설정
    celery_broker_url: str = (
        f"pyamqp://guest:guest@{os.getenv('RABBITMQ_HOST', 'rabbitmq')}:5672//"
    )
    celery_result_backend: str = (
        f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', 6379)}/0"
    )

    # Celery 추가 설정
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = True
    CELERY_FORCE_ROOT: str = os.getenv("CELERY_FORCE_ROOT", "False")
    CELERY_BROKER_CONNECTION_RETRY: bool = True
    CELERY_BROKER_CONNECTION_MAX_RETRIES: int = None
    CELERY_BROKER_CONNECTION_RETRY_INTERVAL: int = 5

    class Config:
        env_file = ".env"
        extra = "allow"


# Redis 설정
class RedisSettings:
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_minutes: float = float(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )
    refresh_token_expire_minutes: float = float(
        os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 1440)
    )


# Google API 클래스
class GoogleConfig:
    API_KEY: str = os.getenv("API_KEY")
    CLIENT_ID: str = os.getenv("CLIENT_ID")
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")
    REDIRECT_URI: str = "http://localhost:8000/googleauth/callback"
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    YOUTUBE_API_URL: str = "https://www.googleapis.com/youtube/v3/"

    def print_config(self):
        print(f"Google Client ID: {self.CLIENT_ID}")


settings = Settings()
google_config = GoogleConfig()
