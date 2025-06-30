#!/usr/bin/env python3
"""スケジュールSQLite統合テスト"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.settings import AppSettings
from src.infrastructure.adapters.persistence.schedule_record_repository_sqlite import ScheduleRecordRepository
from src.infrastructure.database.sqlite_manager import SQLiteManager
from src.share.logger import setup_logger


async def test_schedule_sqlite():
    """スケジュールSQLite統合テスト"""

    # ロガー設定
    logger = setup_logger("schedule_test")

    try:
        print("🧪 スケジュールSQLite統合テスト開始")

        # 設定とSQLiteマネージャー初期化
        settings = AppSettings()
        sqlite_manager = SQLiteManager(settings=settings, logger=logger)

        # リポジトリ初期化
        repository = ScheduleRecordRepository(sqlite_manager=sqlite_manager, logger=logger)

        # 全ユーザーのスケジュール取得テスト
        print("📋 全スケジュール取得テスト")
        all_schedules = await repository.search(
            user_id="frontend_user",  # 実際のユーザーIDを使用
            limit=100,
        )
        print(f"取得件数: {len(all_schedules)}")

        for schedule in all_schedules:
            print(f"  - {schedule.title} ({schedule.date} {schedule.time})")

        # 特定IDでの取得テスト
        if all_schedules:
            test_id = all_schedules[0].event_id
            print(f"\n🔍 個別取得テスト: {test_id}")
            individual_schedule = await repository.get_by_id(test_id)

            if individual_schedule:
                print(f"取得成功: {individual_schedule.title}")
                print(f"詳細: {individual_schedule.to_dict()}")
            else:
                print("取得失敗")

        # 今後の予定取得テスト
        print(f"\n📅 今後の予定取得テスト")
        upcoming = await repository.get_upcoming_events("frontend_user", days=30)
        print(f"今後の予定件数: {len(upcoming)}")

        for event in upcoming:
            print(f"  - {event.title} ({event.date})")

        print("\n✅ テスト完了")

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        logger.error(f"テストエラー: {e}")


if __name__ == "__main__":
    asyncio.run(test_schedule_sqlite())
