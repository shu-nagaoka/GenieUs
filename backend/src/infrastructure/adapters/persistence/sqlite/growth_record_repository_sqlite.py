"""成長記録リポジトリ（SQLite実装）

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
from src.infrastructure.database.sqlite_manager import SQLiteManager


class GrowthRecordRepository:
    """SQLite成長記録リポジトリ

    責務:
    - 成長記録の永続化（SQLite）
    - ユーザー別の成長記録管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, sqlite_manager: SQLiteManager, logger: logging.Logger):
        """GrowthRecordRepository初期化

        Args:
            sqlite_manager: SQLiteマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.sqlite_manager = sqlite_manager
        self.logger = logger
        self._table_name = "growth_records"

    async def save_growth_record(self, growth_record: GrowthRecord) -> dict:
        """成長記録保存

        Args:
            growth_record: 成長記録エンティティ

        Returns:
            dict: 保存結果

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            self.logger.info(f"🗄️ 成長記録DB保存: user_id={growth_record.user_id}, title={growth_record.title}")

            # 現在時刻をセット
            now = datetime.now()
            if not growth_record.created_at:
                growth_record.created_at = now.isoformat()
            growth_record.updated_at = now.isoformat()

            query = f"""
            INSERT OR REPLACE INTO {self._table_name} (
                id, user_id, child_id, record_date, height_cm, weight_kg,
                head_circumference_cm, chest_circumference_cm, milestone_description,
                notes, photo_paths, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # GrowthRecordエンティティからSQLiteスキーマに変換
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

            self.sqlite_manager.execute_update(query, values)

            self.logger.info(f"✅ 成長記録DB保存完了: {growth_record.record_id}")
            return {"record_id": growth_record.record_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"❌ 成長記録DB保存エラー: {e}")
            raise Exception(f"Failed to save growth record in database: {str(e)}")

    async def get_growth_records(self, user_id: str, filters: dict[str, Any] | None = None) -> list[GrowthRecord]:
        """成長記録一覧取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件（オプション）

        Returns:
            list[GrowthRecord]: 成長記録一覧
        """
        try:
            self.logger.debug(f"🔍 成長記録一覧DB取得: user_id={user_id}")

            query = f"SELECT * FROM {self._table_name} WHERE user_id = ? ORDER BY record_date DESC, created_at DESC"
            results = self.sqlite_manager.execute_query(query, (user_id,))

            growth_records = []
            for row in results:
                try:
                    growth_record = self._row_to_growth_record(row)

                    # フィルター適用
                    if filters:
                        if filters.get("child_name") and growth_record.child_name != filters["child_name"]:
                            continue
                        if filters.get("type") and growth_record.type != filters["type"]:
                            continue
                        if filters.get("category") and growth_record.category != filters["category"]:
                            continue

                    growth_records.append(growth_record)
                except Exception as e:
                    self.logger.warning(f"⚠️ 成長記録変換エラー (スキップ): {e}")
                    continue

            self.logger.debug(f"✅ 成長記録一覧DB取得完了: {len(growth_records)}件")
            return growth_records

        except Exception as e:
            self.logger.error(f"❌ 成長記録一覧DB取得エラー: {e}")
            return []

    async def get_growth_record(self, user_id: str, record_id: str) -> GrowthRecord | None:
        """特定成長記録取得

        Args:
            user_id: ユーザーID（権限チェック用）
            record_id: 成長記録ID

        Returns:
            GrowthRecord | None: 成長記録（存在しない/権限なしの場合はNone）
        """
        try:
            self.logger.debug(f"🔍 成長記録DB取得: user_id={user_id}, record_id={record_id}")

            query = f"SELECT * FROM {self._table_name} WHERE id = ? AND user_id = ?"
            results = self.sqlite_manager.execute_query(query, (record_id, user_id))

            if not results:
                return None

            return self._row_to_growth_record(results[0])

        except Exception as e:
            self.logger.error(f"❌ 成長記録DB取得エラー: {e}")
            return None

    async def update_growth_record(self, growth_record: GrowthRecord) -> dict:
        """成長記録更新

        Args:
            growth_record: 更新する成長記録エンティティ

        Returns:
            dict: 更新結果

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            self.logger.info(f"📝 成長記録DB更新: {growth_record.record_id}")

            # 更新時刻をセット
            growth_record.updated_at = datetime.now().isoformat()

            # まず存在チェック
            existing = await self.get_growth_record(growth_record.user_id, growth_record.record_id)
            if not existing:
                raise ValueError(f"更新対象の記録が見つかりません: {growth_record.record_id}")

            # SQLiteスキーマに合わせてデータを変換
            milestone_desc = f"[{growth_record.type}] {growth_record.title}"
            if growth_record.category:
                milestone_desc += f" ({growth_record.category})"

            notes = growth_record.description
            if growth_record.age_in_months:
                notes += f" (年齢: {growth_record.age_in_months}ヶ月)"

            photo_paths = [growth_record.image_url] if growth_record.image_url else []

            query = f"""
            UPDATE {self._table_name} SET
                child_id = ?, record_date = ?, height_cm = ?, weight_kg = ?,
                milestone_description = ?, notes = ?, photo_paths = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """

            values = (
                growth_record.child_id or "frontend_user_child_0",
                growth_record.date or datetime.now().date().isoformat(),
                growth_record.value if growth_record.unit == "cm" else None,
                growth_record.value if growth_record.unit == "kg" else None,
                milestone_desc,
                notes,
                json.dumps(photo_paths, ensure_ascii=False),
                growth_record.updated_at,
                growth_record.record_id,
                growth_record.user_id,
            )

            affected_rows = self.sqlite_manager.execute_update(query, values)

            if affected_rows == 0:
                raise Exception(f"Growth record not found for update: {growth_record.record_id}")

            self.logger.info(f"✅ 成長記録DB更新完了: {growth_record.record_id}")
            return {"record_id": growth_record.record_id, "status": "updated"}

        except Exception as e:
            self.logger.error(f"❌ 成長記録DB更新エラー: {e}")
            raise Exception(f"Failed to update growth record in database: {str(e)}")

    async def delete_growth_record(self, user_id: str, record_id: str) -> GrowthRecord | None:
        """成長記録削除

        Args:
            user_id: ユーザーID（権限チェック用）
            record_id: 成長記録ID

        Returns:
            GrowthRecord | None: 削除された記録（存在しない/権限なしの場合はNone）
        """
        try:
            self.logger.info(f"🗑️ 成長記録DB削除: user_id={user_id}, record_id={record_id}")

            # 削除前に取得して権限確認
            record_to_delete = await self.get_growth_record(user_id, record_id)
            if not record_to_delete:
                self.logger.warning(f"⚠️ 削除権限なし/見つかりません: user_id={user_id}, record_id={record_id}")
                return None

            # 削除実行
            query = f"DELETE FROM {self._table_name} WHERE id = ? AND user_id = ?"
            affected_rows = self.sqlite_manager.execute_update(query, (record_id, user_id))

            if affected_rows > 0:
                self.logger.info(f"✅ 成長記録DB削除完了: {record_id}")
                return record_to_delete
            else:
                self.logger.warning(f"⚠️ 削除対象の成長記録が見つかりません: {record_id}")
                return None

        except Exception as e:
            self.logger.error(f"❌ 成長記録DB削除エラー: {e}")
            raise Exception(f"Failed to delete growth record from database: {str(e)}")

    def _row_to_growth_record(self, row: dict[str, Any]) -> GrowthRecord:
        """データベース行をGrowthRecordエンティティに変換

        Args:
            row: データベース行データ（辞書形式）

        Returns:
            GrowthRecord: 成長記録エンティティ
        """
        try:
            # milestone_descriptionから情報を復元
            milestone_desc = row.get("milestone_description", "")
            type_info = ""
            title = ""
            category = ""

            # [type] title (category) 形式をパース
            if milestone_desc.startswith("[") and "]" in milestone_desc:
                end_bracket = milestone_desc.find("]")
                type_info = milestone_desc[1:end_bracket]
                remaining = milestone_desc[end_bracket + 1 :].strip()

                if "(" in remaining and remaining.endswith(")"):
                    paren_start = remaining.rfind("(")
                    title = remaining[:paren_start].strip()
                    category = remaining[paren_start + 1 : -1]
                else:
                    title = remaining
            else:
                title = milestone_desc

            # photo_pathsをパース
            photo_paths = []
            try:
                if row.get("photo_paths"):
                    photo_paths = json.loads(row["photo_paths"])
            except (json.JSONDecodeError, TypeError):
                photo_paths = []

            image_url = photo_paths[0] if photo_paths else None

            # notesから age_in_months を復元
            notes = row.get("notes", "")
            age_in_months = 0
            if "(年齢:" in notes:
                try:
                    start = notes.find("(年齢:") + 4
                    end = notes.find("ヶ月)", start)
                    if end > start:
                        age_str = notes[start:end].strip()
                        age_in_months = int(age_str)
                        notes = notes[: notes.find("(年齢:")].strip()
                except (ValueError, TypeError):
                    pass

            # 身長・体重からvalue/unitを復元
            value = None
            unit = None
            if row.get("height_cm"):
                value = str(row["height_cm"])
                unit = "cm"
            elif row.get("weight_kg"):
                value = str(row["weight_kg"])
                unit = "kg"

            return GrowthRecord(
                record_id=row["id"],
                user_id=row["user_id"],
                child_id=row.get("child_id"),
                child_name=row.get("child_id", ""),  # child_idをchild_nameとして使用（後で解決される）
                date=row.get("record_date", ""),
                age_in_months=age_in_months,
                type=type_info,
                category=category,
                title=title,
                description=notes,
                value=value,
                unit=unit,
                image_url=image_url,
                detected_by="parent",
                confidence=None,
                emotions=None,
                development_stage=None,
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
            )

        except Exception as e:
            self.logger.error(f"❌ データベース行変換エラー: {e}")
            raise Exception(f"Failed to convert database row to GrowthRecord: {str(e)}")

    async def initialize_table(self) -> None:
        """テーブル初期化（開発・テスト用）"""
        try:
            self.logger.info(f"🗄️ 成長記録テーブル初期化: {self._table_name}")

            # SQLiteの既存テーブル構造を利用
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                record_date TEXT NOT NULL,
                height_cm REAL,
                weight_kg REAL,
                head_circumference_cm REAL,
                chest_circumference_cm REAL,
                milestone_description TEXT,
                notes TEXT,
                photo_paths TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
            )
            """

            self.sqlite_manager.execute_update(create_table_query)

            # インデックス作成
            index_queries = [
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_user_id ON {self._table_name}(user_id)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_child_id ON {self._table_name}(child_id)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_record_date ON {self._table_name}(record_date)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_created_at ON {self._table_name}(created_at)",
            ]

            for index_query in index_queries:
                self.sqlite_manager.execute_update(index_query)

            self.logger.info(f"✅ 成長記録テーブル初期化完了: {self._table_name}")

        except Exception as e:
            self.logger.error(f"❌ 成長記録テーブル初期化エラー: {e}")
            raise Exception(f"Failed to initialize growth records table: {str(e)}")
