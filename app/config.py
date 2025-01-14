from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import redis

folder_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=folder_path + "/.env")


class Settings(BaseSettings):
    app_name: str
    database_url: str
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
