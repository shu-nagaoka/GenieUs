"""食事記録リポジトリ（SQLite実装）

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

from src.application.interface.protocols.meal_record_repository import MealRecordRepositoryProtocol
from src.domain.entities import MealRecord, MealType, FoodDetectionSource
from src.infrastructure.database.sqlite_manager import SQLiteManager


class MealRecordRepository(MealRecordRepositoryProtocol):
    """SQLite食事記録リポジトリ

    責務:
    - 食事記録の永続化（SQLite）
    - 検索・集計機能の実装
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, sqlite_manager: SQLiteManager, logger: logging.Logger):
        """MealRecordRepository初期化

        Args:
            sqlite_manager: SQLiteマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.sqlite_manager = sqlite_manager
        self.logger = logger
        self._table_name = "meal_records"

    async def create(self, meal_record: MealRecord) -> MealRecord:
        """食事記録作成

        Args:
            meal_record: 食事記録エンティティ

        Returns:
            MealRecord: 作成された食事記録

        Raises:
            Exception: 作成に失敗した場合
        """
        try:
            self.logger.info(f"🗄️ 食事記録DB作成: {meal_record.meal_name}")

            query = f"""
            INSERT INTO {self._table_name} (
                id, child_id, meal_name, meal_type, detected_foods, 
                nutrition_info, timestamp, detection_source, confidence,
                image_path, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            values = (
                meal_record.id,
                meal_record.child_id,
                meal_record.meal_name,
                meal_record.meal_type.value,
                json.dumps(meal_record.detected_foods),
                json.dumps(meal_record.nutrition_info),
                meal_record.timestamp.isoformat(),
                meal_record.detection_source.value,
                meal_record.confidence,
                meal_record.image_path,
                meal_record.notes,
                meal_record.created_at.isoformat(),
                meal_record.updated_at.isoformat(),
            )

            self.sqlite_manager.execute_update(query, values)

            self.logger.info(f"✅ 食事記録DB作成完了: {meal_record.id}")
            return meal_record

        except Exception as e:
            self.logger.error(f"❌ 食事記録DB作成エラー: {e}")
            raise Exception(f"Failed to create meal record in database: {str(e)}")

    async def get_by_id(self, meal_record_id: str) -> MealRecord | None:
        """ID指定で食事記録取得

        Args:
            meal_record_id: 食事記録ID

        Returns:
            MealRecord | None: 食事記録（存在しない場合はNone）
        """
        try:
            self.logger.debug(f"🔍 食事記録DB取得: {meal_record_id}")

            query = f"SELECT * FROM {self._table_name} WHERE id = ?"
            results = self.sqlite_manager.execute_query(query, (meal_record_id,))

            if not results:
                return None

            return self._row_to_meal_record(results[0])

        except Exception as e:
            self.logger.error(f"❌ 食事記録DB取得エラー: {e}")
            raise Exception(f"Failed to get meal record from database: {str(e)}")

    async def update(self, meal_record: MealRecord) -> MealRecord:
        """食事記録更新

        Args:
            meal_record: 更新する食事記録エンティティ

        Returns:
            MealRecord: 更新された食事記録

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            self.logger.info(f"📝 食事記録DB更新: {meal_record.id}")

            query = f"""
            UPDATE {self._table_name} SET
                meal_name = ?, meal_type = ?, detected_foods = ?,
                nutrition_info = ?, notes = ?, updated_at = ?
            WHERE id = ?
            """

            values = (
                meal_record.meal_name,
                meal_record.meal_type.value,
                json.dumps(meal_record.detected_foods),
                json.dumps(meal_record.nutrition_info),
                meal_record.notes,
                meal_record.updated_at.isoformat(),
                meal_record.id,
            )

            self.sqlite_manager.execute_update(query, values)

            self.logger.info(f"✅ 食事記録DB更新完了: {meal_record.id}")
            return meal_record

        except Exception as e:
            self.logger.error(f"❌ 食事記録DB更新エラー: {e}")
            raise Exception(f"Failed to update meal record in database: {str(e)}")

    async def delete(self, meal_record_id: str) -> bool:
        """食事記録削除

        Args:
            meal_record_id: 食事記録ID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            self.logger.info(f"🗑️ 食事記録DB削除: {meal_record_id}")

            query = f"DELETE FROM {self._table_name} WHERE id = ?"
            affected_rows = self.sqlite_manager.execute_update(query, (meal_record_id,))

            success = affected_rows > 0
            if success:
                self.logger.info(f"✅ 食事記録DB削除完了: {meal_record_id}")
            else:
                self.logger.warning(f"⚠️ 削除対象の食事記録が見つかりません: {meal_record_id}")

            return success

        except Exception as e:
            self.logger.error(f"❌ 食事記録DB削除エラー: {e}")
            raise Exception(f"Failed to delete meal record from database: {str(e)}")

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
        try:
            self.logger.debug(f"🔍 食事記録DB検索: child_id={child_id}")

            # WHERE句構築
            where_conditions = ["child_id = ?"]
            values = [child_id]

            if start_date:
                where_conditions.append("timestamp >= ?")
                values.append(start_date.isoformat())

            if end_date:
                where_conditions.append("timestamp <= ?")
                values.append(end_date.isoformat())

            if meal_type:
                where_conditions.append("meal_type = ?")
                values.append(meal_type.value)

            where_clause = " AND ".join(where_conditions)

            query = f"""
            SELECT * FROM {self._table_name}
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """

            values.extend([limit, offset])

            results = self.sqlite_manager.execute_query(query, tuple(values))

            meal_records = [self._row_to_meal_record(row) for row in results]

            self.logger.debug(f"✅ 食事記録DB検索完了: {len(meal_records)}件")
            return meal_records

        except Exception as e:
            self.logger.error(f"❌ 食事記録DB検索エラー: {e}")
            raise Exception(f"Failed to search meal records in database: {str(e)}")

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
        try:
            # WHERE句構築（searchメソッドと同じロジック）
            where_conditions = ["child_id = ?"]
            values = [child_id]

            if start_date:
                where_conditions.append("timestamp >= ?")
                values.append(start_date.isoformat())

            if end_date:
                where_conditions.append("timestamp <= ?")
                values.append(end_date.isoformat())

            if meal_type:
                where_conditions.append("meal_type = ?")
                values.append(meal_type.value)

            where_clause = " AND ".join(where_conditions)

            query = f"SELECT COUNT(*) FROM {self._table_name} WHERE {where_clause}"

            results = self.sqlite_manager.execute_query(query, tuple(values))
            return results[0]["COUNT(*)"] if results else 0

        except Exception as e:
            self.logger.error(f"❌ 食事記録DB件数取得エラー: {e}")
            raise Exception(f"Failed to count meal records in database: {str(e)}")

    async def get_by_child_id(self, child_id: str, limit: int = 50, offset: int = 0) -> list[MealRecord]:
        """子どもID指定で食事記録一覧取得

        Args:
            child_id: 子どもID
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[MealRecord]: 食事記録一覧
        """
        return await self.search(child_id=child_id, limit=limit, offset=offset)

    async def get_recent_records(self, child_id: str, days: int = 7, limit: int = 100) -> list[MealRecord]:
        """最近の食事記録取得

        Args:
            child_id: 子どもID
            days: 過去何日分を取得するか
            limit: 取得件数上限

        Returns:
            list[MealRecord]: 最近の食事記録
        """
        from datetime import timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return await self.search(child_id=child_id, start_date=start_date, end_date=end_date, limit=limit)

    def _row_to_meal_record(self, row: dict[str, Any]) -> MealRecord:
        """データベース行をMealRecordエンティティに変換

        Args:
            row: データベース行データ（辞書形式）

        Returns:
            MealRecord: 食事記録エンティティ
        """
        try:
            detected_foods = json.loads(row["detected_foods"]) if row["detected_foods"] else []
            nutrition_info = json.loads(row["nutrition_info"]) if row["nutrition_info"] else {}

            return MealRecord(
                id=row["id"],
                child_id=row["child_id"],
                meal_name=row["meal_name"],
                meal_type=MealType(row["meal_type"]),
                detected_foods=detected_foods,
                nutrition_info=nutrition_info,
                timestamp=datetime.fromisoformat(row["timestamp"]),
                detection_source=FoodDetectionSource(row["detection_source"]),
                confidence=float(row["confidence"]),
                image_path=row["image_path"],
                notes=row["notes"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

        except Exception as e:
            self.logger.error(f"❌ データベース行変換エラー: {e}")
            raise Exception(f"Failed to convert database row to MealRecord: {str(e)}")

    async def initialize_table(self) -> None:
        """テーブル初期化（開発・テスト用）"""
        try:
            self.logger.info(f"🗄️ 食事記録テーブル初期化: {self._table_name}")

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id TEXT PRIMARY KEY,
                child_id TEXT NOT NULL,
                meal_name TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                detected_foods TEXT,
                nutrition_info TEXT,
                timestamp TEXT NOT NULL,
                detection_source TEXT NOT NULL,
                confidence REAL NOT NULL,
                image_path TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """

            await self.sqlite_manager.execute(create_table_query)

            # インデックス作成
            index_queries = [
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_child_id ON {self._table_name}(child_id)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_timestamp ON {self._table_name}(timestamp)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_meal_type ON {self._table_name}(meal_type)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_child_timestamp ON {self._table_name}(child_id, timestamp)",
            ]

            for index_query in index_queries:
                await self.sqlite_manager.execute(index_query)

            self.logger.info(f"✅ 食事記録テーブル初期化完了: {self._table_name}")

        except Exception as e:
            self.logger.error(f"❌ 食事記録テーブル初期化エラー: {e}")
            raise Exception(f"Failed to initialize meal records table: {str(e)}")
