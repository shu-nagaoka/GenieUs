"""家族情報リポジトリ（SQLite実装）

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

from src.application.interface.protocols.family_repository import FamilyRepositoryProtocol
from src.domain.entities import FamilyInfo
from src.infrastructure.database.sqlite_manager import SQLiteManager


class FamilyRepository(FamilyRepositoryProtocol):
    """SQLite家族情報リポジトリ

    責務:
    - 家族情報の永続化（SQLite）
    - ユーザー別の家族情報管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, sqlite_manager: SQLiteManager, logger: logging.Logger):
        """FamilyRepository初期化

        Args:
            sqlite_manager: SQLiteマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.sqlite_manager = sqlite_manager
        self.logger = logger
        self._table_name = "family_info"

    async def create(self, family_info: FamilyInfo) -> FamilyInfo:
        """家族情報作成

        Args:
            family_info: 家族情報エンティティ

        Returns:
            FamilyInfo: 作成された家族情報

        Raises:
            Exception: 作成に失敗した場合
        """
        try:
            self.logger.info(f"🗄️ 家族情報DB作成: {family_info.parent_name} (user_id: {family_info.user_id})")

            # 現在時刻をセット
            now = datetime.now()
            if not family_info.created_at:
                family_info.created_at = now
            family_info.updated_at = now

            query = f"""
            INSERT INTO {self._table_name} (
                family_id, user_id, parent_name, family_structure, concerns,
                living_area, children, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            values = (
                family_info.family_id,
                family_info.user_id,
                family_info.parent_name,
                family_info.family_structure,
                family_info.concerns,
                family_info.living_area,
                json.dumps(family_info.children, ensure_ascii=False),
                family_info.created_at.isoformat(),
                family_info.updated_at.isoformat(),
            )

            self.sqlite_manager.execute_update(query, values)

            self.logger.info(f"✅ 家族情報DB作成完了: {family_info.family_id}")
            return family_info

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB作成エラー: {e}")
            raise Exception(f"Failed to create family info in database: {str(e)}")

    async def get_by_id(self, family_id: str) -> FamilyInfo | None:
        """ID指定で家族情報取得

        Args:
            family_id: 家族情報ID

        Returns:
            FamilyInfo | None: 家族情報（存在しない場合はNone）
        """
        try:
            self.logger.debug(f"🔍 家族情報DB取得: {family_id}")

            query = f"SELECT * FROM {self._table_name} WHERE family_id = ?"
            results = self.sqlite_manager.execute_query(query, (family_id,))

            if not results:
                return None

            return self._row_to_family_info(results[0])

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB取得エラー: {e}")
            raise Exception(f"Failed to get family info from database: {str(e)}")

    async def get_by_user_id(self, user_id: str) -> FamilyInfo | None:
        """ユーザーID指定で家族情報取得

        Args:
            user_id: ユーザーID

        Returns:
            FamilyInfo | None: 家族情報（存在しない場合はNone）
        """
        try:
            self.logger.debug(f"🔍 家族情報DB取得: user_id={user_id}")

            query = f"SELECT * FROM {self._table_name} WHERE user_id = ?"
            results = self.sqlite_manager.execute_query(query, (user_id,))

            if not results:
                return None

            return self._row_to_family_info(results[0])

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB取得エラー: {e}")
            raise Exception(f"Failed to get family info from database: {str(e)}")

    async def update(self, family_info: FamilyInfo) -> FamilyInfo:
        """家族情報更新

        Args:
            family_info: 更新する家族情報エンティティ

        Returns:
            FamilyInfo: 更新された家族情報

        Raises:
            Exception: 更新に失敗した場合
        """
        try:
            self.logger.info(f"📝 家族情報DB更新: {family_info.family_id}")

            # 更新時刻をセット
            family_info.updated_at = datetime.now()

            query = f"""
            UPDATE {self._table_name} SET
                parent_name = ?, family_structure = ?, concerns = ?,
                living_area = ?, children = ?, updated_at = ?
            WHERE family_id = ?
            """

            values = (
                family_info.parent_name,
                family_info.family_structure,
                family_info.concerns,
                family_info.living_area,
                json.dumps(family_info.children, ensure_ascii=False),
                family_info.updated_at.isoformat(),
                family_info.family_id,
            )

            affected_rows = self.sqlite_manager.execute_update(query, values)

            if affected_rows == 0:
                raise Exception(f"Family info not found for update: {family_info.family_id}")

            self.logger.info(f"✅ 家族情報DB更新完了: {family_info.family_id}")
            return family_info

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB更新エラー: {e}")
            raise Exception(f"Failed to update family info in database: {str(e)}")

    async def delete(self, family_id: str) -> bool:
        """家族情報削除

        Args:
            family_id: 家族情報ID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            self.logger.info(f"🗑️ 家族情報DB削除: {family_id}")

            query = f"DELETE FROM {self._table_name} WHERE family_id = ?"
            affected_rows = self.sqlite_manager.execute_update(query, (family_id,))

            success = affected_rows > 0
            if success:
                self.logger.info(f"✅ 家族情報DB削除完了: {family_id}")
            else:
                self.logger.warning(f"⚠️ 削除対象の家族情報が見つかりません: {family_id}")

            return success

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB削除エラー: {e}")
            raise Exception(f"Failed to delete family info from database: {str(e)}")

    async def delete_by_user_id(self, user_id: str) -> bool:
        """ユーザーID指定で家族情報削除

        Args:
            user_id: ユーザーID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            self.logger.info(f"🗑️ 家族情報DB削除: user_id={user_id}")

            query = f"DELETE FROM {self._table_name} WHERE user_id = ?"
            affected_rows = self.sqlite_manager.execute_update(query, (user_id,))

            success = affected_rows > 0
            if success:
                self.logger.info(f"✅ 家族情報DB削除完了: user_id={user_id}")
            else:
                self.logger.warning(f"⚠️ 削除対象の家族情報が見つかりません: user_id={user_id}")

            return success

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB削除エラー: {e}")
            raise Exception(f"Failed to delete family info from database: {str(e)}")

    async def get_all_families(self, limit: int = 100, offset: int = 0) -> list[FamilyInfo]:
        """全家族情報取得（管理用）

        Args:
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[FamilyInfo]: 家族情報一覧
        """
        try:
            self.logger.debug(f"🔍 全家族情報DB取得: limit={limit}, offset={offset}")

            query = f"""
            SELECT * FROM {self._table_name}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """

            results = self.sqlite_manager.execute_query(query, (limit, offset))

            family_infos = [self._row_to_family_info(row) for row in results]

            self.logger.debug(f"✅ 全家族情報DB取得完了: {len(family_infos)}件")
            return family_infos

        except Exception as e:
            self.logger.error(f"❌ 全家族情報DB取得エラー: {e}")
            raise Exception(f"Failed to get all family info from database: {str(e)}")

    async def count_families(self) -> int:
        """家族情報件数取得

        Returns:
            int: 総件数
        """
        try:
            query = f"SELECT COUNT(*) FROM {self._table_name}"
            results = self.sqlite_manager.execute_query(query)
            return results[0]["COUNT(*)"] if results else 0

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB件数取得エラー: {e}")
            raise Exception(f"Failed to count family info in database: {str(e)}")

    def _row_to_family_info(self, row: dict[str, Any]) -> FamilyInfo:
        """データベース行をFamilyInfoエンティティに変換

        Args:
            row: データベース行データ（辞書形式）

        Returns:
            FamilyInfo: 家族情報エンティティ
        """
        try:
            children = json.loads(row["children"]) if row["children"] else []

            return FamilyInfo(
                family_id=row["family_id"],
                user_id=row["user_id"],
                parent_name=row["parent_name"],
                family_structure=row["family_structure"],
                concerns=row["concerns"],
                living_area=row["living_area"],
                children=children,
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

        except Exception as e:
            self.logger.error(f"❌ データベース行変換エラー: {e}")
            raise Exception(f"Failed to convert database row to FamilyInfo: {str(e)}")

    async def get_family_info(self, user_id: str) -> FamilyInfo | None:
        """家族情報取得（JSON Repository互換メソッド）

        Args:
            user_id: ユーザーID

        Returns:
            FamilyInfo | None: 家族情報（存在しない場合はNone）
        """
        return await self.get_by_user_id(user_id)

    async def initialize_table(self) -> None:
        """テーブル初期化（開発・テスト用）"""
        try:
            self.logger.info(f"🗄️ 家族情報テーブル初期化: {self._table_name}")

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                family_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                parent_name TEXT NOT NULL,
                family_structure TEXT,
                concerns TEXT,
                living_area TEXT,
                children TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """

            self.sqlite_manager.execute_update(create_table_query)

            # インデックス作成
            index_queries = [
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_user_id ON {self._table_name}(user_id)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_created_at ON {self._table_name}(created_at)",
                f"CREATE INDEX IF NOT EXISTS idx_{self._table_name}_living_area ON {self._table_name}(living_area)",
            ]

            for index_query in index_queries:
                self.sqlite_manager.execute_update(index_query)

            self.logger.info(f"✅ 家族情報テーブル初期化完了: {self._table_name}")

        except Exception as e:
            self.logger.error(f"❌ 家族情報テーブル初期化エラー: {e}")
            raise Exception(f"Failed to initialize family info table: {str(e)}")
