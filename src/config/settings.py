"""Application settings loaded from environment variables."""

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed settings for database and JWT configuration."""
    DATABASE_URL: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"

    @model_validator(mode="after")
    def validate_database_settings(self):
        if self.DATABASE_URL:
            return self

        missing_fields = [
            field_name
            for field_name in (
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_DB",
            )
            if getattr(self, field_name) is None
        ]

        if missing_fields:
            raise ValueError(
                "DATABASE_URL is not set and missing POSTGRES fields: "
                + ", ".join(missing_fields)
            )

        return self


settings = Settings()