import os
from os.path import abspath, dirname, join, normpath

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.share.logger import setup_logger

logger = setup_logger(__name__)


class AppSettings(BaseSettings):
    """アプリケーション設定"""

    APP_NAME: str = Field(default="Gieieus")
    ENVIRONMENT: str = Field(default="development", alias="ENV")
    GOOGLE_CLOUD_PROJECT: str = Field(alias="GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = Field(default="us-central1")
    GOOGLE_GENAI_USE_VERTEXAI: str = Field(default="True")
    PORT: int = Field(default=8000)
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:3001")
    LOG_LEVEL: str = Field(default="INFO")
    ROOT_DIR: str | None = None

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    @field_validator("ROOT_DIR", mode="before")
    @classmethod
    def set_root_dir(cls, v):
        if v is not None:
            return v
        return normpath(join(dirname(abspath(__file__)), "..", ".."))

    @model_validator(mode="after")
    def validate_settings(self):
        required_fields = ["GOOGLE_CLOUD_PROJECT"]
        missing = [f for f in required_fields if not getattr(self, f)]
        if missing:
            raise ValueError(
                f"必須フィールドが設定されていません: {', '.join(missing)}",
            )
        return self


def get_settings(env_file: str | None = None) -> AppSettings:
    """環境に応じて設定をロード"""
    env = os.getenv("ENVIRONMENT", "dev")
    if env_file is None:
        env_file = f".env.{env}" if env != "dev" else ".env.dev"

    logger.debug(f"選択されている環境変数ファイル: {env_file}")
    logger.debug(f"環境変数: {env}")

    return AppSettings(_env_file=env_file)  # type: ignore
