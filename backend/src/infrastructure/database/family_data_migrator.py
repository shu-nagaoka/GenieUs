"""家族情報データ移行ツール（JSON → SQLite）

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config.settings import AppSettings
from src.domain.entities import FamilyInfo
from src.infrastructure.adapters.persistence.sqlite.family_repository_sqlite import (
    FamilyRepository as SQLiteFamilyRepository,
)
from src.infrastructure.database.sqlite_manager import SQLiteManager


class FamilyDataMigrator:
    """家族情報データ移行ツール（JSON → SQLite）

    責務:
    - 既存JSON家族情報のSQLiteマイグレーション
    - データ整合性の確保
    - バックアップとロールバック機能
    """

    def __init__(
        self,
        settings: AppSettings,
        sqlite_manager: SQLiteManager,
        logger: logging.Logger,
    ):
        """FamilyDataMigrator初期化

        Args:
            settings: アプリケーション設定
            sqlite_manager: SQLiteマネージャー
            logger: DIコンテナから注入されるロガー
        """
        self.settings = settings
        self.sqlite_manager = sqlite_manager
        self.logger = logger
        self.family_repository = SQLiteFamilyRepository(sqlite_manager=sqlite_manager, logger=logger)

        # JSON ファイルパス
        self.json_file_path = Path("data/frontend_user_family.json")
        self.backup_file_path = Path("data/frontend_user_family_backup.json")

    async def migrate_family_data(self) -> dict[str, Any]:
        """家族情報データをJSONからSQLiteに移行

        Returns:
            dict[str, Any]: 移行結果統計
        """
        try:
            self.logger.info("🚀 家族情報データ移行開始")

            # テーブル初期化
            await self.family_repository.initialize_table()

            # JSON データ読み込み
            json_data = self._load_json_data()
            if not json_data:
                return {
                    "success": True,
                    "message": "移行対象の家族情報データが見つかりません",
                    "migrated_count": 0,
                    "failed_count": 0,
                }

            # バックアップ作成
            self._create_backup(json_data)

            # 移行実行
            migration_stats = await self._migrate_data(json_data)

            # 検証
            await self._verify_migration(migration_stats["migrated_count"])

            self.logger.info(f"✅ 家族情報データ移行完了: {migration_stats}")
            return migration_stats

        except Exception as e:
            self.logger.error(f"❌ 家族情報データ移行エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "migrated_count": 0,
                "failed_count": 0,
            }

    def _load_json_data(self) -> dict[str, Any] | None:
        """JSONファイルからデータ読み込み

        Returns:
            dict[str, Any] | None: JSONデータ（存在しない場合はNone）
        """
        try:
            if not self.json_file_path.exists():
                self.logger.info(f"JSONファイルが存在しません: {self.json_file_path}")
                return None

            with open(self.json_file_path, encoding="utf-8") as f:
                data = json.load(f)

            # 単一オブジェクトの場合は辞書に変換
            if isinstance(data, dict) and "user_id" in data:
                user_id = data["user_id"]
                self.logger.info(f"📖 単一家族データを検出: user_id={user_id}")
                return {user_id: data}
            elif isinstance(data, dict):
                self.logger.info(f"📖 JSONデータ読み込み完了: {len(data)}件")
                return data
            else:
                self.logger.warning(f"⚠️ 予期しないJSONフォーマット: {type(data)}")
                return None

        except Exception as e:
            self.logger.error(f"❌ JSONデータ読み込みエラー: {e}")
            raise Exception(f"Failed to load JSON data: {str(e)}")

    def _create_backup(self, data: dict[str, Any]) -> None:
        """バックアップファイル作成

        Args:
            data: バックアップ対象データ
        """
        try:
            # 既存バックアップがあれば、タイムスタンプ付きで保存
            if self.backup_file_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archived_backup = self.backup_file_path.parent / f"frontend_user_family_backup_{timestamp}.json"
                self.backup_file_path.rename(archived_backup)
                self.logger.info(f"既存バックアップを履歴保存: {archived_backup}")

            # 新しいバックアップ作成
            with open(self.backup_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"💾 バックアップ作成完了: {self.backup_file_path}")

        except Exception as e:
            self.logger.error(f"❌ バックアップ作成エラー: {e}")
            raise Exception(f"Failed to create backup: {str(e)}")

    async def _migrate_data(self, json_data: dict[str, Any]) -> dict[str, Any]:
        """データ移行実行

        Args:
            json_data: JSONデータ

        Returns:
            dict[str, Any]: 移行統計
        """
        migrated_count = 0
        failed_count = 0
        errors = []

        self.logger.info(f"📊 移行対象: {len(json_data)}件の家族情報")

        for user_id, family_data in json_data.items():
            try:
                # FamilyInfoエンティティ作成
                family_info = self._json_to_family_info(user_id, family_data)

                # 既存データチェック（重複登録防止）
                existing_family = await self.family_repository.get_by_user_id(user_id)
                if existing_family:
                    self.logger.warning(f"⚠️ 既存家族情報をスキップ: user_id={user_id}")
                    continue

                # SQLiteに保存
                await self.family_repository.create(family_info)
                migrated_count += 1

                self.logger.debug(f"✅ 家族情報移行成功: user_id={user_id}")

            except Exception as e:
                failed_count += 1
                error_msg = f"user_id={user_id}, error={str(e)}"
                errors.append(error_msg)
                self.logger.error(f"❌ 家族情報移行失敗: {error_msg}")

        return {
            "success": failed_count == 0,
            "migrated_count": migrated_count,
            "failed_count": failed_count,
            "errors": errors,
            "message": f"家族情報移行完了: 成功{migrated_count}件, 失敗{failed_count}件",
        }

    def _json_to_family_info(self, user_id: str, family_data: dict[str, Any]) -> FamilyInfo:
        """JSONデータをFamilyInfoエンティティに変換

        Args:
            user_id: ユーザーID
            family_data: 家族情報JSONデータ

        Returns:
            FamilyInfo: 家族情報エンティティ
        """
        try:
            return FamilyInfo(
                family_id=family_data.get("family_id", ""),
                user_id=user_id,
                parent_name=family_data.get("parent_name", ""),
                family_structure=family_data.get("family_structure"),
                concerns=family_data.get("concerns"),
                living_area=family_data.get("living_area"),
                children=family_data.get("children", []),
                created_at=datetime.now(),  # 移行時の現在時刻
                updated_at=datetime.now(),
            )

        except Exception as e:
            self.logger.error(f"❌ FamilyInfo変換エラー: {e}")
            raise Exception(f"Failed to convert JSON to FamilyInfo: {str(e)}")

    async def _verify_migration(self, expected_count: int) -> None:
        """移行結果検証

        Args:
            expected_count: 期待される移行件数
        """
        try:
            # SQLiteから全家族情報を取得
            actual_count = await self.family_repository.count_families()

            self.logger.info(f"🔍 移行検証: 期待件数={expected_count}, 実際件数={actual_count}")

            if actual_count < expected_count:
                raise Exception(f"Migration verification failed: expected {expected_count}, got {actual_count}")

            self.logger.info("✅ 移行検証成功: データ整合性確認")

        except Exception as e:
            self.logger.error(f"❌ 移行検証エラー: {e}")
            raise Exception(f"Failed to verify migration: {str(e)}")

    async def rollback_migration(self) -> dict[str, Any]:
        """移行のロールバック（SQLiteデータ削除 + JSONファイル復元）

        Returns:
            dict[str, Any]: ロールバック結果
        """
        try:
            self.logger.info("🔄 家族情報データ移行ロールバック開始")

            # SQLiteから全家族情報を削除
            deleted_count = 0
            families = await self.family_repository.get_all_families(limit=1000)
            for family in families:
                success = await self.family_repository.delete(family.family_id)
                if success:
                    deleted_count += 1

            # バックアップからJSONファイル復元
            if self.backup_file_path.exists():
                self.backup_file_path.rename(self.json_file_path)
                self.logger.info(f"📄 JSONファイル復元: {self.json_file_path}")

            self.logger.info(f"✅ ロールバック完了: {deleted_count}件削除")
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": "ロールバック完了",
            }

        except Exception as e:
            self.logger.error(f"❌ ロールバックエラー: {e}")
            return {"success": False, "error": str(e)}

    async def get_migration_status(self) -> dict[str, Any]:
        """移行状態取得

        Returns:
            dict[str, Any]: 移行状態情報
        """
        try:
            json_exists = self.json_file_path.exists()
            backup_exists = self.backup_file_path.exists()
            sqlite_count = await self.family_repository.count_families()

            json_count = 0
            if json_exists:
                json_data = self._load_json_data()
                json_count = len(json_data) if json_data else 0

            return {
                "json_file_exists": json_exists,
                "json_record_count": json_count,
                "backup_file_exists": backup_exists,
                "sqlite_record_count": sqlite_count,
                "migration_needed": json_exists and sqlite_count == 0,
            }

        except Exception as e:
            self.logger.error(f"❌ 移行状態取得エラー: {e}")
            return {"error": str(e)}
