from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List
import os

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DEFAULT_USER_EMAIL: str
    DEFAULT_USER_PASSWORD: str
    DEFAULT_USERNAME: str

    APP_NAME: str
    APP_VERSION: str

    DATABASE_URL: str

    DEFAULT_RISK_LEVEL: str
    DEFAULT_CONFIDENCE: float
    DEFAULT_LOT_SIZE: float

    API_V1_STR: str
    PROJECT_NAME: str

    BACKEND_CORS_ORIGINS: List[str]

    FINNHUB_API_KEY: str

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()