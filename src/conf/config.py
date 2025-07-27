from decouple import config as c
from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    Uses python-decouple for environment variable loading and Pydantic for validation.
    All sensitive credentials should be stored in the .env file.
    """
    DB_USER: str = c("DB_USER")
    DB_PASSWORD: str = c("DB_PASSWORD")
    DB_HOST: str = c("DB_HOST")
    DB_PORT: int = c("DB_PORT")
    DB_NAME: str = c("DB_NAME")

    SECRET_KEY: str = c("SECRET_KEY")
    ALGORITHM: str = c("ALGORITHM")
    MAIL_USERNAME: EmailStr = c("MAIL_USERNAME")
    MAIL_PASSWORD: str = c("MAIL_PASSWORD")
    MAIL_FROM: str = c("MAIL_FROM")
    MAIL_PORT: int = c("MAIL_PORT")
    MAIL_SERVER: str = c("MAIL_SERVER")
    REDIS_DOMAIN: str = c("REDIS_DOMAIN")
    REDIS_PORT: int = c("REDIS_PORT")
    REDIS_PASSWORD: str | None = c("REDIS_PASSWORD")

    @property
    def DB_URL(self) -> str:
        """
        Constructs and returns the PostgreSQL database connection URL.

        Returns:
            str: PostgreSQL async connection URL in format:
                 postgresql+asyncpg://user:password@host:port/dbname
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        """
        Validates that the JWT algorithm is one of the supported HMAC algorithms.

        Args:
            v: Algorithm string to validate

        Returns:
            str: Validated algorithm

        Raises:
            ValueError: If algorithm is not supported
        """
        if v not in ["HS256", "HS384", "HS512"]:
            raise ValueError("ALGORITHM must be 'HS256', 'HS384', or 'HS512'")
        return v

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")  # noqa


config = Settings()
