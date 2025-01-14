from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

folder_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=folder_path+'/.env')

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

class GoogleConfig:
    API_KEY = os.getenv("API_KEY")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI ='http://localhost:8000/auth/callback'
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/"


    print(f"Client ID: {CLIENT_ID}")