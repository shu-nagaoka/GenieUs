"""成長記録リポジトリ（PostgreSQL実装）

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

from src.domain.entities import GrowthRecord
from src.infrastructure.database.postgres_manager import PostgreSQLManager


class GrowthRecordRepository:
    """PostgreSQL成長記録リポジトリ

    責務:
    - 成長記録の永続化（PostgreSQL）
    - ユーザー別の成長記録管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, postgres_manager: PostgreSQLManager, logger: logging.Logger):
        """GrowthRecordRepository初期化

        Args:
            postgres_manager: PostgreSQLマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.postgres_manager = postgres_manager
        self.logger = logger
        self._table_name = "growth_records"

    def save_growth_record(self, growth_record: GrowthRecord) -> dict:
        """成長記録保存

        Args:
            growth_record: 成長記録エンティティ

        Returns:
            dict: 保存結果

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            self.logger.info(f"🗄️ PostgreSQL成長記録保存: user_id={growth_record.user_id}, title={growth_record.title}")

            # 現在時刻をセット
            now = datetime.now()
            if not growth_record.created_at:
                growth_record.created_at = now.isoformat()
            growth_record.updated_at = now.isoformat()

            query = f"""
            INSERT INTO {self._table_name} (
                id, user_id, child_id, record_date, height_cm, weight_kg,
                head_circumference_cm, chest_circumference_cm, milestone_description,
                notes, photo_paths, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                height_cm = EXCLUDED.height_cm,
                weight_kg = EXCLUDED.weight_kg,
                milestone_description = EXCLUDED.milestone_description,
                notes = EXCLUDED.notes,
                photo_paths = EXCLUDED.photo_paths,
                updated_at = EXCLUDED.updated_at
            """

            # GrowthRecordエンティティからPostgreSQLスキーマに変換
            milestone_desc = f"[{growth_record.type}] {growth_record.title}"
            if growth_record.category:
                milestone_desc += f" ({growth_record.category})"

            notes = growth_record.description
            if growth_record.age_in_months:
                notes += f" (年齢: {growth_record.age_in_months}ヶ月)"

            photo_paths = [growth_record.image_url] if growth_record.image_url else []

            values = (
                growth_record.record_id,
                growth_record.user_id,
                growth_record.child_id or "frontend_user_child_0",
                growth_record.date or datetime.now().date().isoformat(),
                growth_record.value if growth_record.unit == "cm" else None,  # height_cm
                growth_record.value if growth_record.unit == "kg" else None,  # weight_kg
                None,  # head_circumference_cm
                None,  # chest_circumference_cm
                milestone_desc,
                notes,
                json.dumps(photo_paths, ensure_ascii=False),
                growth_record.created_at,
                growth_record.updated_at,
            )

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQL成長記録保存完了: {growth_record.record_id}")
            return {"record_id": growth_record.record_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL成長記録保存エラー: {e}")
            raise Exception(f"Failed to save growth record to PostgreSQL: {str(e)}")

    def get_growth_records_by_user(self, user_id: str, limit: int = 50) -> list[dict]:
        """ユーザー別成長記録取得

        Args:
            user_id: ユーザーID
            limit: 取得件数上限

        Returns:
            list[dict]: 成長記録一覧
        """
        try:
            self.logger.info(f"🔍 PostgreSQLユーザー別成長記録取得: user_id={user_id}")

            query = f"""
            SELECT * FROM {self._table_name}
            WHERE user_id = %s
            ORDER BY record_date DESC, created_at DESC
            LIMIT %s
            """

            rows = self.postgres_manager.execute_query(query, (user_id, limit))
            records = [self._row_to_dict(row) for row in rows]

            self.logger.info(f"✅ PostgreSQLユーザー別成長記録取得完了: {len(records)}件")
            return records

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLユーザー別成長記録取得エラー: {e}")
            return []

    def get_growth_record_by_id(self, record_id: str) -> dict | None:
        """ID指定成長記録取得

        Args:
            record_id: 成長記録ID

        Returns:
            dict | None: 成長記録（存在しない場合はNone）
        """
        try:
            query = f"SELECT * FROM {self._table_name} WHERE id = %s"
            rows = self.postgres_manager.execute_query(query, (record_id,))

            if not rows:
                return None

            return self._row_to_dict(rows[0])

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL成長記録ID取得エラー: {e}")
            return None

    def delete_growth_record(self, record_id: str) -> bool:
        """成長記録削除

        Args:
            record_id: 削除する記録のID

        Returns:
            bool: 削除成功時True
        """
        try:
            self.logger.info(f"🗑️ PostgreSQL成長記録削除: {record_id}")

            query = f"DELETE FROM {self._table_name} WHERE id = %s"
            self.postgres_manager.execute_update(query, (record_id,))

            self.logger.info(f"✅ PostgreSQL成長記録削除完了: {record_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL成長記録削除エラー: {e}")
            return False

    def _row_to_dict(self, row: dict[str, Any]) -> dict:
        """データベース行を辞書に変換

        Args:
            row: データベース行（辞書形式）

        Returns:
            dict: 成長記録辞書
        """
        try:
            photo_paths = json.loads(row["photo_paths"]) if row["photo_paths"] else []

            return {
                "record_id": row["id"],
                "user_id": row["user_id"],
                "child_id": row["child_id"],
                "record_date": row["record_date"],
                "height_cm": row["height_cm"],
                "weight_kg": row["weight_kg"],
                "head_circumference_cm": row["head_circumference_cm"],
                "chest_circumference_cm": row["chest_circumference_cm"],
                "milestone_description": row["milestone_description"],
                "notes": row["notes"],
                "photo_paths": photo_paths,
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL成長記録行変換エラー: {e}")
            return {}