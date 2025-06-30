"""努力レポートリポジトリ（PostgreSQL実装）

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

from src.application.interface.protocols.effort_report_repository import EffortReportRepositoryProtocol
from src.domain.entities import EffortReportRecord
from src.infrastructure.database.postgres_manager import PostgreSQLManager


class EffortReportRepository(EffortReportRepositoryProtocol):
    """PostgreSQL努力レポートリポジトリ

    責務:
    - 努力レポートの永続化（PostgreSQL）
    - ユーザー別の努力レポート管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, postgres_manager: PostgreSQLManager, logger: logging.Logger):
        """EffortReportRepository初期化

        Args:
            postgres_manager: PostgreSQLマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.postgres_manager = postgres_manager
        self.logger = logger
        self._table_name = "effort_reports"

    def create(self, effort_report: EffortReportRecord) -> EffortReportRecord:
        """努力レポート作成

        Args:
            effort_report: 努力レポートエンティティ

        Returns:
            EffortReportRecord: 作成された努力レポート

        Raises:
            Exception: 作成に失敗した場合
        """
        try:
            self.logger.info(
                f"🐘 PostgreSQL努力レポートDB作成: user_id={effort_report.user_id}, score={effort_report.score}"
            )

            # 現在時刻をセット
            now = datetime.now()
            if not effort_report.created_at:
                effort_report.created_at = now.isoformat()
            effort_report.updated_at = now.isoformat()

            query = f"""
            INSERT INTO {self._table_name} (
                report_id, user_id, period_days, effort_count, score,
                highlights, categories, summary, achievements,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                effort_report.report_id,
                effort_report.user_id,
                effort_report.period_days,
                effort_report.effort_count,
                effort_report.score,
                json.dumps(effort_report.highlights, ensure_ascii=False),
                json.dumps(effort_report.categories, ensure_ascii=False),
                effort_report.summary,
                json.dumps(effort_report.achievements, ensure_ascii=False),
                effort_report.created_at,
                effort_report.updated_at,
            )

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQL努力レポートDB作成完了: {effort_report.report_id}")
            return effort_report

        except Exception as e:
            self.logger.error(f"❌ 努力レポートDB作成エラー: {e}")
            raise Exception(f"Failed to create effort report in database: {str(e)}")

    def get_by_id(self, report_id: str) -> EffortReportRecord | None:
        """ID指定で努力レポート取得

        Args:
            report_id: 努力レポートID

        Returns:
            EffortReportRecord | None: 努力レポート（存在しない場合はNone）
        """
        try:
            self.logger.debug(f"🔍 PostgreSQL努力レポートDB取得: {report_id}")

            query = f"SELECT * FROM {self._table_name} WHERE report_id = %s"
            results = self.postgres_manager.execute_query(query, (report_id,))

            if not results:
                return None

            return self._row_to_effort_report(results[0])

        except Exception as e:
            self.logger.error(f"❌ 努力レポートDB取得エラー: {e}")
            raise Exception(f"Failed to get effort report from database: {str(e)}")

    def get_by_user_id(
        self,
        user_id: str,
        filters: dict[str, Any] | None = None,
    ) -> list[EffortReportRecord]:
        """ユーザーID指定で努力レポート一覧取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件（オプション）

        Returns:
            list[EffortReportRecord]: 努力レポート一覧
        """
        try:
            self.logger.debug(f"🔍 PostgreSQL努力レポート一覧DB取得: user_id={user_id}")

            query = f"SELECT * FROM {self._table_name} WHERE user_id = %s ORDER BY created_at DESC"
            results = self.postgres_manager.execute_query(query, (user_id,))

            effort_reports = [self._row_to_effort_report(row) for row in results]

            self.logger.debug(f"✅ 努力レポート一覧DB取得完了: {len(effort_reports)}件")
            return effort_reports

        except Exception as e:
            self.logger.error(f"❌ 努力レポート一覧DB取得エラー: {e}")
            raise Exception(f"Failed to get effort reports from database: {str(e)}")

    def get_user_report(self, user_id: str, report_id: str) -> EffortReportRecord | None:
        """ユーザー権限付きで特定レポート取得

        Args:
            user_id: ユーザーID（権限チェック用）
            report_id: 努力レポートID

        Returns:
            EffortReportRecord | None: 努力レポート（存在しない/権限なしの場合はNone）
        """
        try:
            self.logger.debug(f"🔍 努力レポートDB取得: user_id={user_id}, report_id={report_id}")

            query = f"SELECT * FROM {self._table_name} WHERE report_id = %s AND user_id = %s"
            results = self.postgres_manager.execute_query(query, (report_id, user_id))

            if not results:
                return None

            return self._row_to_effort_report(results[0])

        except Exception as e:
            self.logger.error(f"❌ 努力レポートDB取得エラー: {e}")
            raise Exception(f"Failed to get user effort report from database: {str(e)}")

    def update(self, effort_report: EffortReportRecord) -> EffortReportRecord:
        """努力レポート更新

        Args:
            effort_report: 更新する努力レポートエンティティ

        Returns:
            EffortReportRecord: 更新された努力レポート

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            self.logger.info(f"📝 PostgreSQL努力レポートDB更新: {effort_report.report_id}")

            # 更新時刻をセット
            effort_report.updated_at = datetime.now().isoformat()

            query = f"""
            UPDATE {self._table_name} SET
                period_days = %s, effort_count = %s, score = %s,
                highlights = %s, categories = %s, summary = %s, achievements = %s,
                updated_at = %s
            WHERE report_id = %s
            """

            values = (
                effort_report.period_days,
                effort_report.effort_count,
                effort_report.score,
                json.dumps(effort_report.highlights, ensure_ascii=False),
                json.dumps(effort_report.categories, ensure_ascii=False),
                effort_report.summary,
                json.dumps(effort_report.achievements, ensure_ascii=False),
                effort_report.updated_at,
                effort_report.report_id,
            )

            affected_rows = self.postgres_manager.execute_update(query, values)

            if affected_rows == 0:
                raise Exception(f"Effort report not found for update: {effort_report.report_id}")

            self.logger.info(f"✅ PostgreSQL努力レポートDB更新完了: {effort_report.report_id}")
            return effort_report

        except Exception as e:
            self.logger.error(f"❌ 努力レポートDB更新エラー: {e}")
            raise Exception(f"Failed to update effort report in database: {str(e)}")

    def delete(self, report_id: str) -> bool:
        """努力レポート削除

        Args:
            report_id: 努力レポートID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            self.logger.info(f"🗑️ PostgreSQL努力レポートDB削除: {report_id}")

            query = f"DELETE FROM {self._table_name} WHERE report_id = %s"
            affected_rows = self.postgres_manager.execute_update(query, (report_id,))

            success = affected_rows > 0
            if success:
                self.logger.info(f"✅ PostgreSQL努力レポートDB削除完了: {report_id}")
            else:
                self.logger.warning(f"⚠️ 削除対象の努力レポートが見つかりません: {report_id}")

            return success

        except Exception as e:
            self.logger.error(f"❌ 努力レポートDB削除エラー: {e}")
            raise Exception(f"Failed to delete effort report from database: {str(e)}")

    def delete_user_report(self, user_id: str, report_id: str) -> EffortReportRecord | None:
        """ユーザー権限付きで努力レポート削除

        Args:
            user_id: ユーザーID（権限チェック用）
            report_id: 努力レポートID

        Returns:
            EffortReportRecord | None: 削除されたレポート（存在しない/権限なしの場合はNone）
        """
        try:
            self.logger.info(f"🗑️ 努力レポートDB削除: user_id={user_id}, report_id={report_id}")

            # 削除前に取得して権限確認
            report_to_delete = self.get_user_report(user_id, report_id)
            if not report_to_delete:
                self.logger.warning(f"⚠️ 削除権限なし/見つかりません: user_id={user_id}, report_id={report_id}")
                return None

            # 削除実行
            query = f"DELETE FROM {self._table_name} WHERE report_id = %s AND user_id = %s"
            affected_rows = self.postgres_manager.execute_update(query, (report_id, user_id))

            if affected_rows > 0:
                self.logger.info(f"✅ PostgreSQL努力レポートDB削除完了: {report_id}")
                return report_to_delete
            else:
                self.logger.warning(f"⚠️ 削除対象の努力レポートが見つかりません: {report_id}")
                return None

        except Exception as e:
            self.logger.error(f"❌ 努力レポートDB削除エラー: {e}")
            raise Exception(f"Failed to delete user effort report from database: {str(e)}")

    def get_all_reports(self, limit: int = 100, offset: int = 0) -> list[EffortReportRecord]:
        """全努力レポート取得（管理用）

        Args:
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[EffortReportRecord]: 努力レポート一覧
        """
        try:
            self.logger.debug(f"🔍 全努力レポートDB取得: limit={limit}, offset={offset}")

            query = f"""
            SELECT * FROM {self._table_name}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """

            results = self.postgres_manager.execute_query(query, (limit, offset))

            effort_reports = [self._row_to_effort_report(row) for row in results]

            self.logger.debug(f"✅ 全努力レポートDB取得完了: {len(effort_reports)}件")
            return effort_reports

        except Exception as e:
            self.logger.error(f"❌ 全努力レポートDB取得エラー: {e}")
            raise Exception(f"Failed to get all effort reports from database: {str(e)}")

    def count_reports(self) -> int:
        """努力レポート件数取得

        Returns:
            int: 総件数
        """
        try:
            query = f"SELECT COUNT(*) FROM {self._table_name}"
            results = self.postgres_manager.execute_query(query)
            return results[0]["count"] if results else 0

        except Exception as e:
            self.logger.error(f"❌ 努力レポートDB件数取得エラー: {e}")
            raise Exception(f"Failed to count effort reports in database: {str(e)}")

    def count_user_reports(self, user_id: str) -> int:
        """ユーザー別努力レポート件数取得

        Args:
            user_id: ユーザーID

        Returns:
            int: ユーザーのレポート件数
        """
        try:
            query = f"SELECT COUNT(*) FROM {self._table_name} WHERE user_id = %s"
            results = self.postgres_manager.execute_query(query, (user_id,))
            return results[0]["count"] if results else 0

        except Exception as e:
            self.logger.error(f"❌ ユーザー努力レポートDB件数取得エラー: {e}")
            raise Exception(f"Failed to count user effort reports in database: {str(e)}")

    def _row_to_effort_report(self, row: dict[str, Any]) -> EffortReportRecord:
        """データベース行をEffortReportRecordエンティティに変換

        Args:
            row: データベース行データ（辞書形式）

        Returns:
            EffortReportRecord: 努力レポートエンティティ
        """
        try:
            highlights = json.loads(row["highlights"]) if row["highlights"] else []
            categories = json.loads(row["categories"]) if row["categories"] else {}
            achievements = json.loads(row["achievements"]) if row["achievements"] else []

            return EffortReportRecord(
                report_id=row["report_id"],
                user_id=row["user_id"],
                period_days=row["period_days"],
                effort_count=row["effort_count"],
                score=row["score"],
                highlights=highlights,
                categories=categories,
                summary=row["summary"],
                achievements=achievements,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        except Exception as e:
            self.logger.error(f"❌ データベース行変換エラー: {e}")
            raise Exception(f"Failed to convert database row to EffortReportRecord: {str(e)}")

    def initialize_table(self) -> None:
        """テーブル初期化（開発・テスト用）"""
        try:
            self.logger.info(f"🐘 PostgreSQL努力レポートテーブル初期化: {self._table_name}")

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                report_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                period_days INTEGER NOT NULL DEFAULT 7,
                effort_count INTEGER NOT NULL DEFAULT 0,
                score REAL NOT NULL DEFAULT 0.0,
                highlights TEXT,
                categories TEXT,
                summary TEXT NOT NULL DEFAULT '',
                achievements TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """

            self.postgres_manager.execute_update(create_table_query)

            # インデックス作成
            index_queries = [
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_user_id ON {self._table_name}(user_id)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_created_at ON {self._table_name}(created_at)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_score ON {self._table_name}(score)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_period_days ON {self._table_name}(period_days)",
            ]

            for index_query in index_queries:
                self.postgres_manager.execute_update(index_query)

            self.logger.info(f"✅ PostgreSQL努力レポートテーブル初期化完了: {self._table_name}")

        except Exception as e:
            self.logger.error(f"❌ 努力レポートテーブル初期化エラー: {e}")
            raise Exception(f"Failed to initialize effort report table: {str(e)}")
