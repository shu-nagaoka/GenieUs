"""スケジュール記録リポジトリプロトコル

Clean Architecture準拠のリポジトリインターフェース定義
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol

from src.domain.entities import ScheduleEvent


class ScheduleRecordRepositoryProtocol(Protocol):
    """スケジュール記録リポジトリプロトコル

    責務:
    - スケジュール記録の永続化操作
    - 検索・フィルタリング機能
    - 日付・時間範囲での取得
    """

    @abstractmethod
    async def create(self, schedule_event: ScheduleEvent) -> ScheduleEvent:
        """スケジュール記録作成

        Args:
            schedule_event: スケジュールイベントエンティティ

        Returns:
            ScheduleEvent: 作成されたスケジュール記録

        Raises:
            Exception: 作成に失敗した場合
        """
        pass

    @abstractmethod
    async def get_by_id(self, schedule_id: str) -> ScheduleEvent | None:
        """ID指定でスケジュール記録取得

        Args:
            schedule_id: スケジュール記録ID

        Returns:
            ScheduleEvent | None: スケジュール記録（存在しない場合はNone）
        """
        pass

    @abstractmethod
    async def update(self, schedule_event: ScheduleEvent) -> ScheduleEvent:
        """スケジュール記録更新

        Args:
            schedule_event: 更新するスケジュールイベントエンティティ

        Returns:
            ScheduleEvent: 更新されたスケジュール記録

        Raises:
            Exception: 更新に失敗した場合
        """
        pass

    @abstractmethod
    async def delete(self, schedule_id: str) -> bool:
        """スケジュール記録削除

        Args:
            schedule_id: スケジュール記録ID

        Returns:
            bool: 削除成功フラグ
        """
        pass

    @abstractmethod
    async def search(
        self,
        user_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        event_type: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ScheduleEvent]:
        """スケジュール記録検索

        Args:
            user_id: ユーザーID
            start_date: 開始日時（指定なしの場合は制限なし）
            end_date: 終了日時（指定なしの場合は制限なし）
            event_type: イベントタイプ（指定なしの場合は全タイプ）
            status: ステータス（指定なしの場合は全ステータス）
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[ScheduleEvent]: 検索結果
        """
        pass

    @abstractmethod
    async def count(
        self,
        user_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        event_type: str | None = None,
        status: str | None = None,
    ) -> int:
        """スケジュール記録件数取得

        Args:
            user_id: ユーザーID
            start_date: 開始日時（指定なしの場合は制限なし）
            end_date: 終了日時（指定なしの場合は制限なし）
            event_type: イベントタイプ（指定なしの場合は全タイプ）
            status: ステータス（指定なしの場合は全ステータス）

        Returns:
            int: 該当件数
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> list[ScheduleEvent]:
        """ユーザーID指定でスケジュール記録一覧取得

        Args:
            user_id: ユーザーID
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[ScheduleEvent]: スケジュール記録一覧
        """
        pass

    @abstractmethod
    async def get_upcoming_events(self, user_id: str, days: int = 30, limit: int = 100) -> list[ScheduleEvent]:
        """今後の予定取得

        Args:
            user_id: ユーザーID
            days: 今後何日分を取得するか
            limit: 取得件数上限

        Returns:
            list[ScheduleEvent]: 今後の予定
        """
        pass

    @abstractmethod
    async def get_events_by_date(self, user_id: str, target_date: datetime) -> list[ScheduleEvent]:
        """指定日のイベント取得

        Args:
            user_id: ユーザーID
            target_date: 対象日付

        Returns:
            list[ScheduleEvent]: 指定日のイベント
        """
        pass
