#!/usr/bin/env python3
"""家族情報データ移行スクリプト（JSON → SQLite）

Usage:
    python migrate_family_data.py
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import get_settings
from src.di_provider.composition_root import CompositionRootFactory
from src.infrastructure.database.family_data_migrator import FamilyDataMigrator
from src.share.logger import setup_logger


async def main():
    """家族情報データ移行メイン処理"""
    logger = setup_logger(name="family_migration", env="development")

    try:
        logger.info("🚀 家族情報データ移行スクリプト開始")

        # 設定とComposition Root初期化
        settings = get_settings()
        composition_root = CompositionRootFactory.create(settings=settings, logger=logger)

        # SQLiteマネージャー取得
        sqlite_manager = composition_root._infrastructure.get_required("sqlite_manager")

        # データ移行ツール初期化
        migrator = FamilyDataMigrator(
            settings=settings,
            sqlite_manager=sqlite_manager,
            logger=logger,
        )

        # 移行状態確認
        logger.info("📊 移行前状態確認...")
        status = await migrator.get_migration_status()
        logger.info(f"移行前状態: {status}")

        if not status.get("json_file_exists", False):
            logger.info("✅ JSONファイルが存在しないため、移行をスキップします")
            return

        if status.get("sqlite_record_count", 0) > 0:
            logger.warning("⚠️ SQLiteに既存データがあります。続行しますか？")
            response = input("続行する場合は 'yes' を入力してください: ")
            if response.lower() != "yes":
                logger.info("移行をキャンセルしました")
                return

        # データ移行実行
        logger.info("🔄 データ移行実行...")
        migration_result = await migrator.migrate_family_data()

        logger.info(f"📈 移行結果: {migration_result}")

        if migration_result.get("success", False):
            logger.info("✅ 家族情報データ移行完了")

            # 移行後状態確認
            final_status = await migrator.get_migration_status()
            logger.info(f"移行後状態: {final_status}")

        else:
            logger.error("❌ 家族情報データ移行に失敗しました")
            logger.error(f"エラー: {migration_result.get('error', 'Unknown error')}")

            # ロールバック提案
            response = input("ロールバックを実行しますか？ ('yes' で実行): ")
            if response.lower() == "yes":
                rollback_result = await migrator.rollback_migration()
                logger.info(f"ロールバック結果: {rollback_result}")

    except Exception as e:
        logger.error(f"❌ 移行スクリプト実行エラー: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
