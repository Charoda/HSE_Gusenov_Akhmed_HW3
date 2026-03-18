from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/url_shortener")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    LINK_EXPIRATION_DAYS: int = Field(default=30)
    CLEANUP_UNUSED_DAYS: int = Field(default=90)

    class Config:
        env_file = ".env"


settings = Settings()