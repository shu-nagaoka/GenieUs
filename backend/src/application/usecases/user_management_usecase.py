"""ユーザー管理UseCase - Google OAuth統合"""

import logging
from typing import Any

from src.application.interface.protocols.user_repository import UserRepositoryProtocol
from src.domain.entities import User
from src.presentation.api.middleware.auth_middleware import JWTAuthenticator


class UserManagementUseCase:
    """ユーザー管理ビジネスロジック"""

    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        jwt_authenticator: JWTAuthenticator,
        logger: logging.Logger,
    ):
        self.user_repository = user_repository
        self.jwt_authenticator = jwt_authenticator
        self.logger = logger

    def login_with_google_oauth(self, google_user_info: dict[str, Any]) -> dict[str, Any]:
        """Google OAuth情報でログイン処理"""
        try:
            self.logger.info(
                "Google OAuthログイン開始",
                extra={
                    "email": google_user_info.get("email"),
                    "google_id": google_user_info.get("sub"),
                },
            )

            # Google OAuth情報からUserエンティティ作成
            user = User.from_google_oauth(google_user_info)

            # ユーザー作成または更新（upsert）
            stored_user = self.user_repository.create_or_update_user(user)

            # 最終ログイン時刻を更新
            self.user_repository.update_last_login(stored_user.google_id)

            # JWTトークン生成
            access_token = self.jwt_authenticator.create_access_token(stored_user)

            self.logger.info(
                "Google OAuthログイン完了",
                extra={
                    "google_id": stored_user.google_id,
                    "email": stored_user.email,
                },
            )

            return {
                "success": True,
                "user": stored_user.to_dict(),
                "access_token": access_token,
                "token_type": "bearer",
            }

        except Exception as e:
            self.logger.error(
                "Google OAuthログインエラー",
                extra={
                    "error": str(e),
                    "email": google_user_info.get("email"),
                },
            )
            return {
                "success": False,
                "error": "ログインに失敗しました",
                "detail": str(e),
            }

    def get_user_profile(self, google_id: str) -> dict[str, Any]:
        """ユーザープロフィール取得"""
        try:
            self.logger.debug(
                "ユーザープロフィール取得開始",
                extra={
                    "google_id": google_id,
                },
            )

            user = self.user_repository.get_user_by_google_id(google_id)

            if not user:
                self.logger.warning(
                    "ユーザー未存在",
                    extra={
                        "google_id": google_id,
                    },
                )
                return {
                    "success": False,
                    "error": "ユーザーが見つかりません",
                }

            self.logger.debug(
                "ユーザープロフィール取得完了",
                extra={
                    "google_id": google_id,
                },
            )

            return {
                "success": True,
                "user": user.to_dict(),
            }

        except Exception as e:
            self.logger.error(
                "ユーザープロフィール取得エラー",
                extra={
                    "error": str(e),
                    "google_id": google_id,
                },
            )
            return {
                "success": False,
                "error": "プロフィール取得に失敗しました",
                "detail": str(e),
            }

    def update_user_profile(self, google_id: str, profile_data: dict[str, Any]) -> dict[str, Any]:
        """ユーザープロフィール更新"""
        try:
            self.logger.info(
                "ユーザープロフィール更新開始",
                extra={
                    "google_id": google_id,
                },
            )

            # 既存ユーザー取得
            user = self.user_repository.get_user_by_google_id(google_id)

            if not user:
                self.logger.warning(
                    "ユーザー未存在（更新）",
                    extra={
                        "google_id": google_id,
                    },
                )
                return {
                    "success": False,
                    "error": "ユーザーが見つかりません",
                }

            # 更新可能フィールドのみ更新
            if "name" in profile_data:
                user.name = profile_data["name"]
            if "picture_url" in profile_data:
                user.picture_url = profile_data["picture_url"]
            if "locale" in profile_data:
                user.locale = profile_data["locale"]

            # ユーザー更新
            updated_user = self.user_repository.update_user(user)

            self.logger.info(
                "ユーザープロフィール更新完了",
                extra={
                    "google_id": google_id,
                },
            )

            return {
                "success": True,
                "user": updated_user.to_dict(),
            }

        except Exception as e:
            self.logger.error(
                "ユーザープロフィール更新エラー",
                extra={
                    "error": str(e),
                    "google_id": google_id,
                },
            )
            return {
                "success": False,
                "error": "プロフィール更新に失敗しました",
                "detail": str(e),
            }

    def delete_user_account(self, google_id: str) -> dict[str, Any]:
        """ユーザーアカウント削除"""
        try:
            self.logger.info(
                "ユーザーアカウント削除開始",
                extra={
                    "google_id": google_id,
                },
            )

            # ユーザー存在確認
            user = self.user_repository.get_user_by_google_id(google_id)

            if not user:
                self.logger.warning(
                    "ユーザー未存在（削除）",
                    extra={
                        "google_id": google_id,
                    },
                )
                return {
                    "success": False,
                    "error": "ユーザーが見つかりません",
                }

            # ユーザー削除（関連データはCASCADE削除）
            deleted = self.user_repository.delete_user(google_id)

            if not deleted:
                return {
                    "success": False,
                    "error": "削除に失敗しました",
                }

            self.logger.info(
                "ユーザーアカウント削除完了",
                extra={
                    "google_id": google_id,
                    "email": user.email,
                },
            )

            return {
                "success": True,
                "message": "アカウントが削除されました",
            }

        except Exception as e:
            self.logger.error(
                "ユーザーアカウント削除エラー",
                extra={
                    "error": str(e),
                    "google_id": google_id,
                },
            )
            return {
                "success": False,
                "error": "アカウント削除に失敗しました",
                "detail": str(e),
            }

    def verify_user_token(self, token: str) -> dict[str, Any]:
        """JWTトークン検証"""
        try:
            self.logger.debug("トークン検証開始")

            # JWTトークン検証
            payload = self.jwt_authenticator.verify_token(token)
            google_id = payload.get("sub")

            if not google_id:
                return {
                    "success": False,
                    "error": "無効なトークンです",
                }

            # ユーザー存在確認
            user = self.user_repository.get_user_by_google_id(google_id)

            if not user:
                self.logger.warning(
                    "トークンユーザー未存在",
                    extra={
                        "google_id": google_id,
                    },
                )
                return {
                    "success": False,
                    "error": "ユーザーが見つかりません",
                }

            self.logger.debug(
                "トークン検証完了",
                extra={
                    "google_id": google_id,
                },
            )

            return {
                "success": True,
                "user": user.to_dict(),
                "token_payload": payload,
            }

        except Exception as e:
            self.logger.warning(
                "トークン検証エラー",
                extra={
                    "error": str(e),
                },
            )
            return {
                "success": False,
                "error": "トークン検証に失敗しました",
                "detail": str(e),
            }

    def refresh_token(self, google_id: str) -> dict[str, Any]:
        """トークンリフレッシュ"""
        try:
            self.logger.debug(
                "トークンリフレッシュ開始",
                extra={
                    "google_id": google_id,
                },
            )

            # ユーザー取得
            user = self.user_repository.get_user_by_google_id(google_id)

            if not user:
                return {
                    "success": False,
                    "error": "ユーザーが見つかりません",
                }

            # 最終ログイン時刻を更新
            self.user_repository.update_last_login(google_id)

            # 新しいJWTトークン生成
            access_token = self.jwt_authenticator.create_access_token(user)

            self.logger.debug(
                "トークンリフレッシュ完了",
                extra={
                    "google_id": google_id,
                },
            )

            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
            }

        except Exception as e:
            self.logger.error(
                "トークンリフレッシュエラー",
                extra={
                    "error": str(e),
                    "google_id": google_id,
                },
            )
            return {
                "success": False,
                "error": "トークンリフレッシュに失敗しました",
                "detail": str(e),
            }
