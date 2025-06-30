#!/usr/bin/env python3
"""スケジュールデータ移行スクリプト

JSONファイルからSQLiteデータベースへのスケジュールデータ移行を実行
"""

import asyncio
import logging
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.settings import AppSettings
from src.infrastructure.database.schedule_data_migrator import ScheduleDataMigrator
from src.infrastructure.database.sqlite_manager import SQLiteManager
from src.share.logger import setup_logger


async def main():
    """メイン実行関数"""

    # ロガー設定
    logger = setup_logger("schedule_migration")
    logger.setLevel(logging.INFO)

    try:
        print("🚀 スケジュールデータ移行開始")

        # 設定初期化
        settings = AppSettings()

        # SQLiteマネージャー初期化
        sqlite_manager = SQLiteManager(settings=settings, logger=logger)

        # マイグレーター初期化
        migrator = ScheduleDataMigrator(
            sqlite_manager=sqlite_manager, logger=logger, json_file_path="data/schedules.json"
        )

        # バックアップ作成
        print("📁 JSONファイルバックアップ作成中...")
        backup_success = await migrator.backup_json_data()
        if backup_success:
            print("✅ バックアップ作成完了")
        else:
            print("⚠️ バックアップ作成に失敗しましたが、移行を続行します")

        # データ移行実行
        print("📊 データ移行実行中...")
        migration_result = await migrator.migrate_schedule_data(force_overwrite=False)

        if migration_result["success"]:
            print(f"✅ 移行完了: {migration_result['message']}")
            print(f"   - 移行件数: {migration_result['migrated_count']}")
            print(f"   - スキップ件数: {migration_result['skipped_count']}")
            print(f"   - エラー件数: {migration_result['error_count']}")
        else:
            print(f"❌ 移行失敗: {migration_result['message']}")
            return 1

        # 整合性確認
        print("🔍 データ整合性確認中...")
        verification_result = await migrator.verify_migration()

        if verification_result["success"]:
            print("✅ 整合性確認: 問題なし")
            print(f"   - JSON件数: {verification_result['json_count']}")
            print(f"   - SQLite件数: {verification_result['sqlite_count']}")
            print(f"   - 一致件数: {verification_result['match_count']}")
        else:
            print("⚠️ 整合性確認: 不整合が検出されました")
            print(f"   - 不整合件数: {verification_result['mismatch_count']}")
            if verification_result.get("mismatch_details"):
                print("   - 不整合の詳細:")
                for detail in verification_result["mismatch_details"][:5]:
                    print(f"     {detail['event_id']}: {detail['issue']}")

        print("🎉 スケジュールデータ移行プロセス完了")
        return 0

    except Exception as e:
        logger.error(f"移行プロセスでエラーが発生しました: {e}")
        print(f"❌ エラー: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
