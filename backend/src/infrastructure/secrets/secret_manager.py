"""Google Secret Manager統合クラス

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import logging
from typing import Any

from google.cloud import secretmanager
from google.cloud.secretmanager import SecretManagerServiceClient

from src.config.settings import AppSettings


class SecretManagerService:
    """Google Secret Manager統合サービス

    Cloud SQLパスワードや機密情報の安全な管理
    """

    def __init__(self, settings: AppSettings, logger: logging.Logger):
        """Secret Manager サービス初期化

        Args:
            settings: アプリケーション設定
            logger: DIコンテナから注入されるロガー
        """
        self.settings = settings
        self.logger = logger
        self.project_id = settings.GOOGLE_CLOUD_PROJECT

        try:
            self.client = SecretManagerServiceClient()
            self.logger.info(f"Secret Manager初期化完了: project={self.project_id}")
        except Exception as e:
            self.logger.error(f"Secret Manager初期化エラー: {e}")
            raise RuntimeError(f"Secret Manager接続に失敗しました: {e}") from e

    def get_secret(self, secret_id: str, version_id: str = "latest") -> str:
        """シークレット値取得

        Args:
            secret_id: シークレットID
            version_id: バージョンID（デフォルト: latest）

        Returns:
            str: シークレット値

        Raises:
            RuntimeError: シークレット取得エラー
        """
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"

            self.logger.debug(f"シークレット取得: {secret_id}")
            response = self.client.access_secret_version(request={"name": name})

            secret_value = response.payload.data.decode("UTF-8")
            self.logger.info(f"✅ シークレット取得成功: {secret_id}")

            return secret_value

        except Exception as e:
            self.logger.error(f"❌ シークレット取得エラー ({secret_id}): {e}")
            raise RuntimeError(f"シークレット取得に失敗しました: {secret_id}") from e

    def get_postgres_password(self) -> str:
        """PostgreSQLパスワード取得

        Returns:
            str: PostgreSQLパスワード
        """
        try:
            return self.get_secret("postgres-password")
        except Exception as e:
            self.logger.warning(f"Secret Managerからのパスワード取得失敗: {e}")
            # フォールバック: 環境変数
            return self.settings.POSTGRES_PASSWORD or "fallback_demo_password"

    def get_jwt_secret(self) -> str:
        """JWT秘密鍵取得

        Returns:
            str: JWT秘密鍵
        """
        try:
            return self.get_secret("jwt-secret")
        except Exception as e:
            self.logger.warning(f"Secret ManagerからのJWT秘密鍵取得失敗: {e}")
            # フォールバック: 環境変数
            return self.settings.JWT_SECRET

    def get_nextauth_secret(self) -> str:
        """NextAuth秘密鍵取得

        Returns:
            str: NextAuth秘密鍵
        """
        try:
            return self.get_secret("nextauth-secret")
        except Exception as e:
            self.logger.warning(f"Secret ManagerからのNextAuth秘密鍵取得失敗: {e}")
            # フォールバック: 環境変数
            return self.settings.NEXTAUTH_SECRET

    def get_google_oauth_credentials(self) -> dict[str, str]:
        """Google OAuth認証情報取得

        Returns:
            dict: Google OAuth認証情報
        """
        try:
            client_id = self.get_secret("google-oauth-client-id")
            client_secret = self.get_secret("google-oauth-client-secret")

            return {"client_id": client_id, "client_secret": client_secret}

        except Exception as e:
            self.logger.warning(f"Secret ManagerからのOAuth認証情報取得失敗: {e}")
            # フォールバック: 環境変数
            return {"client_id": self.settings.GOOGLE_CLIENT_ID, "client_secret": self.settings.GOOGLE_CLIENT_SECRET}

    def create_secret_if_not_exists(self, secret_id: str, secret_value: str) -> bool:
        """シークレット作成（存在しない場合）

        Args:
            secret_id: シークレットID
            secret_value: シークレット値

        Returns:
            bool: 作成成功時True
        """
        try:
            parent = f"projects/{self.project_id}"

            # シークレット存在確認
            try:
                self.get_secret(secret_id)
                self.logger.info(f"シークレット既存: {secret_id}")
                return True
            except RuntimeError:
                # シークレットが存在しない場合は作成
                pass

            # シークレット作成
            secret = {"replication": {"automatic": {}}}

            create_response = self.client.create_secret(
                request={"parent": parent, "secret_id": secret_id, "secret": secret}
            )

            # シークレット値追加
            self.client.add_secret_version(
                request={"parent": create_response.name, "payload": {"data": secret_value.encode("UTF-8")}}
            )

            self.logger.info(f"✅ シークレット作成成功: {secret_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ シークレット作成エラー ({secret_id}): {e}")
            return False

    def setup_demo_secrets(self) -> bool:
        """デモ用シークレット設定

        Returns:
            bool: 設定成功時True
        """
        try:
            self.logger.info("🔐 デモ用シークレット設定開始")

            demo_secrets = {
                "postgres-password": "genieus_demo_secure_password_2024",
                "jwt-secret": "genieus_demo_jwt_secret_key_very_secure_2024",
                "nextauth-secret": "genieus_demo_nextauth_secret_key_2024",
                "google-oauth-client-id": "demo_client_id",
                "google-oauth-client-secret": "demo_client_secret",
            }

            success_count = 0
            for secret_id, secret_value in demo_secrets.items():
                if self.create_secret_if_not_exists(secret_id, secret_value):
                    success_count += 1

            self.logger.info(f"✅ デモ用シークレット設定完了: {success_count}/{len(demo_secrets)}")
            return success_count == len(demo_secrets)

        except Exception as e:
            self.logger.error(f"❌ デモ用シークレット設定エラー: {e}")
            return False
