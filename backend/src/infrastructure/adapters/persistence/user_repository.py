"""ユーザーRepository - SQLite実装"""

import logging
from datetime import datetime
from typing import Any

from src.application.interface.protocols.user_repository import UserRepositoryProtocol
from src.domain.entities import User
from src.infrastructure.database.sqlite_manager import SQLiteManager


class UserRepository(UserRepositoryProtocol):
    """ユーザーデータ永続化Repository（SQLite版）"""

    def __init__(self, sqlite_manager: SQLiteManager, logger: logging.Logger):
        self.sqlite_manager = sqlite_manager
        self.logger = logger

    async def create_user(self, user: User) -> User:
        """ユーザー作成"""
        try:
            self.logger.info(
                "ユーザー作成開始",
                extra={
                    "google_id": user.google_id,
                    "email": user.email,
                },
            )

            query = """
            INSERT INTO users (
                google_id, email, name, picture_url, locale, verified_email,
                created_at, last_login, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                user.google_id,
                user.email,
                user.name,
                user.picture_url,
                user.locale,
                user.verified_email,
                user.created_at.isoformat(),
                user.last_login.isoformat(),
                user.updated_at.isoformat(),
            )

            self.sqlite_manager.execute_update(query, params)

            self.logger.info(
                "ユーザー作成完了",
                extra={
                    "google_id": user.google_id,
                },
            )

            return user

        except Exception as e:
            self.logger.error(
                "ユーザー作成エラー",
                extra={
                    "error": str(e),
                    "google_id": user.google_id,
                },
            )
            raise

    async def get_user_by_google_id(self, google_id: str) -> User | None:
        """Google IDでユーザー取得"""
        try:
            self.logger.debug("ユーザー取得開始", extra={"google_id": google_id})

            query = "SELECT * FROM users WHERE google_id = ?"
            results = self.sqlite_manager.execute_query(query, (google_id,))

            if not results:
                self.logger.debug("ユーザー未存在", extra={"google_id": google_id})
                return None

            user_data = results[0]
            user = self._row_to_user(user_data)

            self.logger.debug(
                "ユーザー取得完了",
                extra={
                    "google_id": google_id,
                    "email": user.email,
                },
            )

            return user

        except Exception as e:
            self.logger.error(
                "ユーザー取得エラー",
                extra={
                    "error": str(e),
                    "google_id": google_id,
                },
            )
            raise

    async def get_user_by_email(self, email: str) -> User | None:
        """メールアドレスでユーザー取得"""
        try:
            self.logger.debug("ユーザー取得開始（メール）", extra={"email": email})

            query = "SELECT * FROM users WHERE email = ?"
            results = self.sqlite_manager.execute_query(query, (email,))

            if not results:
                self.logger.debug("ユーザー未存在（メール）", extra={"email": email})
                return None

            user_data = results[0]
            user = self._row_to_user(user_data)

            self.logger.debug(
                "ユーザー取得完了（メール）",
                extra={
                    "email": email,
                    "google_id": user.google_id,
                },
            )

            return user

        except Exception as e:
            self.logger.error(
                "ユーザー取得エラー（メール）",
                extra={
                    "error": str(e),
                    "email": email,
                },
            )
            raise

    async def update_user(self, user: User) -> User:
        """ユーザー更新"""
        try:
            self.logger.info(
                "ユーザー更新開始",
                extra={
                    "google_id": user.google_id,
                },
            )

            # 更新時刻を現在時刻に設定
            user.updated_at = datetime.now()

            query = """
            UPDATE users SET
                email = ?, name = ?, picture_url = ?, locale = ?,
                verified_email = ?, last_login = ?, updated_at = ?
            WHERE google_id = ?
            """

            params = (
                user.email,
                user.name,
                user.picture_url,
                user.locale,
                user.verified_email,
                user.last_login.isoformat(),
                user.updated_at.isoformat(),
                user.google_id,
            )

            affected_rows = self.sqlite_manager.execute_update(query, params)

            if affected_rows == 0:
                self.logger.warning(
                    "ユーザー更新対象なし",
                    extra={
                        "google_id": user.google_id,
                    },
                )
                raise ValueError(f"ユーザーが見つかりません: {user.google_id}")

            self.logger.info(
                "ユーザー更新完了",
                extra={
                    "google_id": user.google_id,
                },
            )

            return user

        except Exception as e:
            self.logger.error(
                "ユーザー更新エラー",
                extra={
                    "error": str(e),
                    "google_id": user.google_id,
                },
            )
            raise

    async def update_last_login(self, google_id: str) -> None:
        """最終ログイン時刻を更新"""
        try:
            now = datetime.now()

            query = """
            UPDATE users SET last_login = ?, updated_at = ?
            WHERE google_id = ?
            """

            params = (now.isoformat(), now.isoformat(), google_id)
            affected_rows = self.sqlite_manager.execute_update(query, params)

            if affected_rows == 0:
                self.logger.warning(
                    "最終ログイン更新対象なし",
                    extra={
                        "google_id": google_id,
                    },
                )
            else:
                self.logger.debug(
                    "最終ログイン更新完了",
                    extra={
                        "google_id": google_id,
                    },
                )

        except Exception as e:
            self.logger.error(
                "最終ログイン更新エラー",
                extra={
                    "error": str(e),
                    "google_id": google_id,
                },
            )
            raise

    async def delete_user(self, google_id: str) -> bool:
        """ユーザー削除"""
        try:
            self.logger.info(
                "ユーザー削除開始",
                extra={
                    "google_id": google_id,
                },
            )

            query = "DELETE FROM users WHERE google_id = ?"
            affected_rows = self.sqlite_manager.execute_update(query, (google_id,))

            if affected_rows == 0:
                self.logger.warning(
                    "ユーザー削除対象なし",
                    extra={
                        "google_id": google_id,
                    },
                )
                return False

            self.logger.info(
                "ユーザー削除完了",
                extra={
                    "google_id": google_id,
                },
            )

            return True

        except Exception as e:
            self.logger.error(
                "ユーザー削除エラー",
                extra={
                    "error": str(e),
                    "google_id": google_id,
                },
            )
            raise

    async def list_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        """ユーザー一覧取得"""
        try:
            self.logger.debug(
                "ユーザー一覧取得開始",
                extra={
                    "limit": limit,
                    "offset": offset,
                },
            )

            query = """
            SELECT * FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """

            results = self.sqlite_manager.execute_query(query, (limit, offset))
            users = [self._row_to_user(row) for row in results]

            self.logger.debug(
                "ユーザー一覧取得完了",
                extra={
                    "count": len(users),
                },
            )

            return users

        except Exception as e:
            self.logger.error(
                "ユーザー一覧取得エラー",
                extra={
                    "error": str(e),
                },
            )
            raise

    async def count_users(self) -> int:
        """ユーザー数カウント"""
        try:
            query = "SELECT COUNT(*) as count FROM users"
            results = self.sqlite_manager.execute_query(query)
            return results[0]["count"] if results else 0

        except Exception as e:
            self.logger.error(
                "ユーザー数カウントエラー",
                extra={
                    "error": str(e),
                },
            )
            raise

    def _row_to_user(self, row: dict[str, Any]) -> User:
        """SQLite行データからUserエンティティを作成"""
        return User(
            google_id=row["google_id"],
            email=row["email"],
            name=row["name"],
            picture_url=row["picture_url"],
            locale=row["locale"],
            verified_email=bool(row["verified_email"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_login=datetime.fromisoformat(row["last_login"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    async def create_or_update_user(self, user: User) -> User:
        """ユーザー作成または更新（upsert）"""
        try:
            existing_user = await self.get_user_by_google_id(user.google_id)

            if existing_user:
                # 既存ユーザーの更新
                user.created_at = existing_user.created_at  # 作成日時を保持
                return await self.update_user(user)
            else:
                # 新規ユーザー作成
                return await self.create_user(user)

        except Exception as e:
            self.logger.error(
                "ユーザー作成/更新エラー",
                extra={
                    "error": str(e),
                    "google_id": user.google_id,
                },
            )
            raise
