"""認証ミドルウェア - JWT + Google OAuth Token検証"""

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError

from src.config.settings import AppSettings
from src.domain.entities import User


class AuthError(Exception):
    """認証エラー"""

    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GoogleTokenVerifier:
    """Google OAuth Token検証クラス"""

    GOOGLE_TOKEN_VERIFY_URL = "https://oauth2.googleapis.com/tokeninfo"

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def verify_google_token(self, token: str) -> dict[str, Any] | None:
        """Google OAuth Tokenを検証してユーザー情報を取得"""
        try:
            self.logger.info("Google Token検証開始")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.GOOGLE_TOKEN_VERIFY_URL,
                    params={"access_token": token},
                    timeout=10.0,
                )

                if response.status_code != 200:
                    self.logger.warning(f"Google Token検証失敗: {response.status_code}")
                    return None

                token_info = response.json()

                # トークンの有効性チェック
                if "error" in token_info:
                    self.logger.warning(f"無効なGoogle Token: {token_info.get('error')}")
                    return None

                self.logger.info(
                    "Google Token検証成功",
                    extra={
                        "user_id": token_info.get("sub"),
                        "email": token_info.get("email"),
                    },
                )

                return token_info

        except Exception as e:
            self.logger.error(f"Google Token検証エラー: {e}")
            return None


class JWTAuthenticator:
    """JWT認証管理クラス"""

    def __init__(self, settings: AppSettings, logger: logging.Logger):
        self.settings = settings
        self.logger = logger
        self.security = HTTPBearer(auto_error=False)

    def create_access_token(self, user: User) -> str:
        """アクセストークン生成"""
        try:
            payload = {
                "sub": user.google_id,
                "email": user.email,
                "name": user.name,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=self.settings.JWT_EXPIRE_MINUTES),
            }

            token = jwt.encode(
                payload,
                self.settings.JWT_SECRET,
                algorithm="HS256",
            )

            self.logger.info(
                "JWTトークン生成完了",
                extra={
                    "user_id": user.google_id,
                    "expires_at": payload["exp"].isoformat(),
                },
            )

            return token

        except Exception as e:
            self.logger.error(f"JWTトークン生成エラー: {e}")
            raise AuthError("トークン生成に失敗しました")

    def verify_token(self, token: str) -> dict[str, Any]:
        """JWTトークン検証"""
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET,
                algorithms=["HS256"],
            )

            self.logger.debug(
                "JWTトークン検証成功",
                extra={
                    "user_id": payload.get("sub"),
                },
            )

            return payload

        except jwt.ExpiredSignatureError:
            self.logger.warning("期限切れJWTトークン")
            raise AuthError("トークンの有効期限が切れています")
        except PyJWTError as e:
            self.logger.warning(f"無効なJWTトークン: {e}")
            raise AuthError("無効なトークンです")
        except Exception as e:
            self.logger.error(f"JWTトークン検証エラー: {e}")
            raise AuthError("認証に失敗しました")


class AuthMiddleware:
    """認証ミドルウェア - Composition Root統合版"""

    def __init__(
        self,
        settings: AppSettings,
        logger: logging.Logger,
        google_verifier: GoogleTokenVerifier,
        jwt_authenticator: JWTAuthenticator,
    ):
        self.settings = settings
        self.logger = logger
        self.google_verifier = google_verifier
        self.jwt_authenticator = jwt_authenticator

    async def authenticate_request(
        self,
        authorization: HTTPAuthorizationCredentials | None,
    ) -> dict[str, Any] | None:
        """リクエスト認証

        1. JWTトークン検証 (優先)
        2. Google OAuth Token検証 (フォールバック)
        """
        if not authorization:
            return None

        token = authorization.credentials

        try:
            # 1. JWTトークン検証を試行
            self.logger.debug("JWT認証を試行")
            payload = self.jwt_authenticator.verify_token(token)

            return {
                "user_id": payload["sub"],
                "email": payload["email"],
                "name": payload["name"],
                "auth_type": "jwt",
            }

        except AuthError:
            # 2. Google OAuth Token検証にフォールバック
            self.logger.debug("Google OAuth認証にフォールバック")
            google_user_info = await self.google_verifier.verify_google_token(token)

            if google_user_info:
                return {
                    "user_id": google_user_info["sub"],
                    "email": google_user_info["email"],
                    "name": google_user_info.get("name", ""),
                    "auth_type": "google_oauth",
                }

        self.logger.warning("認証失敗: 無効なトークン")
        return None

    async def require_authentication(
        self,
        authorization: HTTPAuthorizationCredentials | None,
    ) -> dict[str, Any]:
        """必須認証 - 認証が必要なエンドポイント用"""
        user_context = await self.authenticate_request(authorization)

        if not user_context:
            self.logger.warning("認証が必要なエンドポイントへの未認証アクセス")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証が必要です",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.logger.info(
            "認証成功",
            extra={
                "user_id": user_context["user_id"],
                "auth_type": user_context["auth_type"],
            },
        )

        return user_context

    async def optional_authentication(
        self,
        authorization: HTTPAuthorizationCredentials | None,
    ) -> dict[str, Any] | None:
        """オプション認証 - 認証が任意のエンドポイント用"""
        user_context = await self.authenticate_request(authorization)

        if user_context:
            self.logger.info(
                "オプション認証成功",
                extra={
                    "user_id": user_context["user_id"],
                    "auth_type": user_context["auth_type"],
                },
            )
        else:
            self.logger.debug("未認証ユーザーによるアクセス")

        return user_context
