from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_PATH = _PROJECT_ROOT / '.env'
_ENV_FILE = _ENV_PATH if _ENV_PATH.exists() else (_PROJECT_ROOT / '.env.example')


class ENV_CONFIG(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_ignore_empty=True,
        extra='ignore',
    )

    DEBUG: bool = True  # Django 用
    SECRET_KEY: SecretStr  # Django 用

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int

    BACKEND_CORS_ORIGINS: list[str] = []

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, list):
            return v
        return []

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Django ORM 使用"""
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return (
            f'postgresql://{self.POSTGRES_USER}:{password}'
            f'@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )


env_config = ENV_CONFIG()
