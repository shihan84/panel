import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Flussonic Management Dashboard"
    PROJECT_VERSION: str = "1.0.0"

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
