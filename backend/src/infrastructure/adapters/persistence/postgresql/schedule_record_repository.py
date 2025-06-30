"""スケジュール記録リポジトリ（PostgreSQL実装）

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

from src.application.interface.protocols.schedule_record_repository import ScheduleRecordRepositoryProtocol
from src.domain.entities import ScheduleEvent
from src.infrastructure.database.postgres_manager import PostgreSQLManager


class ScheduleRecordRepository(ScheduleRecordRepositoryProtocol):
    """PostgreSQLスケジュール記録リポジトリ

    責務:
    - スケジュール記録の永続化（PostgreSQL）
    - 検索・集計機能の実装
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, postgres_manager: PostgreSQLManager, logger: logging.Logger):
        """ScheduleRecordRepository初期化

        Args:
            postgres_manager: PostgreSQLマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.postgres_manager = postgres_manager
        self.logger = logger
        self._table_name = "schedule_records"

    def create(self, schedule_event: ScheduleEvent) -> ScheduleEvent:
        """スケジュール記録作成

        Args:
            schedule_event: スケジュールイベントエンティティ

        Returns:
            ScheduleEvent: 作成されたスケジュール記録

        Raises:
            Exception: 作成に失敗した場合
        """
        try:
            self.logger.info(f"🐘 PostgreSQLスケジュール記録DB作成: {schedule_event.title}")

            # 現在時刻をISO形式でセット
            now = datetime.now().isoformat()
            if not schedule_event.created_at:
                schedule_event.created_at = now
            schedule_event.updated_at = now

            query = f"""
            INSERT INTO {self._table_name} (
                id, user_id, title, date, time, type, location, 
                description, status, created_by, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                schedule_event.event_id,
                schedule_event.user_id,
                schedule_event.title,
                schedule_event.date,
                schedule_event.time,
                schedule_event.type,
                schedule_event.location,
                schedule_event.description,
                schedule_event.status,
                schedule_event.created_by,
                schedule_event.created_at,
                schedule_event.updated_at,
            )

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQLスケジュール記録DB作成完了: {schedule_event.event_id}")
            return schedule_event

        except Exception as e:
            self.logger.error(f"❌ スケジュール記録DB作成エラー: {e}")
            raise Exception(f"Failed to create schedule record in database: {str(e)}")

    def get_by_id(self, schedule_id: str) -> ScheduleEvent | None:
        """ID指定でスケジュール記録取得

        Args:
            schedule_id: スケジュール記録ID

        Returns:
            ScheduleEvent | None: スケジュール記録（存在しない場合はNone）
        """
        try:
            self.logger.debug(f"🔍 PostgreSQLスケジュール記録DB取得: {schedule_id}")

            query = f"SELECT * FROM {self._table_name} WHERE id = %s"
            results = self.postgres_manager.execute_query(query, (schedule_id,))

            if not results:
                return None

            return self._row_to_schedule_event(results[0])

        except Exception as e:
            self.logger.error(f"❌ スケジュール記録DB取得エラー: {e}")
            raise Exception(f"Failed to get schedule record from database: {str(e)}")

    def update(self, schedule_event: ScheduleEvent) -> ScheduleEvent:
        """スケジュール記録更新

        Args:
            schedule_event: 更新するスケジュールイベントエンティティ

        Returns:
            ScheduleEvent: 更新されたスケジュール記録

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            self.logger.info(f"📝 PostgreSQLスケジュール記録DB更新: {schedule_event.event_id}")

            # 更新時刻をセット
            schedule_event.updated_at = datetime.now().isoformat()

            query = f"""
            UPDATE {self._table_name} SET
                title = %s, date = %s, time = %s, type = %s, location = %s,
                description = %s, status = %s, updated_at = %s
            WHERE id = %s
            """

            values = (
                schedule_event.title,
                schedule_event.date,
                schedule_event.time,
                schedule_event.type,
                schedule_event.location,
                schedule_event.description,
                schedule_event.status,
                schedule_event.updated_at,
                schedule_event.event_id,
            )

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQLスケジュール記録DB更新完了: {schedule_event.event_id}")
            return schedule_event

        except Exception as e:
            self.logger.error(f"❌ スケジュール記録DB更新エラー: {e}")
            raise Exception(f"Failed to update schedule record in database: {str(e)}")

    def delete(self, schedule_id: str) -> bool:
        """スケジュール記録削除

        Args:
            schedule_id: スケジュール記録ID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            self.logger.info(f"🗑️ PostgreSQLスケジュール記録DB削除: {schedule_id}")

            query = f"DELETE FROM {self._table_name} WHERE id = %s"
            affected_rows = self.postgres_manager.execute_update(query, (schedule_id,))

            success = affected_rows > 0
            if success:
                self.logger.info(f"✅ PostgreSQLスケジュール記録DB削除完了: {schedule_id}")
            else:
                self.logger.warning(f"⚠️ 削除対象のスケジュール記録が見つかりません: {schedule_id}")

            return success

        except Exception as e:
            self.logger.error(f"❌ スケジュール記録DB削除エラー: {e}")
            raise Exception(f"Failed to delete schedule record from database: {str(e)}")

    def search(
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
        try:
            self.logger.debug(f"🔍 PostgreSQLスケジュール記録DB検索: user_id={user_id}")

            # WHERE句構築
            where_conditions = ["user_id = %s"]
            values = [user_id]

            if start_date:
                where_conditions.append("date >= %s")
                values.append(start_date.strftime("%Y-%m-%d"))

            if end_date:
                where_conditions.append("date <= %s")
                values.append(end_date.strftime("%Y-%m-%d"))

            if event_type:
                where_conditions.append("type = %s")
                values.append(event_type)

            if status:
                where_conditions.append("status = %s")
                values.append(status)

            where_clause = " AND ".join(where_conditions)

            query = f"""
            SELECT * FROM {self._table_name}
            WHERE {where_clause}
            ORDER BY date DESC, time DESC
            LIMIT %s OFFSET %s
            """

            values.extend([limit, offset])

            results = self.postgres_manager.execute_query(query, tuple(values))

            schedule_events = [self._row_to_schedule_event(row) for row in results]

            self.logger.debug(f"✅ PostgreSQLスケジュール記録DB検索完了: {len(schedule_events)}件")
            return schedule_events

        except Exception as e:
            self.logger.error(f"❌ スケジュール記録DB検索エラー: {e}")
            raise Exception(f"Failed to search schedule records in database: {str(e)}")

    def count(
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
        try:
            # WHERE句構築（searchメソッドと同じロジック）
            where_conditions = ["user_id = %s"]
            values = [user_id]

            if start_date:
                where_conditions.append("date >= %s")
                values.append(start_date.strftime("%Y-%m-%d"))

            if end_date:
                where_conditions.append("date <= %s")
                values.append(end_date.strftime("%Y-%m-%d"))

            if event_type:
                where_conditions.append("type = %s")
                values.append(event_type)

            if status:
                where_conditions.append("status = %s")
                values.append(status)

            where_clause = " AND ".join(where_conditions)

            query = f"SELECT COUNT(*) FROM {self._table_name} WHERE {where_clause}"

            results = self.postgres_manager.execute_query(query, tuple(values))
            return results[0]["count"] if results else 0

        except Exception as e:
            self.logger.error(f"❌ スケジュール記録DB件数取得エラー: {e}")
            raise Exception(f"Failed to count schedule records in database: {str(e)}")

    def get_by_user_id(self, user_id: str, limit: int = 50, offset: int = 0) -> list[ScheduleEvent]:
        """ユーザーID指定でスケジュール記録一覧取得

        Args:
            user_id: ユーザーID
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[ScheduleEvent]: スケジュール記録一覧
        """
        return self.search(user_id=user_id, limit=limit, offset=offset)

    def get_upcoming_events(self, user_id: str, days: int = 30, limit: int = 100) -> list[ScheduleEvent]:
        """今後の予定取得

        Args:
            user_id: ユーザーID
            days: 今後何日分を取得するか
            limit: 取得件数上限

        Returns:
            list[ScheduleEvent]: 今後の予定
        """
        from datetime import timedelta

        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)

        return self.search(user_id=user_id, start_date=start_date, end_date=end_date, status="upcoming", limit=limit)

    def get_events_by_date(self, user_id: str, target_date: datetime) -> list[ScheduleEvent]:
        """指定日のイベント取得

        Args:
            user_id: ユーザーID
            target_date: 対象日付

        Returns:
            list[ScheduleEvent]: 指定日のイベント
        """
        return self.search(user_id=user_id, start_date=target_date, end_date=target_date, limit=100)

    def _row_to_schedule_event(self, row: dict[str, Any]) -> ScheduleEvent:
        """データベース行をScheduleEventエンティティに変換

        Args:
            row: データベース行データ（辞書形式）

        Returns:
            ScheduleEvent: スケジュールイベントエンティティ
        """
        try:
            return ScheduleEvent(
                event_id=row["id"],
                user_id=row["user_id"],
                title=row["title"],
                date=row["date"] or "",
                time=row["time"] or "",
                type=row["type"] or "",
                location=row["location"],
                description=row["description"],
                status=row["status"] or "upcoming",
                created_by=row["created_by"] or "genie",
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        except Exception as e:
            self.logger.error(f"❌ データベース行変換エラー: {e}")
            raise Exception(f"Failed to convert database row to ScheduleEvent: {str(e)}")

    def initialize_table(self) -> None:
        """テーブル初期化（開発・テスト用）"""
        try:
            self.logger.info(f"🐘 PostgreSQLスケジュール記録テーブル初期化: {self._table_name}")

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                date TEXT,
                time TEXT,
                type TEXT,
                location TEXT,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'upcoming',
                created_by TEXT NOT NULL DEFAULT 'genie',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """

            self.postgres_manager.execute_update(create_table_query)

            # インデックス作成
            index_queries = [
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_user_id ON {self._table_name}(user_id)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_date ON {self._table_name}(date)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_type ON {self._table_name}(type)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_status ON {self._table_name}(status)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_user_date ON {self._table_name}(user_id, date)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_user_status ON {self._table_name}(user_id, status)",
            ]

            for index_query in index_queries:
                self.postgres_manager.execute_update(index_query)

            self.logger.info(f"✅ PostgreSQLスケジュール記録テーブル初期化完了: {self._table_name}")

        except Exception as e:
            self.logger.error(f"❌ スケジュール記録テーブル初期化エラー: {e}")
            raise Exception(f"Failed to initialize schedule records table: {str(e)}")
