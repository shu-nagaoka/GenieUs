import os
from os.path import abspath, dirname, join, normpath

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.share.logger import setup_logger

logger = setup_logger(__name__)


class AppSettings(BaseSettings):
    """アプリケーション設定"""

    APP_NAME: str = Field(default="GenieUs")
    ENVIRONMENT: str = Field(default="development", alias="ENV")

    # Google Cloud設定
    GOOGLE_CLOUD_PROJECT: str = Field(alias="GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = Field(default="us-central1")
    GOOGLE_GENAI_USE_VERTEXAI: str = Field(default="True")
    GOOGLE_API_KEY: str = Field(default="")
    GOOGLE_AIPSK: str = Field(default="")

    # NextAuth.js認証設定
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    NEXTAUTH_SECRET: str = Field(default="")
    NEXTAUTH_URL: str = Field(default="http://localhost:3000")

    # データベース設定
    DATABASE_URL: str = Field(default="sqlite:///./data/genieus.db")
    DATABASE_TYPE: str = Field(default=os.getenv("DATABASE_TYPE", "postgresql"))

    # Cloud SQL PostgreSQL設定
    POSTGRES_USER: str = Field(default="genieus_user")
    POSTGRES_PASSWORD: str = Field(default="")
    POSTGRES_DB: str = Field(default="genieus_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    CLOUD_SQL_CONNECTION_NAME: str = Field(default="")

    # セキュリティ設定
    JWT_SECRET: str = Field(default="your-jwt-secret-key")
    JWT_EXPIRE_MINUTES: int = Field(default=1440)  # 24時間

    # サーバー設定
    PORT: int = Field(default=8000)
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:30001")

    # ログ設定
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")

    # ファイル設定
    ROOT_DIR: str | None = None
    BUCKET_NAME: str = Field(default="genieus-files")

    # ルーティング設定（ADK標準固定）
    ROUTING_LOG_LEVEL: str = Field(default="INFO")  # デバッグ用のみ保持

    model_config = SettingsConfigDict(
        env_file=".env.dev", 
        env_file_encoding="utf-8", 
        extra="ignore",
        env_prefix="",
        case_sensitive=False,
        env_file_has_priority=False  # 環境変数を優先
    )

    @field_validator("ROOT_DIR", mode="before")
    @classmethod
    def set_root_dir(cls, v):
        if v is not None:
            return v
        return normpath(join(dirname(abspath(__file__)), "..", ".."))
    
    @field_validator("DATABASE_TYPE", mode="before")
    @classmethod
    def set_database_type(cls, v):
        # Cloud Run環境でCloud SQL接続が設定されている場合はPostgreSQLを優先
        if os.getenv("CLOUD_SQL_CONNECTION_NAME"):
            return "postgresql"
        return v or os.getenv("DATABASE_TYPE", "sqlite")

    @model_validator(mode="after")
    def validate_settings(self):
        required_fields = ["GOOGLE_CLOUD_PROJECT"]

        # 本番環境では認証設定が必須
        if self.ENVIRONMENT == "production":
            required_fields.extend(["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "NEXTAUTH_SECRET", "JWT_SECRET"])

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
