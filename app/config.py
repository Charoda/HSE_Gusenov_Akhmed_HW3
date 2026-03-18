from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = Field(default=None)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    LINK_EXPIRATION_DAYS: int = Field(default=30)
    CLEANUP_UNUSED_DAYS: int = Field(default=90)

    # Optional individual PostgreSQL settings (used by some hosting platforms)
    POSTGRES_USER: Optional[str] = Field(default=None)
    POSTGRES_PASSWORD: Optional[str] = Field(default=None)
    POSTGRES_DB: Optional[str] = Field(default=None)
    POSTGRES_HOST: Optional[str] = Field(default="localhost")
    POSTGRES_PORT: Optional[int] = Field(default=5432)

    class Config:
        env_file = ".env"

    @model_validator(mode='after')
    def build_database_url(self):
        if self.DATABASE_URL is None:
            user = self.POSTGRES_USER or 'postgres'
            password = self.POSTGRES_PASSWORD or 'postgres'
            host = self.POSTGRES_HOST or 'localhost'
            port = self.POSTGRES_PORT or 5432
            db = self.POSTGRES_DB or 'url_shortener'
            self.DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        return self


settings = Settings()