#!/usr/bin/env python3
"""Growth Records データ移行スクリプト - JSON → SQLite"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

from src.config.settings import AppSettings
from src.infrastructure.database.sqlite_manager import SQLiteManager


class GrowthDataMigrator:
    """成長記録データの安全な移行"""

    def __init__(self):
        # ログ設定
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        self.logger = logging.getLogger(__name__)
        self.settings = AppSettings()
        self.sqlite_manager = SQLiteManager(self.settings, self.logger)
        self.data_dir = Path(self.settings.ROOT_DIR) / "data"

    async def migrate_growth_records(self) -> dict:
        """growth_records.json のデータをSQLiteに移行"""
        self.logger.info("Growth Records データ移行開始")

        result = {"success": True, "migrated_count": 0, "errors": [], "skipped_count": 0}

        try:
            growth_file = self.data_dir / "growth_records.json"

            if not growth_file.exists():
                self.logger.warning(f"Growth records ファイルが見つかりません: {growth_file}")
                return result

            # JSONファイル読み込み
            with open(growth_file, "r", encoding="utf-8") as f:
                growth_data = json.load(f)

            self.logger.info(f"読み込み完了: {len(growth_data)} 件のレコード")

            # 辞書形式のデータ（実際の構造に基づく）
            if isinstance(growth_data, dict):
                for record_id, record_data in growth_data.items():
                    try:
                        # 既存データチェック
                        existing = self.sqlite_manager.execute_query(
                            "SELECT id FROM growth_records WHERE id = ?", (record_id,)
                        )

                        if existing:
                            self.logger.debug(f"スキップ（既存）: {record_id}")
                            result["skipped_count"] += 1
                            continue

                        # SQLiteに挿入
                        await self._insert_growth_record(record_id, record_data)
                        result["migrated_count"] += 1
                        self.logger.debug(f"移行完了: {record_id}")

                    except Exception as e:
                        error_msg = f"レコード移行エラー ({record_id}): {e}"
                        self.logger.error(error_msg)
                        result["errors"].append(error_msg)
                        result["success"] = False

            self.logger.info(
                f"Growth Records 移行完了: {result['migrated_count']}件移行, {result['skipped_count']}件スキップ"
            )
            return result

        except Exception as e:
            self.logger.error(f"Growth Records 移行エラー: {e}")
            result["success"] = False
            result["errors"].append(str(e))
            return result

    async def _insert_growth_record(self, record_id: str, record_data: dict) -> None:
        """成長記録をSQLiteに挿入"""
        # デフォルトユーザー確保
        user_id = record_data.get("user_id", "frontend_user")
        await self._ensure_default_user(user_id)

        # SQLiteスキーマに合わせてデータを変換
        # JSONの構造: type, category, title, description, date, age_in_months など
        # SQLiteの構造: height_cm, weight_kg, milestone_description, notes など

        query = """
        INSERT OR REPLACE INTO growth_records (
            id, user_id, child_id, record_date, 
            height_cm, weight_kg, head_circumference_cm, chest_circumference_cm,
            milestone_description, notes, photo_paths, 
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # データ変換ロジック
        milestone_desc = f"[{record_data.get('type', '')}] {record_data.get('title', '')}"
        if record_data.get("category"):
            milestone_desc += f" ({record_data.get('category')})"

        notes = record_data.get("description", "")
        if record_data.get("age_in_months"):
            notes += f" (年齢: {record_data.get('age_in_months')}ヶ月)"

        params = (
            record_id,
            user_id,
            record_data.get("child_id", "frontend_user_child_0"),
            record_data.get("date", datetime.now().date().isoformat()),
            record_data.get("height_cm"),  # JSONにない場合はNone
            record_data.get("weight_kg"),  # JSONにない場合はNone
            record_data.get("head_circumference_cm"),
            record_data.get("chest_circumference_cm"),
            milestone_desc,
            notes,
            json.dumps(
                record_data.get("photo_paths", [record_data.get("image_url")]) if record_data.get("image_url") else [],
                ensure_ascii=False,
            ),
            record_data.get("created_at", datetime.now().isoformat()),
            record_data.get("updated_at", datetime.now().isoformat()),
        )

        self.sqlite_manager.execute_update(query, params)

    async def _ensure_default_user(self, user_id: str) -> None:
        """デフォルトユーザーの存在確保"""
        existing_user = self.sqlite_manager.execute_query("SELECT google_id FROM users WHERE google_id = ?", (user_id,))

        if not existing_user:
            query = """
            INSERT OR IGNORE INTO users (
                google_id, email, name, verified_email, 
                created_at, last_login, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            now = datetime.now().isoformat()
            params = (user_id, f"{user_id}@example.com", user_id.replace("_", " ").title(), False, now, now, now)

            self.sqlite_manager.execute_update(query, params)
            self.logger.debug(f"デフォルトユーザー作成: {user_id}")

    async def verify_migration(self) -> dict:
        """移行結果の検証"""
        self.logger.info("移行結果検証開始")

        try:
            # SQLiteレコード数確認
            sqlite_count = self.sqlite_manager.execute_query("SELECT COUNT(*) as count FROM growth_records")
            sqlite_records = sqlite_count[0]["count"] if sqlite_count else 0

            # JSONレコード数確認
            growth_file = self.data_dir / "growth_records.json"
            json_records = 0
            if growth_file.exists():
                with open(growth_file, "r", encoding="utf-8") as f:
                    growth_data = json.load(f)
                    json_records = len(growth_data) if isinstance(growth_data, dict) else 0

            verification = {
                "json_records": json_records,
                "sqlite_records": sqlite_records,
                "migration_complete": sqlite_records >= json_records,
            }

            self.logger.info(f"検証結果: JSON={json_records}件, SQLite={sqlite_records}件")
            return verification

        except Exception as e:
            self.logger.error(f"移行検証エラー: {e}")
            return {"error": str(e)}


async def main():
    """メイン実行関数"""
    print("=== Growth Records データ移行ツール ===")

    migrator = GrowthDataMigrator()

    try:
        # 1. 移行実行
        migration_result = await migrator.migrate_growth_records()

        print(f"移行結果:")
        print(f"  成功: {migration_result['success']}")
        print(f"  移行件数: {migration_result['migrated_count']}")
        print(f"  スキップ件数: {migration_result['skipped_count']}")

        if migration_result["errors"]:
            print(f"  エラー: {len(migration_result['errors'])}件")
            for error in migration_result["errors"]:
                print(f"    - {error}")

        # 2. 検証実行
        verification = await migrator.verify_migration()
        print(f"\n検証結果:")
        print(f"  JSON レコード数: {verification.get('json_records', 'N/A')}")
        print(f"  SQLite レコード数: {verification.get('sqlite_records', 'N/A')}")
        print(f"  移行完了: {verification.get('migration_complete', False)}")

        if migration_result["success"] and verification.get("migration_complete"):
            print("\n✅ Growth Records データ移行が正常に完了しました")
        else:
            print("\n❌ 移行中にエラーまたは不整合が発生しました")

    except Exception as e:
        print(f"❌ 移行プロセスエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
