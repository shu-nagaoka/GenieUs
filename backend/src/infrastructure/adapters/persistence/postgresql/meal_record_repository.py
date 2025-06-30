"""食事記録リポジトリ（PostgreSQL実装）

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
from src.infrastructure.database.postgres_manager import PostgreSQLManager


class MealRecordRepository(MealRecordRepositoryProtocol):
    """PostgreSQL食事記録リポジトリ

    責務:
    - 食事記録の永続化（PostgreSQL）
    - 検索・集計機能の実装
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, postgres_manager: PostgreSQLManager, logger: logging.Logger):
        """MealRecordRepository初期化

        Args:
            postgres_manager: PostgreSQLマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.postgres_manager = postgres_manager
        self.logger = logger
        self._table_name = "meal_records"

    def create(self, meal_record: MealRecord) -> MealRecord:
        """食事記録作成

        Args:
            meal_record: 食事記録エンティティ

        Returns:
            MealRecord: 作成された食事記録

        Raises:
            Exception: 作成に失敗した場合
        """
        try:
            self.logger.info(f"🍽️ PostgreSQL食事記録作成開始: user_id={meal_record.user_id}")

            query = f"""
            INSERT INTO {self._table_name} (
                id, user_id, date, meal_type, food_items,
                detection_source, image_url, notes, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                meal_record.id,
                meal_record.user_id,
                meal_record.date,
                meal_record.meal_type.value,
                json.dumps(meal_record.food_items, ensure_ascii=False),
                meal_record.detection_source.value,
                meal_record.image_url,
                meal_record.notes,
                meal_record.created_at,
                meal_record.updated_at,
            )

            self.postgres_manager.execute_update(query, params)

            self.logger.info(f"✅ PostgreSQL食事記録作成完了: id={meal_record.id}")
            return meal_record

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL食事記録作成エラー: {e}")
            raise Exception(f"Failed to create meal record in PostgreSQL: {e}")

    def get_by_id(self, record_id: str) -> MealRecord | None:
        """ID指定で食事記録取得

        Args:
            record_id: 食事記録ID

        Returns:
            MealRecord | None: 食事記録（存在しない場合はNone）
        """
        try:
            query = f"SELECT * FROM {self._table_name} WHERE id = %s"
            rows = self.postgres_manager.execute_query(query, (record_id,))

            if not rows:
                return None

            return self._row_to_meal_record(rows[0])

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL食事記録取得エラー: {e}")
            return None

    def update(self, meal_record: MealRecord) -> MealRecord:
        """食事記録更新

        Args:
            meal_record: 更新する食事記録

        Returns:
            MealRecord: 更新された食事記録

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            query = f"""
            UPDATE {self._table_name} SET
                date = %s, meal_type = %s, food_items = %s,
                detection_source = %s, image_url = %s, notes = %s, updated_at = %s
            WHERE id = %s
            """

            params = (
                meal_record.date,
                meal_record.meal_type.value,
                json.dumps(meal_record.food_items, ensure_ascii=False),
                meal_record.detection_source.value,
                meal_record.image_url,
                meal_record.notes,
                meal_record.updated_at,
                meal_record.id,
            )

            affected_rows = self.postgres_manager.execute_update(query, params)

            if affected_rows == 0:
                raise Exception("更新対象の食事記録が見つかりません")

            self.logger.info(f"✅ PostgreSQL食事記録更新完了: id={meal_record.id}")
            return meal_record

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL食事記録更新エラー: {e}")
            raise Exception(f"Failed to update meal record in PostgreSQL: {e}")

    def delete(self, record_id: str) -> bool:
        """食事記録削除

        Args:
            record_id: 削除する記録のID

        Returns:
            bool: 削除成功時True
        """
        try:
            query = f"DELETE FROM {self._table_name} WHERE id = %s"
            affected_rows = self.postgres_manager.execute_update(query, (record_id,))

            success = affected_rows > 0
            self.logger.info(f"🗑️ PostgreSQL食事記録削除: id={record_id}, success={success}")
            return success

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL食事記録削除エラー: {e}")
            return False

    def search(
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
            start_date: 開始日時
            end_date: 終了日時
            meal_type: 食事タイプ
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[MealRecord]: 検索結果の食事記録リスト
        """
        try:
            conditions = ["user_id = %s"]
            params: list[Any] = [child_id]

            if start_date:
                conditions.append("date >= %s")
                params.append(start_date)

            if end_date:
                conditions.append("date <= %s")
                params.append(end_date)

            if meal_type:
                conditions.append("meal_type = %s")
                params.append(meal_type.value)

            query = f"""
            SELECT * FROM {self._table_name}
            WHERE {" AND ".join(conditions)}
            ORDER BY date DESC, created_at DESC
            LIMIT %s OFFSET %s
            """

            params.extend([limit, offset])
            rows = self.postgres_manager.execute_query(query, params)

            return [self._row_to_meal_record(row) for row in rows]

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL食事記録検索エラー: {e}")
            return []

    def count(
        self,
        child_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        meal_type: MealType | None = None,
    ) -> int:
        """食事記録件数取得

        Args:
            child_id: 子どもID
            start_date: 開始日時
            end_date: 終了日時
            meal_type: 食事タイプ

        Returns:
            int: 条件に合致する食事記録件数
        """
        try:
            conditions = ["user_id = %s"]
            params: list[Any] = [child_id]

            if start_date:
                conditions.append("date >= %s")
                params.append(start_date)

            if end_date:
                conditions.append("date <= %s")
                params.append(end_date)

            if meal_type:
                conditions.append("meal_type = %s")
                params.append(meal_type.value)

            query = f"SELECT COUNT(*) as count FROM {self._table_name} WHERE {' AND '.join(conditions)}"
            rows = self.postgres_manager.execute_query(query, params)

            return rows[0]["count"] if rows else 0

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL食事記録件数取得エラー: {e}")
            return 0

    def get_by_child_id(self, child_id: str, limit: int = 50, offset: int = 0) -> list[MealRecord]:
        """子どもID指定で食事記録一覧取得

        Args:
            child_id: 子どもID
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[MealRecord]: 食事記録一覧
        """
        try:
            query = f"""
            SELECT * FROM {self._table_name}
            WHERE user_id = %s
            ORDER BY date DESC, created_at DESC
            LIMIT %s OFFSET %s
            """

            rows = self.postgres_manager.execute_query(query, (child_id, limit, offset))
            return [self._row_to_meal_record(row) for row in rows]

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL子どもID指定食事記録取得エラー: {e}")
            return []

    def get_recent_records(self, child_id: str, days: int = 7, limit: int = 100) -> list[MealRecord]:
        """最近の食事記録取得

        Args:
            child_id: 子どもID
            days: 過去何日分を取得するか
            limit: 取得件数上限

        Returns:
            list[MealRecord]: 最近の食事記録
        """
        try:
            query = f"""
            SELECT * FROM {self._table_name}
            WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date DESC, created_at DESC
            LIMIT %s
            """

            rows = self.postgres_manager.execute_query(query, (child_id, days, limit))
            return [self._row_to_meal_record(row) for row in rows]

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL最近の食事記録取得エラー: {e}")
            return []

    def _row_to_meal_record(self, row: dict[str, Any]) -> MealRecord:
        """データベース行を食事記録エンティティに変換

        Args:
            row: データベース行データ（辞書形式）

        Returns:
            MealRecord: 食事記録エンティティ
        """
        try:
            food_items = json.loads(row["food_items"]) if row["food_items"] else []

            return MealRecord(
                id=row["id"],
                user_id=row["user_id"],
                date=row["date"],
                meal_type=MealType(row["meal_type"]),
                food_items=food_items,
                detection_source=FoodDetectionSource(row["detection_source"]),
                image_url=row["image_url"],
                notes=row["notes"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL食事記録行変換エラー: {e}")
            # エラー時はデフォルト値でMealRecordを返す
            return MealRecord(
                id=row.get("id", ""),
                user_id=row.get("user_id", ""),
                date=row.get("date", datetime.now()),
                meal_type=MealType.BREAKFAST,
                food_items=[],
                detection_source=FoodDetectionSource.MANUAL,
                image_url=row.get("image_url"),
                notes=row.get("notes"),
                created_at=row.get("created_at", datetime.now()),
                updated_at=row.get("updated_at", datetime.now()),
            )
