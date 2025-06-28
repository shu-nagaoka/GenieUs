"""食事記録リポジトリプロトコル

Clean Architecture準拠のリポジトリインターフェース定義
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol

from src.domain.entities import MealRecord, MealType


class MealRecordRepositoryProtocol(Protocol):
    """食事記録リポジトリプロトコル

    責務:
    - 食事記録の永続化操作
    - 検索・フィルタリング機能
    - 集計・分析用データ取得
    """

    @abstractmethod
    async def create(self, meal_record: MealRecord) -> MealRecord:
        """食事記録作成

        Args:
            meal_record: 食事記録エンティティ

        Returns:
            MealRecord: 作成された食事記録

        Raises:
            Exception: 作成に失敗した場合
        """
        pass

    @abstractmethod
    async def get_by_id(self, meal_record_id: str) -> MealRecord | None:
        """ID指定で食事記録取得

        Args:
            meal_record_id: 食事記録ID

        Returns:
            MealRecord | None: 食事記録（存在しない場合はNone）
        """
        pass

    @abstractmethod
    async def update(self, meal_record: MealRecord) -> MealRecord:
        """食事記録更新

        Args:
            meal_record: 更新する食事記録エンティティ

        Returns:
            MealRecord: 更新された食事記録

        Raises:
            Exception: 更新に失敗した場合
        """
        pass

    @abstractmethod
    async def delete(self, meal_record_id: str) -> bool:
        """食事記録削除

        Args:
            meal_record_id: 食事記録ID

        Returns:
            bool: 削除成功フラグ
        """
        pass

    @abstractmethod
    async def search(
        self,
        child_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        meal_type: MealType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MealRecord]:
        """食事記録検索

        Args:
            child_id: 子どもID
            start_date: 開始日時（指定なしの場合は制限なし）
            end_date: 終了日時（指定なしの場合は制限なし）
            meal_type: 食事タイプ（指定なしの場合は全タイプ）
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[MealRecord]: 検索結果
        """
        pass

    @abstractmethod
    async def count(
        self,
        child_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        meal_type: MealType | None = None,
    ) -> int:
        """食事記録件数取得

        Args:
            child_id: 子どもID
            start_date: 開始日時（指定なしの場合は制限なし）
            end_date: 終了日時（指定なしの場合は制限なし）
            meal_type: 食事タイプ（指定なしの場合は全タイプ）

        Returns:
            int: 該当件数
        """
        pass

    @abstractmethod
    async def get_by_child_id(self, child_id: str, limit: int = 50, offset: int = 0) -> list[MealRecord]:
        """子どもID指定で食事記録一覧取得

        Args:
            child_id: 子どもID
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[MealRecord]: 食事記録一覧
        """
        pass

    @abstractmethod
    async def get_recent_records(self, child_id: str, days: int = 7, limit: int = 100) -> list[MealRecord]:
        """最近の食事記録取得

        Args:
            child_id: 子どもID
            days: 過去何日分を取得するか
            limit: 取得件数上限

        Returns:
            list[MealRecord]: 最近の食事記録
        """
        pass
