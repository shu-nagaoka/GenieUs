#!/usr/bin/env python3
"""Schedules データ統合スクリプト - JSON → SQLite"""

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


class SchedulesDataMigrator:
    """スケジュールデータの安全な統合"""

    def __init__(self):
        # ログ設定
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        self.logger = logging.getLogger(__name__)
        self.settings = AppSettings()
        self.sqlite_manager = SQLiteManager(self.settings, self.logger)
        self.data_dir = Path(self.settings.ROOT_DIR) / "data"

    async def migrate_schedules(self) -> dict:
        """schedules.json のデータをSQLiteに統合"""
        self.logger.info("Schedules データ統合開始")

        result = {"success": True, "migrated_count": 0, "errors": [], "skipped_count": 0, "duplicates_found": 0}

        try:
            schedules_file = self.data_dir / "schedules.json"

            if not schedules_file.exists():
                self.logger.warning(f"Schedules ファイルが見つかりません: {schedules_file}")
                return result

            # JSONファイル読み込み
            with open(schedules_file, "r", encoding="utf-8") as f:
                schedules_data = json.load(f)

            self.logger.info(f"読み込み完了: {len(schedules_data)} 件のレコード")

            # 既存のSQLiteデータを確認
            existing_records = self.sqlite_manager.execute_query("SELECT id, title, event_date FROM schedule_events")
            existing_titles_dates = {(record["title"], record["event_date"]) for record in existing_records}
            self.logger.info(f"既存SQLiteレコード: {len(existing_records)} 件")

            # 辞書形式のデータ（実際の構造に基づく）
            if isinstance(schedules_data, dict):
                for schedule_id, schedule_data in schedules_data.items():
                    try:
                        # IDでの重複チェック
                        existing_by_id = self.sqlite_manager.execute_query(
                            "SELECT id FROM schedule_events WHERE id = ?", (schedule_id,)
                        )

                        if existing_by_id:
                            self.logger.debug(f"スキップ（ID重複）: {schedule_id}")
                            result["skipped_count"] += 1
                            continue

                        # タイトル+日付での重複チェック
                        title = schedule_data.get("title", "")
                        date = schedule_data.get("date", "")

                        if (title, date) in existing_titles_dates:
                            self.logger.debug(f"スキップ（内容重複）: {title} on {date}")
                            result["duplicates_found"] += 1
                            continue

                        # SQLiteに挿入
                        await self._insert_schedule_record(schedule_id, schedule_data)
                        result["migrated_count"] += 1
                        self.logger.debug(f"移行完了: {schedule_id} - {title}")

                    except Exception as e:
                        error_msg = f"レコード移行エラー ({schedule_id}): {e}"
                        self.logger.error(error_msg)
                        result["errors"].append(error_msg)
                        result["success"] = False

            self.logger.info(
                f"Schedules 統合完了: {result['migrated_count']}件移行, {result['skipped_count']}件スキップ, {result['duplicates_found']}件重複"
            )
            return result

        except Exception as e:
            self.logger.error(f"Schedules 統合エラー: {e}")
            result["success"] = False
            result["errors"].append(str(e))
            return result

    async def _insert_schedule_record(self, schedule_id: str, schedule_data: dict) -> None:
        """スケジュール記録をSQLiteに挿入"""
        # デフォルトユーザー確保
        user_id = schedule_data.get("user_id", "frontend_user")
        await self._ensure_default_user(user_id)

        # SQLiteスキーマに合わせてデータを変換
        # JSONの構造: title, date, time, type, location, description, status など
        # SQLiteの構造: title, event_date, start_time, event_type, location など

        query = """
        INSERT OR REPLACE INTO schedule_events (
            id, user_id, child_id, title, description, event_date, 
            start_time, end_time, location, event_type, 
            reminder_minutes, is_completed, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # ステータスから完了フラグに変換
        is_completed = schedule_data.get("status", "upcoming") == "completed"

        # 型の変換
        event_type = schedule_data.get("type", "other")
        if event_type == "checkup":
            event_type = "medical"
        elif event_type == "outing":
            event_type = "outdoor"

        params = (
            schedule_id,
            user_id,
            schedule_data.get("child_id", "frontend_user_child_0"),
            schedule_data.get("title", ""),
            schedule_data.get("description", ""),
            schedule_data.get("date", datetime.now().date().isoformat()),
            schedule_data.get("time", ""),
            "",  # end_time（JSONにない）
            schedule_data.get("location", ""),
            event_type,
            None,  # reminder_minutes（JSONにない）
            is_completed,
            schedule_data.get("created_at", datetime.now().isoformat()),
            schedule_data.get("updated_at", datetime.now().isoformat()),
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
        """統合結果の検証"""
        self.logger.info("統合結果検証開始")

        try:
            # SQLiteレコード数確認
            sqlite_count = self.sqlite_manager.execute_query("SELECT COUNT(*) as count FROM schedule_events")
            sqlite_records = sqlite_count[0]["count"] if sqlite_count else 0

            # JSONレコード数確認
            schedules_file = self.data_dir / "schedules.json"
            json_records = 0
            if schedules_file.exists():
                with open(schedules_file, "r", encoding="utf-8") as f:
                    schedules_data = json.load(f)
                    json_records = len(schedules_data) if isinstance(schedules_data, dict) else 0

            # 詳細なレコード確認
            all_schedules = self.sqlite_manager.execute_query(
                "SELECT id, title, event_date, created_at FROM schedule_events ORDER BY created_at"
            )

            verification = {
                "json_records": json_records,
                "sqlite_records": sqlite_records,
                "total_expected": "6 + 新規追加分",
                "records_sample": [
                    {"id": r["id"][:8] + "...", "title": r["title"], "date": r["event_date"]}
                    for r in all_schedules[:10]  # 最初の10件のサンプル
                ],
            }

            self.logger.info(f"検証結果: JSON={json_records}件, SQLite={sqlite_records}件")
            return verification

        except Exception as e:
            self.logger.error(f"統合検証エラー: {e}")
            return {"error": str(e)}


async def main():
    """メイン実行関数"""
    print("=== Schedules データ統合ツール ===")

    migrator = SchedulesDataMigrator()

    try:
        # 1. 統合実行
        migration_result = await migrator.migrate_schedules()

        print(f"統合結果:")
        print(f"  成功: {migration_result['success']}")
        print(f"  移行件数: {migration_result['migrated_count']}")
        print(f"  スキップ件数: {migration_result['skipped_count']}")
        print(f"  重複検出: {migration_result['duplicates_found']}")

        if migration_result["errors"]:
            print(f"  エラー: {len(migration_result['errors'])}件")
            for error in migration_result["errors"]:
                print(f"    - {error}")

        # 2. 検証実行
        verification = await migrator.verify_migration()
        print(f"\n検証結果:")
        print(f"  JSON レコード数: {verification.get('json_records', 'N/A')}")
        print(f"  SQLite レコード数: {verification.get('sqlite_records', 'N/A')}")

        if verification.get("records_sample"):
            print(f"  レコードサンプル:")
            for record in verification["records_sample"]:
                print(f"    - {record['title']} ({record['date']})")

        if migration_result["success"]:
            print("\n✅ Schedules データ統合が正常に完了しました")
        else:
            print("\n❌ 統合中にエラーが発生しました")

    except Exception as e:
        print(f"❌ 統合プロセスエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
