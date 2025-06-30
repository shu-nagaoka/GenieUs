#!/usr/bin/env python3
"""Memories データ移行スクリプト - JSON → SQLite"""

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


class MemoriesDataMigrator:
    """メモリーデータの安全な移行"""

    def __init__(self):
        # ログ設定
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        self.logger = logging.getLogger(__name__)
        self.settings = AppSettings()
        self.sqlite_manager = SQLiteManager(self.settings, self.logger)
        self.data_dir = Path(self.settings.ROOT_DIR) / "data"

    async def migrate_memories(self) -> dict:
        """memories.json のデータをSQLiteに移行"""
        self.logger.info("Memories データ移行開始")

        result = {"success": True, "migrated_count": 0, "errors": [], "skipped_count": 0}

        try:
            memories_file = self.data_dir / "memories.json"

            if not memories_file.exists():
                self.logger.warning(f"Memories ファイルが見つかりません: {memories_file}")
                return result

            # JSONファイル読み込み
            with open(memories_file, "r", encoding="utf-8") as f:
                memories_data = json.load(f)

            self.logger.info(f"読み込み完了: {len(memories_data)} 件のレコード")

            # 辞書形式のデータ（実際の構造に基づく）
            if isinstance(memories_data, dict):
                for memory_id, memory_data in memories_data.items():
                    try:
                        # 既存データチェック
                        existing = self.sqlite_manager.execute_query(
                            "SELECT id FROM memory_records WHERE id = ?", (memory_id,)
                        )

                        if existing:
                            self.logger.debug(f"スキップ（既存）: {memory_id}")
                            result["skipped_count"] += 1
                            continue

                        # SQLiteに挿入
                        await self._insert_memory_record(memory_id, memory_data)
                        result["migrated_count"] += 1
                        self.logger.debug(f"移行完了: {memory_id}")

                    except Exception as e:
                        error_msg = f"レコード移行エラー ({memory_id}): {e}"
                        self.logger.error(error_msg)
                        result["errors"].append(error_msg)
                        result["success"] = False

            self.logger.info(
                f"Memories 移行完了: {result['migrated_count']}件移行, {result['skipped_count']}件スキップ"
            )
            return result

        except Exception as e:
            self.logger.error(f"Memories 移行エラー: {e}")
            result["success"] = False
            result["errors"].append(str(e))
            return result

    async def _insert_memory_record(self, memory_id: str, memory_data: dict) -> None:
        """メモリー記録をSQLiteに挿入"""
        # デフォルトユーザー確保
        user_id = memory_data.get("user_id", "frontend_user")
        await self._ensure_default_user(user_id)

        # SQLiteスキーマに合わせてデータを変換
        # JSONの構造: title, description, date, type, category, tags, media_url など
        # SQLiteの構造: title, description, date, tags, media_paths など

        query = """
        INSERT OR REPLACE INTO memory_records (
            id, user_id, child_id, title, description, date, 
            tags, media_paths, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # tags を JSON文字列に変換
        tags_json = json.dumps(memory_data.get("tags", []), ensure_ascii=False)

        # media_paths を構築（media_url があれば配列に含める）
        media_paths = []
        if memory_data.get("media_url"):
            media_paths.append(memory_data["media_url"])
        if memory_data.get("thumbnail_url") and memory_data["thumbnail_url"] not in media_paths:
            media_paths.append(memory_data["thumbnail_url"])
        media_paths_json = json.dumps(media_paths, ensure_ascii=False)

        params = (
            memory_id,
            user_id,
            memory_data.get("child_id", "frontend_user_child_0"),
            memory_data.get("title", ""),
            memory_data.get("description", ""),
            memory_data.get("date", datetime.now().date().isoformat()),
            tags_json,
            media_paths_json,
            memory_data.get("created_at", datetime.now().isoformat()),
            memory_data.get("updated_at", datetime.now().isoformat()),
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
            sqlite_count = self.sqlite_manager.execute_query("SELECT COUNT(*) as count FROM memory_records")
            sqlite_records = sqlite_count[0]["count"] if sqlite_count else 0

            # JSONレコード数確認
            memories_file = self.data_dir / "memories.json"
            json_records = 0
            if memories_file.exists():
                with open(memories_file, "r", encoding="utf-8") as f:
                    memories_data = json.load(f)
                    json_records = len(memories_data) if isinstance(memories_data, dict) else 0

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
    print("=== Memories データ移行ツール ===")

    migrator = MemoriesDataMigrator()

    try:
        # 1. 移行実行
        migration_result = await migrator.migrate_memories()

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
            print("\n✅ Memories データ移行が正常に完了しました")
        else:
            print("\n❌ 移行中にエラーまたは不整合が発生しました")

    except Exception as e:
        print(f"❌ 移行プロセスエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
