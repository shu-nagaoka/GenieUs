"""家族情報リポジトリ（PostgreSQL実装）

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
from src.infrastructure.database.postgres_manager import PostgreSQLManager


class FamilyRepository(FamilyRepositoryProtocol):
    """PostgreSQL家族情報リポジトリ

    責務:
    - 家族情報の永続化（PostgreSQL）
    - ユーザー別の家族情報管理
    - データベース操作の詳細を隠蔽
    """

    def __init__(self, postgres_manager: PostgreSQLManager, logger: logging.Logger):
        """FamilyRepository初期化

        Args:
            postgres_manager: PostgreSQLマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.postgres_manager = postgres_manager
        self.logger = logger
        self._table_name = "family_info"

    def create(self, family_info: FamilyInfo) -> FamilyInfo:
        """家族情報作成

        Args:
            family_info: 家族情報エンティティ

        Returns:
            FamilyInfo: 作成された家族情報

        Raises:
            Exception: 作成に失敗した場合
        """
        try:
            self.logger.info(f"🐘 PostgreSQL家族情報DB作成: {family_info.parent_name} (user_id: {family_info.user_id})")

            # 現在時刻をセット
            now = datetime.now()
            if not family_info.created_at:
                family_info.created_at = now
            family_info.updated_at = now

            query = f"""
            INSERT INTO {self._table_name} (
                family_id, user_id, parent_name, family_structure, concerns,
                living_area, children, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQL家族情報DB作成完了: {family_info.family_id}")
            return family_info

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL家族情報DB作成エラー: {e}")
            raise Exception(f"Failed to create family info in PostgreSQL database: {str(e)}")

    def get_by_id(self, family_id: str) -> FamilyInfo | None:
        """ID指定で家族情報取得

        Args:
            family_id: 家族情報ID

        Returns:
            FamilyInfo | None: 家族情報（存在しない場合はNone）
        """
        try:
            self.logger.debug(f"🔍 PostgreSQL家族情報DB取得: {family_id}")

            query = f"SELECT * FROM {self._table_name} WHERE family_id = %s"
            rows = self.postgres_manager.execute_query(query, (family_id,))

            if not rows:
                self.logger.debug(f"❌ 家族情報が見つかりません: {family_id}")
                return None

            row = rows[0]
            family_info = self._row_to_family_info(row)

            self.logger.debug(f"✅ 家族情報DB取得完了: {family_id}")
            return family_info

        except Exception as e:
            self.logger.error(f"❌ 家族情報DB取得エラー: {e}")
            raise Exception(f"Failed to get family info from PostgreSQL database: {str(e)}")

    def get_by_user_id(self, user_id: str) -> FamilyInfo | None:
        """ユーザーID指定で家族情報取得

        Args:
            user_id: ユーザーID

        Returns:
            FamilyInfo | None: 家族情報（存在しない場合はNone）
        """
        try:
            self.logger.debug(f"🔍 PostgreSQLユーザー別家族情報DB取得: {user_id}")

            query = f"SELECT * FROM {self._table_name} WHERE user_id = %s ORDER BY created_at DESC LIMIT 1"
            rows = self.postgres_manager.execute_query(query, (user_id,))

            if not rows:
                self.logger.debug(f"❌ ユーザーの家族情報が見つかりません: {user_id}")
                return None

            row = rows[0]
            family_info = self._row_to_family_info(row)

            self.logger.debug(f"✅ PostgreSQLユーザー別家族情報DB取得完了: {user_id}")
            return family_info

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLユーザー別家族情報DB取得エラー: {e}")
            raise Exception(f"Failed to get family info by user_id from PostgreSQL database: {str(e)}")

    def update(self, family_info: FamilyInfo) -> FamilyInfo:
        """家族情報更新

        Args:
            family_info: 更新する家族情報エンティティ

        Returns:
            FamilyInfo: 更新された家族情報
        """
        try:
            self.logger.info(f"🔄 PostgreSQL家族情報DB更新: {family_info.family_id}")

            # 更新時刻をセット
            family_info.updated_at = datetime.now()

            query = f"""
            UPDATE {self._table_name} SET
                parent_name = %s, family_structure = %s, concerns = %s,
                living_area = %s, children = %s, updated_at = %s
            WHERE family_id = %s
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

            self.postgres_manager.execute_update(query, values)

            self.logger.info(f"✅ PostgreSQL家族情報DB更新完了: {family_info.family_id}")
            return family_info

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL家族情報DB更新エラー: {e}")
            raise Exception(f"Failed to update family info in PostgreSQL database: {str(e)}")

    def delete(self, family_id: str) -> bool:
        """家族情報削除

        Args:
            family_id: 削除する家族情報ID

        Returns:
            bool: 削除成功時True、失敗時False
        """
        try:
            self.logger.info(f"🗑️ PostgreSQL家族情報DB削除: {family_id}")

            query = f"DELETE FROM {self._table_name} WHERE family_id = %s"
            self.postgres_manager.execute_update(query, (family_id,))

            self.logger.info(f"✅ PostgreSQL家族情報DB削除完了: {family_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL家族情報DB削除エラー: {e}")
            raise Exception(f"Failed to delete family info from PostgreSQL database: {str(e)}")

    def delete_by_user_id(self, user_id: str) -> bool:
        """ユーザーID指定で家族情報削除

        Args:
            user_id: ユーザーID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            self.logger.info(f"🗑️ PostgreSQLユーザーID指定家族情報削除: {user_id}")

            query = f"DELETE FROM {self._table_name} WHERE user_id = %s"
            result = self.postgres_manager.execute_update(query, (user_id,))

            self.logger.info(f"✅ PostgreSQLユーザーID指定家族情報削除完了: {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ PostgreSQLユーザーID指定家族情報削除エラー: {e}")
            return False

    def get_all_families(self, limit: int = 100, offset: int = 0) -> list[FamilyInfo]:
        """全家族情報取得（管理用）

        Args:
            limit: 取得件数上限
            offset: オフセット

        Returns:
            list[FamilyInfo]: 家族情報一覧
        """
        try:
            self.logger.info(f"📋 PostgreSQL全家族情報取得: limit={limit}, offset={offset}")

            query = f"""
            SELECT * FROM {self._table_name}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """

            rows = self.postgres_manager.execute_query(query, (limit, offset))
            families = [self._row_to_family_info(row) for row in rows]

            self.logger.info(f"✅ PostgreSQL全家族情報取得完了: {len(families)}件")
            return families

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL全家族情報取得エラー: {e}")
            return []

    def count_families(self) -> int:
        """家族情報件数取得

        Returns:
            int: 総件数
        """
        try:
            self.logger.info("🔢 PostgreSQL家族情報件数取得")

            query = f"SELECT COUNT(*) as count FROM {self._table_name}"
            rows = self.postgres_manager.execute_query(query)

            count = rows[0]["count"] if rows else 0
            self.logger.info(f"✅ PostgreSQL家族情報総件数: {count}")
            return count

        except Exception as e:
            self.logger.error(f"❌ PostgreSQL家族情報件数取得エラー: {e}")
            return 0

    def _row_to_family_info(self, row: dict[str, Any]) -> FamilyInfo:
        """データベース行をFamilyInfoエンティティに変換

        Args:
            row: データベース行（辞書形式）

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
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            )
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL行データ変換エラー: {e}")
            raise Exception(f"Failed to convert PostgreSQL row to FamilyInfo: {str(e)}")
