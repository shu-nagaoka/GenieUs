"""メモリー記録リポジトリ（SQLite実装）

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

from src.domain.entities import MemoryRecord
from src.infrastructure.database.sqlite_manager import SQLiteManager


class MemoryRecordRepository:
    """SQLiteメモリー記録リポジトリ

    責務:
    - メモリー記録の永続化（SQLite）
    - ユーザー別のメモリー管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, sqlite_manager: SQLiteManager, logger: logging.Logger):
        """MemoryRecordRepository初期化

        Args:
            sqlite_manager: SQLiteマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.sqlite_manager = sqlite_manager
        self.logger = logger
        self._table_name = "memory_records"

    async def save_memory_record(self, memory_record: MemoryRecord) -> dict:
        """メモリー記録保存

        Args:
            memory_record: メモリー記録エンティティ

        Returns:
            dict: 保存結果

        Raises:
            Exception: 保存に失敗した場合
        """
        try:
            self.logger.info(f"🗄️ メモリー記録DB保存: user_id={memory_record.user_id}, title={memory_record.title}")

            # 現在時刻をセット
            now = datetime.now()
            if not memory_record.created_at:
                memory_record.created_at = now.isoformat()
            memory_record.updated_at = now.isoformat()

            query = f"""
            INSERT OR REPLACE INTO {self._table_name} (
                id, user_id, child_id, title, description, date, 
                tags, media_paths, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # メモリー記録エンティティからSQLiteスキーマに変換
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
                json.dumps(memory_record.tags, ensure_ascii=False),
                json.dumps(media_paths, ensure_ascii=False),
                memory_record.created_at,
                memory_record.updated_at,
            )

            self.sqlite_manager.execute_update(query, values)

            self.logger.info(f"✅ メモリー記録DB保存完了: {memory_record.memory_id}")
            return {"memory_id": memory_record.memory_id, "status": "saved"}

        except Exception as e:
            self.logger.error(f"❌ メモリー記録DB保存エラー: {e}")
            raise Exception(f"Failed to save memory record in database: {str(e)}")

    async def get_memory_records(self, user_id: str, filters: dict[str, Any] | None = None) -> list[MemoryRecord]:
        """メモリー記録一覧取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件（オプション）

        Returns:
            list[MemoryRecord]: メモリー記録一覧
        """
        try:
            self.logger.debug(f"🔍 メモリー記録一覧DB取得: user_id={user_id}")

            query = f"SELECT * FROM {self._table_name} WHERE user_id = ? ORDER BY date DESC, created_at DESC"
            results = self.sqlite_manager.execute_query(query, (user_id,))

            memory_records = []
            for row in results:
                try:
                    memory_record = self._row_to_memory_record(row)

                    # フィルター適用
                    if filters:
                        if filters.get("category") and memory_record.category != filters["category"]:
                            continue
                        if filters.get("type") and memory_record.type != filters["type"]:
                            continue
                        if filters.get("favorited") is not None and memory_record.favorited != filters["favorited"]:
                            continue

                    memory_records.append(memory_record)
                except Exception as e:
                    self.logger.warning(f"⚠️ メモリー記録変換エラー (スキップ): {e}")
                    continue

            self.logger.debug(f"✅ メモリー記録一覧DB取得完了: {len(memory_records)}件")
            return memory_records

        except Exception as e:
            self.logger.error(f"❌ メモリー記録一覧DB取得エラー: {e}")
            return []

    async def get_memory_record(self, user_id: str, memory_id: str) -> MemoryRecord | None:
        """特定メモリー記録取得

        Args:
            user_id: ユーザーID（権限チェック用）
            memory_id: メモリー記録ID

        Returns:
            MemoryRecord | None: メモリー記録（存在しない/権限なしの場合はNone）
        """
        try:
            self.logger.debug(f"🔍 メモリー記録DB取得: user_id={user_id}, memory_id={memory_id}")

            query = f"SELECT * FROM {self._table_name} WHERE id = ? AND user_id = ?"
            results = self.sqlite_manager.execute_query(query, (memory_id, user_id))

            if not results:
                return None

            return self._row_to_memory_record(results[0])

        except Exception as e:
            self.logger.error(f"❌ メモリー記録DB取得エラー: {e}")
            return None

    async def update_memory_record(self, memory_record: MemoryRecord) -> dict:
        """メモリー記録更新

        Args:
            memory_record: 更新するメモリー記録エンティティ

        Returns:
            dict: 更新結果

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            self.logger.info(f"📝 メモリー記録DB更新: {memory_record.memory_id}")

            # 更新時刻をセット
            memory_record.updated_at = datetime.now().isoformat()

            # まず存在チェック
            existing = await self.get_memory_record(memory_record.user_id, memory_record.memory_id)
            if not existing:
                raise ValueError(f"更新対象の記録が見つかりません: {memory_record.memory_id}")

            # SQLiteスキーマに合わせてデータを変換
            media_paths = []
            if memory_record.media_url:
                media_paths.append(memory_record.media_url)
            if memory_record.thumbnail_url and memory_record.thumbnail_url not in media_paths:
                media_paths.append(memory_record.thumbnail_url)

            query = f"""
            UPDATE {self._table_name} SET
                title = ?, description = ?, date = ?, 
                tags = ?, media_paths = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """

            values = (
                memory_record.title,
                memory_record.description,
                memory_record.date or datetime.now().date().isoformat(),
                json.dumps(memory_record.tags, ensure_ascii=False),
                json.dumps(media_paths, ensure_ascii=False),
                memory_record.updated_at,
                memory_record.memory_id,
                memory_record.user_id,
            )

            affected_rows = self.sqlite_manager.execute_update(query, values)

            if affected_rows == 0:
                raise Exception(f"Memory record not found for update: {memory_record.memory_id}")

            self.logger.info(f"✅ メモリー記録DB更新完了: {memory_record.memory_id}")
            return {"memory_id": memory_record.memory_id, "status": "updated"}

        except Exception as e:
            self.logger.error(f"❌ メモリー記録DB更新エラー: {e}")
            raise Exception(f"Failed to update memory record in database: {str(e)}")

    async def delete_memory_record(self, user_id: str, memory_id: str) -> MemoryRecord | None:
        """メモリー記録削除

        Args:
            user_id: ユーザーID（権限チェック用）
            memory_id: メモリー記録ID

        Returns:
            MemoryRecord | None: 削除された記録（存在しない/権限なしの場合はNone）
        """
        try:
            self.logger.info(f"🗑️ メモリー記録DB削除: user_id={user_id}, memory_id={memory_id}")

            # 削除前に取得して権限確認
            record_to_delete = await self.get_memory_record(user_id, memory_id)
            if not record_to_delete:
                self.logger.warning(f"⚠️ 削除権限なし/見つかりません: user_id={user_id}, memory_id={memory_id}")
                return None

            # 削除実行
            query = f"DELETE FROM {self._table_name} WHERE id = ? AND user_id = ?"
            affected_rows = self.sqlite_manager.execute_update(query, (memory_id, user_id))

            if affected_rows > 0:
                self.logger.info(f"✅ メモリー記録DB削除完了: {memory_id}")
                return record_to_delete
            else:
                self.logger.warning(f"⚠️ 削除対象のメモリー記録が見つかりません: {memory_id}")
                return None

        except Exception as e:
            self.logger.error(f"❌ メモリー記録DB削除エラー: {e}")
            raise Exception(f"Failed to delete memory record from database: {str(e)}")

    async def toggle_favorite(self, user_id: str, memory_id: str) -> bool:
        """お気に入り状態切り替え

        Args:
            user_id: ユーザーID（権限チェック用）
            memory_id: メモリー記録ID

        Returns:
            bool: 新しいお気に入り状態

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            self.logger.info(f"⭐ メモリー記録お気に入り切り替え: user_id={user_id}, memory_id={memory_id}")

            # 現在の状態を取得
            current_record = await self.get_memory_record(user_id, memory_id)
            if not current_record:
                raise ValueError(f"Memory record not found: {memory_id}")

            # お気に入り状態を切り替え
            new_favorited = not current_record.favorited

            # Note: SQLiteスキーマにfavoritedフィールドがないため、タグで管理
            tags = list(current_record.tags)
            if new_favorited:
                if "お気に入り" not in tags:
                    tags.append("お気に入り")
            else:
                if "お気に入り" in tags:
                    tags.remove("お気に入り")

            # SQLiteを更新
            query = f"""
            UPDATE {self._table_name} SET
                tags = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """

            values = (
                json.dumps(tags, ensure_ascii=False),
                datetime.now().isoformat(),
                memory_id,
                user_id,
            )

            affected_rows = self.sqlite_manager.execute_update(query, values)

            if affected_rows == 0:
                raise Exception(f"Memory record not found for favorite toggle: {memory_id}")

            self.logger.info(f"✅ メモリー記録お気に入り切り替え完了: {memory_id} -> {new_favorited}")
            return new_favorited

        except Exception as e:
            self.logger.error(f"❌ メモリー記録お気に入り切り替えエラー: {e}")
            raise Exception(f"Failed to toggle favorite for memory record in database: {str(e)}")

    async def get_favorite_memories(self, user_id: str) -> list[MemoryRecord]:
        """お気に入りメモリー一覧取得

        Args:
            user_id: ユーザーID

        Returns:
            list[MemoryRecord]: お気に入りメモリー一覧
        """
        try:
            self.logger.debug(f"🔍 お気に入りメモリーDB取得: user_id={user_id}")

            # tagsに「お気に入り」が含まれるレコードを取得
            query = f"""
            SELECT * FROM {self._table_name} 
            WHERE user_id = ? AND tags LIKE '%お気に入り%'
            ORDER BY date DESC, created_at DESC
            """
            results = self.sqlite_manager.execute_query(query, (user_id,))

            memory_records = []
            for row in results:
                try:
                    memory_record = self._row_to_memory_record(row)
                    # お気に入りフラグを確実に設定
                    memory_record.favorited = "お気に入り" in memory_record.tags
                    memory_records.append(memory_record)
                except Exception as e:
                    self.logger.warning(f"⚠️ お気に入りメモリー変換エラー (スキップ): {e}")
                    continue

            self.logger.debug(f"✅ お気に入りメモリーDB取得完了: {len(memory_records)}件")
            return memory_records

        except Exception as e:
            self.logger.error(f"❌ お気に入りメモリーDB取得エラー: {e}")
            return []

    def _row_to_memory_record(self, row: dict[str, Any]) -> MemoryRecord:
        """データベース行をMemoryRecordエンティティに変換

        Args:
            row: データベース行データ（辞書形式）

        Returns:
            MemoryRecord: メモリー記録エンティティ
        """
        try:
            # tagsをパース
            tags = []
            try:
                if row.get("tags"):
                    tags = json.loads(row["tags"])
            except (json.JSONDecodeError, TypeError):
                tags = []

            # media_pathsをパース
            media_paths = []
            try:
                if row.get("media_paths"):
                    media_paths = json.loads(row["media_paths"])
            except (json.JSONDecodeError, TypeError):
                media_paths = []

            # URLを分離
            media_url = media_paths[0] if media_paths else None
            thumbnail_url = media_paths[1] if len(media_paths) > 1 else None

            # お気に入り状態を判定
            favorited = "お気に入り" in tags

            return MemoryRecord(
                memory_id=row["id"],
                user_id=row["user_id"],
                title=row.get("title", ""),
                description=row.get("description", ""),
                date=row.get("date", ""),
                type="photo",  # SQLiteスキーマにはtype情報がない
                category="daily",  # SQLiteスキーマにはcategory情報がない
                media_url=media_url,
                thumbnail_url=thumbnail_url,
                location="",  # SQLiteスキーマにはlocation情報がない
                tags=tags,
                favorited=favorited,
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
            )

        except Exception as e:
            self.logger.error(f"❌ データベース行変換エラー: {e}")
            raise Exception(f"Failed to convert database row to MemoryRecord: {str(e)}")

    async def initialize_table(self) -> None:
        """テーブル初期化（開発・テスト用）"""
        try:
            self.logger.info(f"🗄️ メモリー記録テーブル初期化: {self._table_name}")

            # SQLiteの既存テーブル構造を利用
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                child_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                tags TEXT,
                media_paths TEXT,
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
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_date ON {self._table_name}(date)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_created_at ON {self._table_name}(created_at)",
            ]

            for index_query in index_queries:
                self.sqlite_manager.execute_update(index_query)

            self.logger.info(f"✅ メモリー記録テーブル初期化完了: {self._table_name}")

        except Exception as e:
            self.logger.error(f"❌ メモリー記録テーブル初期化エラー: {e}")
            raise Exception(f"Failed to initialize memory records table: {str(e)}")
