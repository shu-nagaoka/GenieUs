"""予定イベントリポジトリ（PostgreSQL実装）

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from src.domain.entities import ScheduleEvent
from src.infrastructure.database.postgres_manager import PostgreSQLManager


class ScheduleEventRepository:
    """PostgreSQL予定イベントリポジトリ

    責務:
    - 予定イベントの永続化（PostgreSQL）
    - ユーザー別の予定管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, postgres_manager: PostgreSQLManager, logger: logging.Logger):
        """ScheduleEventRepository初期化

        Args:
            postgres_manager: PostgreSQLマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.postgres_manager = postgres_manager
        self.logger = logger
        self._table_name = "schedule_events"

    def save_schedule_event(self, schedule_event: ScheduleEvent) -> dict:
        """予定イベントを保存

        Args:
            schedule_event: 予定イベントエンティティ

        Returns:
            dict: 保存結果

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            self.logger.info(f"🗄️ PostgreSQL予定イベント保存: user_id={schedule_event.user_id}, title={schedule_event.title}")

            # 新規イベントの場合はIDを生成
            if not schedule_event.event_id:
                schedule_event.event_id = str(uuid4())

            # 現在時刻をセット
            now = datetime.now().isoformat()
            schedule_event.created_at = schedule_event.created_at or now
            schedule_event.updated_at = now

            query = f"""
            INSERT INTO {self._table_name} (
                event_id, user_id, title, description, start_time, end_time,
                location, participants, reminder_minutes, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                start_time = EXCLUDED.start_time,
                end_time = EXCLUDED.end_time,
                location = EXCLUDED.location,
                participants = EXCLUDED.participants,
                reminder_minutes = EXCLUDED.reminder_minutes,
                updated_at = EXCLUDED.updated_at
            """

            values = (
                schedule_event.event_id,
                schedule_event.user_id,
                schedule_event.title,
                schedule_event.description,
                schedule_event.start_time,
                schedule_event.end_time,
                schedule_event.location,
                json.dumps(schedule_event.participants or [], ensure_ascii=False),
                schedule_event.reminder_minutes,
                schedule_event.created_at,
                schedule_event.updated_at,
            )

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQL予定イベント保存完了: {schedule_event.event_id}")
            return {"event_id": schedule_event.event_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL予定イベント保存エラー: {e}")
            raise Exception(f"Failed to save schedule event to PostgreSQL: {str(e)}")

    def get_schedule_events(self, user_id: str, filters: dict[str, Any] | None = None) -> list[ScheduleEvent]:
        """予定イベント一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            list[ScheduleEvent]: 予定イベント一覧
        """
        try:
            self.logger.info(f"🔍 PostgreSQLユーザー別予定イベント取得: user_id={user_id}")

            where_conditions = ["user_id = %s"]
            params = [user_id]

            # フィルター処理
            if filters:
                if "start_date" in filters:
                    where_conditions.append("start_time >= %s")
                    params.append(filters["start_date"])
                if "end_date" in filters:
                    where_conditions.append("end_time <= %s")
                    params.append(filters["end_date"])

            query = f"""
            SELECT * FROM {self._table_name}
            WHERE {' AND '.join(where_conditions)}
            ORDER BY start_time ASC
            """

            rows = self.postgres_manager.execute_query(query, tuple(params))
            events = [self._row_to_schedule_event(row) for row in rows]

            self.logger.info(f"✅ PostgreSQLユーザー別予定イベント取得完了: {len(events)}件")
            return events

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLユーザー別予定イベント取得エラー: {e}")
            return []

    def get_schedule_event_by_id(self, event_id: str) -> ScheduleEvent | None:
        """ID指定予定イベント取得

        Args:
            event_id: イベントID

        Returns:
            ScheduleEvent | None: 予定イベント（存在しない場合はNone）
        """
        try:
            query = f"SELECT * FROM {self._table_name} WHERE event_id = %s"
            rows = self.postgres_manager.execute_query(query, (event_id,))

            if not rows:
                return None

            return self._row_to_schedule_event(rows[0])

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL予定イベントID取得エラー: {e}")
            return None

    def delete_schedule_event(self, event_id: str) -> bool:
        """予定イベント削除

        Args:
            event_id: 削除するイベントのID

        Returns:
            bool: 削除成功時True
        """
        try:
            self.logger.info(f"🗑️ PostgreSQL予定イベント削除: {event_id}")

            query = f"DELETE FROM {self._table_name} WHERE event_id = %s"
            self.postgres_manager.execute_update(query, (event_id,))

            self.logger.info(f"✅ PostgreSQL予定イベント削除完了: {event_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL予定イベント削除エラー: {e}")
            return False

    def _row_to_schedule_event(self, row: dict[str, Any]) -> ScheduleEvent:
        """データベース行をScheduleEventエンティティに変換

        Args:
            row: データベース行（辞書形式）

        Returns:
            ScheduleEvent: 予定イベントエンティティ
        """
        try:
            participants = json.loads(row["participants"]) if row["participants"] else []

            return ScheduleEvent(
                event_id=row["event_id"],
                user_id=row["user_id"],
                title=row["title"],
                description=row["description"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                location=row["location"],
                participants=participants,
                reminder_minutes=row["reminder_minutes"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL予定イベント行変換エラー: {e}")
            # エラー時はデフォルト値でScheduleEventを返す
            return ScheduleEvent(
                event_id=row.get("event_id", ""),
                user_id=row.get("user_id", ""),
                title=row.get("title", ""),
                description=row.get("description", ""),
                start_time=row.get("start_time", ""),
                end_time=row.get("end_time", ""),
                location=row.get("location", ""),
                participants=[],
                reminder_minutes=0,
                created_at=row.get("created_at", ""),
                updated_at=row.get("updated_at", ""),
            )