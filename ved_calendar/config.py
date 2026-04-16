import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List


load_dotenv()


class Settings(BaseSettings):
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ADMIN_IDS: str = ""
    
    # Web Application Configuration
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = 8000
    WEBAPP_URL: str = "https://localhost:8000"
    
    # Admin Panel Configuration
    ADMIN_HOST: str = "0.0.0.0"
    ADMIN_PORT: int = 8001
    ADMIN_SECRET_KEY: str = "change_this_secret_key"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./ved_calendar.db"
    
    # Security
    JWT_SECRET_KEY: str = "change_this_jwt_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Settings
    DEBUG: bool = True
    TIMEZONE: str = "Europe/Moscow"
    EVENTS_PER_PAGE: int = 20
    CACHE_EXPIRE_HOURS: int = 1
    
    # Email Notifications (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    
    @property
    def admin_ids(self) -> List[int]:
        """Получить список ID администраторов из строки"""
        if not self.TELEGRAM_ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.TELEGRAM_ADMIN_IDS.split(",")]
    
    @property
    def database_async_url(self) -> str:
        """Получить асинхронный URL для базы данных"""
        return self.DATABASE_URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
