from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
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

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def build_database_url(cls, v, values):
        if v is not None:
            return v

        # Build DATABASE_URL from individual components if available
        user = values.get('POSTGRES_USER', 'postgres')
        password = values.get('POSTGRES_PASSWORD', 'postgres')
        host = values.get('POSTGRES_HOST', 'localhost')
        port = values.get('POSTGRES_PORT', 5432)
        db = values.get('POSTGRES_DB', 'url_shortener')

        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


settings = Settings()