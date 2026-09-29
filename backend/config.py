import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "CocoCare AI"
    APP_VERSION: str = "1.0.0"
    TAGLINE: str = "Protect Every Coconut Tree with AI"
    
    # Roboflow Configuration
    ROBOFLOW_API_KEY: str = ""
    ROBOFLOW_MODEL: str = "coconut-tree-disease"
    ROBOFLOW_VERSION: int = 1

    # Groq AI Configuration (for multilingual chatbot)
    GROQ_API_KEY: str = ""
    
    # Server Settings
    BACKEND_URL: str = "http://127.0.0.1:8000"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Database Settings
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/cococare.db"
    
    # Uploads Directory
    UPLOADS_DIR: str = str(BASE_DIR / "uploads")
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure required data and uploads directories exist
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
