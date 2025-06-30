"""ユーザーリポジトリプロトコル

Clean Architecture準拠のリポジトリインターフェース定義
"""

from abc import ABC, abstractmethod
from typing import Protocol

from src.domain.entities import User


class UserRepositoryProtocol(Protocol):
    """ユーザーリポジトリプロトコル

    責務:
    - ユーザー情報の永続化操作
    - Google OAuth統合
    - 検索・取得機能
    """

    @abstractmethod
    def create_user(self, user: User) -> User:
        """ユーザー作成

        Args:
            user: ユーザーエンティティ

        Returns:
            User: 作成されたユーザー

        Raises:
            Exception: 作成に失敗した場合
        """
        pass

    @abstractmethod
    def get_user_by_google_id(self, google_id: str) -> User | None:
        """Google IDでユーザー取得

        Args:
            google_id: Google ID

        Returns:
            User | None: ユーザー（存在しない場合はNone）
        """
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User | None:
        """メールアドレスでユーザー取得

        Args:
            email: メールアドレス

        Returns:
            User | None: ユーザー（存在しない場合はNone）
        """
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        """ユーザー更新

        Args:
            user: 更新するユーザーエンティティ

        Returns:
            User: 更新されたユーザー

        Raises:
            Exception: 更新に失敗した場合
        """
        pass

    @abstractmethod
    def update_last_login(self, google_id: str) -> None:
        """最終ログイン時刻を更新

        Args:
            google_id: Google ID

        Raises:
            Exception: 更新に失敗した場合
        """
        pass

    @abstractmethod
    def delete_user(self, google_id: str) -> bool:
        """ユーザー削除

        Args:
            google_id: Google ID

        Returns:
            bool: 削除成功フラグ
        """
        pass

    @abstractmethod
    def list_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        """ユーザー一覧取得

        Args:
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[User]: ユーザー一覧
        """
        pass

    @abstractmethod
    def count_users(self) -> int:
        """ユーザー数カウント

        Returns:
            int: 総ユーザー数
        """
        pass

    @abstractmethod
    def create_or_update_user(self, user: User) -> User:
        """ユーザー作成または更新（upsert）

        Args:
            user: ユーザーエンティティ

        Returns:
            User: 作成または更新されたユーザー

        Raises:
            Exception: 処理に失敗した場合
        """
        pass