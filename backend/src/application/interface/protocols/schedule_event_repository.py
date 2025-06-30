"""スケジュールイベントリポジトリプロトコル

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- プロトコル定義パターン
"""

from typing import Protocol
from src.domain.entities import ScheduleEvent


class ScheduleEventRepositoryProtocol(Protocol):
    """スケジュールイベントリポジトリプロトコル"""

    def save_schedule_event(self, schedule_event: ScheduleEvent) -> bool:
        """スケジュールイベント保存"""
        ...

    def get_schedule_events(self, user_id: str) -> list[ScheduleEvent]:
        """スケジュールイベント一覧取得"""
        ...

    def get_schedule_event_by_id(self, event_id: str) -> ScheduleEvent | None:
        """スケジュールイベント個別取得"""
        ...

    def delete_schedule_event(self, event_id: str) -> bool:
        """スケジュールイベント削除"""
        ...
