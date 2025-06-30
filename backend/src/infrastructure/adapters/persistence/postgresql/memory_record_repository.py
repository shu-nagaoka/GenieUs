"""メモリー記録リポジトリ（PostgreSQL実装）

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

from src.application.interface.protocols.memory_record_repository import MemoryRecordRepositoryProtocol
from src.domain.entities import MemoryRecord
from src.infrastructure.database.postgres_manager import PostgreSQLManager


class MemoryRecordRepository(MemoryRecordRepositoryProtocol):
    """PostgreSQLメモリー記録リポジトリ

    責務:
    - メモリー記録の永続化（PostgreSQL）
    - ユーザー別のメモリー管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, postgres_manager: PostgreSQLManager, logger: logging.Logger):
        """MemoryRecordRepository初期化

        Args:
            postgres_manager: PostgreSQLマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.postgres_manager = postgres_manager
        self.logger = logger
        self._table_name = "memory_records"

    def save_memory_record(self, memory_record: MemoryRecord) -> dict:
        """メモリー記録保存

        Args:
            memory_record: メモリー記録エンティティ

        Returns:
            dict: 保存結果

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            self.logger.info(
                f"🗄️ PostgreSQLメモリー記録保存: user_id={memory_record.user_id}, title={memory_record.title}"
            )

            # 現在時刻をセット
            now = datetime.now()
            if not memory_record.created_at:
                memory_record.created_at = now.isoformat()
            memory_record.updated_at = now.isoformat()

            query = f"""
            INSERT INTO {self._table_name} (
                id, user_id, child_id, title, description, date, 
                tags, media_paths, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                date = EXCLUDED.date,
                tags = EXCLUDED.tags,
                media_paths = EXCLUDED.media_paths,
                updated_at = EXCLUDED.updated_at
            """

            # メモリー記録エンティティからPostgreSQLスキーマに変換
            media_paths = []
            if memory_record.media_url:
                media_paths.append(memory_record.media_url)
            if memory_record.thumbnail_url and memory_record.thumbnail_url not in media_paths:
                media_paths.append(memory_record.thumbnail_url)

            values = (
                memory_record.memory_id,
                memory_record.user_id,
                "frontend_user_child_0",  # child_id（デフォルト値）
                memory_record.title,
                memory_record.description,
                memory_record.date or datetime.now().date().isoformat(),
                json.dumps(memory_record.tags or [], ensure_ascii=False),
                json.dumps(media_paths, ensure_ascii=False),
                memory_record.created_at,
                memory_record.updated_at,
            )

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQLメモリー記録保存完了: {memory_record.memory_id}")
            return {"memory_id": memory_record.memory_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLメモリー記録保存エラー: {e}")
            raise Exception(f"Failed to save memory record to PostgreSQL: {str(e)}")

    def get_memory_records_by_user(self, user_id: str, limit: int = 50) -> list[dict]:
        """ユーザー別メモリー記録取得

        Args:
            user_id: ユーザーID
            limit: 取得件数上限

        Returns:
            list[dict]: メモリー記録一覧
        """
        try:
            self.logger.info(f"🔍 PostgreSQLユーザー別メモリー記録取得: user_id={user_id}")

            query = f"""
            SELECT * FROM {self._table_name}
            WHERE user_id = %s
            ORDER BY date DESC, created_at DESC
            LIMIT %s
            """

            rows = self.postgres_manager.execute_query(query, (user_id, limit))
            records = [self._row_to_dict(row) for row in rows]

            self.logger.info(f"✅ PostgreSQLユーザー別メモリー記録取得完了: {len(records)}件")
            return records

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLユーザー別メモリー記録取得エラー: {e}")
            return []

    def get_memory_record_by_id(self, memory_id: str) -> dict | None:
        """ID指定メモリー記録取得

        Args:
            memory_id: メモリー記録ID

        Returns:
            dict | None: メモリー記録（存在しない場合はNone）
        """
        try:
            query = f"SELECT * FROM {self._table_name} WHERE id = %s"
            rows = self.postgres_manager.execute_query(query, (memory_id,))

            if not rows:
                return None

            return self._row_to_dict(rows[0])

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLメモリー記録ID取得エラー: {e}")
            return None

    def delete_memory_record(self, memory_id: str) -> bool:
        """メモリー記録削除

        Args:
            memory_id: 削除する記録のID

        Returns:
            bool: 削除成功時True
        """
        try:
            self.logger.info(f"🗑️ PostgreSQLメモリー記録削除: {memory_id}")

            query = f"DELETE FROM {self._table_name} WHERE id = %s"
            self.postgres_manager.execute_update(query, (memory_id,))

            self.logger.info(f"✅ PostgreSQLメモリー記録削除完了: {memory_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLメモリー記録削除エラー: {e}")
            return False

    def _row_to_dict(self, row: dict[str, Any]) -> dict:
        """データベース行を辞書に変換

        Args:
            row: データベース行（辞書形式）

        Returns:
            dict: メモリー記録辞書
        """
        try:
            tags = json.loads(row["tags"]) if row["tags"] else []
            media_paths = json.loads(row["media_paths"]) if row["media_paths"] else []

            return {
                "memory_id": row["id"],
                "user_id": row["user_id"],
                "child_id": row["child_id"],
                "title": row["title"],
                "description": row["description"],
                "date": row["date"],
                "tags": tags,
                "media_paths": media_paths,
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
        except Exception as e:
            self.logger.error(f"❌ PostgreSQLメモリー記録行変換エラー: {e}")
            return {}
