#!/usr/bin/env python3
"""SQLite から PostgreSQL へのデータ移行スクリプト

既存のSQLiteデータベースからPostgreSQLデータベースへの
完全データ移行を実行します。

使用方法:
    python migrate_sqlite_to_postgresql.py

環境変数:
    DATABASE_TYPE=postgresql にセットしてから実行
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config.settings import get_settings
from src.di_provider.composition_root import CompositionRootFactory
from src.infrastructure.database.postgres_manager import PostgreSQLManager
from src.infrastructure.database.sqlite_manager import SQLiteManager
from src.share.logger import setup_logger


class SQLiteToPostgreSQLMigrator:
    """SQLiteからPostgreSQLへのデータ移行クラス"""

    def __init__(self):
        """移行ツール初期化"""
        self.logger = setup_logger("migration", env="development")

        # SQLite設定（移行元）
        self.sqlite_settings = get_settings()
        self.sqlite_settings.DATABASE_TYPE = "sqlite"
        self.sqlite_manager = SQLiteManager(settings=self.sqlite_settings, logger=self.logger)

        # PostgreSQL設定（移行先）
        self.postgres_settings = get_settings()
        self.postgres_settings.DATABASE_TYPE = "postgresql"
        self.postgres_manager = PostgreSQLManager(settings=self.postgres_settings, logger=self.logger)

    def migrate_all_data(self) -> bool:
        """全データの移行実行

        Returns:
            bool: 移行成功時True
        """
        try:
            self.logger.info("🚀 SQLite → PostgreSQL データ移行開始")

            # PostgreSQL接続テスト
            if not self.postgres_manager.test_connection():
                self.logger.error("PostgreSQL接続に失敗しました")
                return False

            # PostgreSQLスキーマ初期化
            if not self.postgres_manager.is_database_initialized():
                self.logger.info("PostgreSQLスキーマを初期化します")
                if not self.postgres_manager.initialize_database():
                    self.logger.error("PostgreSQLスキーマ初期化に失敗しました")
                    return False

            # 移行実行
            success_count = 0
            total_tables = 7

            if self._migrate_users():
                success_count += 1
            if self._migrate_family():
                success_count += 1
            if self._migrate_growth_records():
                success_count += 1
            if self._migrate_memory_records():
                success_count += 1
            if self._migrate_schedule_events():
                success_count += 1
            if self._migrate_effort_reports():
                success_count += 1
            if self._migrate_meal_records():
                success_count += 1

            self.logger.info(f"✅ データ移行完了: {success_count}/{total_tables}テーブル成功")
            return success_count == total_tables

        except Exception as e:
            self.logger.error(f"❌ データ移行エラー: {e}")
            return False

    def _migrate_users(self) -> bool:
        """ユーザーデータ移行"""
        try:
            self.logger.info("👤 ユーザーデータ移行開始")

            # SQLiteからデータ取得
            sqlite_data = self._get_sqlite_data("users")
            if not sqlite_data:
                self.logger.info("ユーザーデータが存在しません")
                return True

            # PostgreSQLへデータ挿入
            for user in sqlite_data:
                postgres_query = """
                INSERT INTO users (user_id, email, name, picture_url, provider, provider_id, 
                                 is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    email = EXCLUDED.email,
                    name = EXCLUDED.name,
                    picture_url = EXCLUDED.picture_url,
                    updated_at = EXCLUDED.updated_at
                """

                params = (
                    user.get("google_id", f"migrated_{user['id']}"),  # user_id
                    user["email"],
                    user["name"],
                    user.get("picture_url"),
                    "google",  # provider
                    user.get("google_id"),  # provider_id
                    True,  # is_active
                    user.get("created_at", datetime.now().isoformat()),
                    user.get("updated_at", datetime.now().isoformat()),
                )

                with self.postgres_manager.get_raw_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(postgres_query, params)

            self.logger.info(f"✅ ユーザーデータ移行完了: {len(sqlite_data)}件")
            return True

        except Exception as e:
            self.logger.error(f"❌ ユーザーデータ移行エラー: {e}")
            return False

    def _migrate_family(self) -> bool:
        """家族データ移行"""
        try:
            self.logger.info("👨‍👩‍👧‍👦 家族データ移行開始")

            # SQLiteからデータ取得
            sqlite_data = self._get_sqlite_data("family")
            if not sqlite_data:
                self.logger.info("家族データが存在しません")
                return True

            # PostgreSQLへデータ挿入
            for family in sqlite_data:
                postgres_query = """
                INSERT INTO family (user_id, family_name, family_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """

                # family_dataをJSONBに変換
                family_data = family.get("family_data", "{}")
                if isinstance(family_data, str):
                    try:
                        family_data = json.loads(family_data)
                    except json.JSONDecodeError:
                        family_data = {}

                params = (
                    family.get("user_id", "demo_user_001"),
                    family.get("family_name", "Unknown Family"),
                    json.dumps(family_data),
                    family.get("created_at", datetime.now().isoformat()),
                    family.get("updated_at", datetime.now().isoformat()),
                )

                with self.postgres_manager.get_raw_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(postgres_query, params)

            self.logger.info(f"✅ 家族データ移行完了: {len(sqlite_data)}件")
            return True

        except Exception as e:
            self.logger.error(f"❌ 家族データ移行エラー: {e}")
            return False

    def _migrate_growth_records(self) -> bool:
        """成長記録データ移行"""
        try:
            self.logger.info("📈 成長記録データ移行開始")

            sqlite_data = self._get_sqlite_data("growth_records")
            if not sqlite_data:
                self.logger.info("成長記録データが存在しません")
                return True

            for record in sqlite_data:
                postgres_query = """
                INSERT INTO growth_records (user_id, child_name, record_date, height_cm, 
                                          weight_kg, notes, record_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                record_data = record.get("record_data", "{}")
                if isinstance(record_data, str):
                    try:
                        record_data = json.loads(record_data)
                    except json.JSONDecodeError:
                        record_data = {}

                params = (
                    record.get("user_id", "demo_user_001"),
                    record.get("child_name", "Unknown Child"),
                    record.get("record_date", datetime.now().date()),
                    record.get("height_cm"),
                    record.get("weight_kg"),
                    record.get("notes"),
                    json.dumps(record_data),
                    record.get("created_at", datetime.now().isoformat()),
                    record.get("updated_at", datetime.now().isoformat()),
                )

                with self.postgres_manager.get_raw_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(postgres_query, params)

            self.logger.info(f"✅ 成長記録データ移行完了: {len(sqlite_data)}件")
            return True

        except Exception as e:
            self.logger.error(f"❌ 成長記録データ移行エラー: {e}")
            return False

    def _migrate_memory_records(self) -> bool:
        """思い出記録データ移行"""
        try:
            self.logger.info("💕 思い出記録データ移行開始")

            sqlite_data = self._get_sqlite_data("memory_records")
            if not sqlite_data:
                self.logger.info("思い出記録データが存在しません")
                return True

            for record in sqlite_data:
                postgres_query = """
                INSERT INTO memory_records (user_id, child_name, memory_date, memory_title, 
                                          memory_content, image_url, memory_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                memory_data = record.get("memory_data", "{}")
                if isinstance(memory_data, str):
                    try:
                        memory_data = json.loads(memory_data)
                    except json.JSONDecodeError:
                        memory_data = {}

                params = (
                    record.get("user_id", "demo_user_001"),
                    record.get("child_name", "Unknown Child"),
                    record.get("memory_date", datetime.now().date()),
                    record.get("memory_title", "Untitled Memory"),
                    record.get("memory_content"),
                    record.get("image_url"),
                    json.dumps(memory_data),
                    record.get("created_at", datetime.now().isoformat()),
                    record.get("updated_at", datetime.now().isoformat()),
                )

                with self.postgres_manager.get_raw_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(postgres_query, params)

            self.logger.info(f"✅ 思い出記録データ移行完了: {len(sqlite_data)}件")
            return True

        except Exception as e:
            self.logger.error(f"❌ 思い出記録データ移行エラー: {e}")
            return False

    def _migrate_schedule_events(self) -> bool:
        """スケジュールイベントデータ移行"""
        try:
            self.logger.info("📅 スケジュールイベントデータ移行開始")

            sqlite_data = self._get_sqlite_data("schedule_events")
            if not sqlite_data:
                self.logger.info("スケジュールイベントデータが存在しません")
                return True

            for event in sqlite_data:
                postgres_query = """
                INSERT INTO schedule_events (user_id, event_title, event_date, event_time, 
                                           event_description, event_type, child_name, event_data, 
                                           created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                event_data = event.get("event_data", "{}")
                if isinstance(event_data, str):
                    try:
                        event_data = json.loads(event_data)
                    except json.JSONDecodeError:
                        event_data = {}

                params = (
                    event.get("user_id", "demo_user_001"),
                    event.get("event_title", "Untitled Event"),
                    event.get("event_date", datetime.now().date()),
                    event.get("event_time"),
                    event.get("event_description"),
                    event.get("event_type", "general"),
                    event.get("child_name"),
                    json.dumps(event_data),
                    event.get("created_at", datetime.now().isoformat()),
                    event.get("updated_at", datetime.now().isoformat()),
                )

                with self.postgres_manager.get_raw_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(postgres_query, params)

            self.logger.info(f"✅ スケジュールイベントデータ移行完了: {len(sqlite_data)}件")
            return True

        except Exception as e:
            self.logger.error(f"❌ スケジュールイベントデータ移行エラー: {e}")
            return False

    def _migrate_effort_reports(self) -> bool:
        """努力レポートデータ移行"""
        try:
            self.logger.info("💪 努力レポートデータ移行開始")

            sqlite_data = self._get_sqlite_data("effort_reports")
            if not sqlite_data:
                self.logger.info("努力レポートデータが存在しません")
                return True

            for report in sqlite_data:
                postgres_query = """
                INSERT INTO effort_reports (user_id, child_name, report_date, effort_category, 
                                          effort_description, effort_level, report_data, 
                                          created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                report_data = report.get("report_data", "{}")
                if isinstance(report_data, str):
                    try:
                        report_data = json.loads(report_data)
                    except json.JSONDecodeError:
                        report_data = {}

                params = (
                    report.get("user_id", "demo_user_001"),
                    report.get("child_name", "Unknown Child"),
                    report.get("report_date", datetime.now().date()),
                    report.get("effort_category", "general"),
                    report.get("effort_description", "No description"),
                    report.get("effort_level", 3),
                    json.dumps(report_data),
                    report.get("created_at", datetime.now().isoformat()),
                    report.get("updated_at", datetime.now().isoformat()),
                )

                with self.postgres_manager.get_raw_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(postgres_query, params)

            self.logger.info(f"✅ 努力レポートデータ移行完了: {len(sqlite_data)}件")
            return True

        except Exception as e:
            self.logger.error(f"❌ 努力レポートデータ移行エラー: {e}")
            return False

    def _migrate_meal_records(self) -> bool:
        """食事記録データ移行"""
        try:
            self.logger.info("🍽️ 食事記録データ移行開始")

            sqlite_data = self._get_sqlite_data("meal_records")
            if not sqlite_data:
                self.logger.info("食事記録データが存在しません")
                return True

            for meal in sqlite_data:
                postgres_query = """
                INSERT INTO meal_records (user_id, child_name, meal_date, meal_type, 
                                        meal_description, image_url, analysis_result, 
                                        meal_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                meal_data = meal.get("meal_data", "{}")
                if isinstance(meal_data, str):
                    try:
                        meal_data = json.loads(meal_data)
                    except json.JSONDecodeError:
                        meal_data = {}

                analysis_result = meal.get("analysis_result", "{}")
                if isinstance(analysis_result, str):
                    try:
                        analysis_result = json.loads(analysis_result)
                    except json.JSONDecodeError:
                        analysis_result = {}

                params = (
                    meal.get("user_id", "demo_user_001"),
                    meal.get("child_name", "Unknown Child"),
                    meal.get("meal_date", datetime.now().date()),
                    meal.get("meal_type", "lunch"),
                    meal.get("meal_description", "No description"),
                    meal.get("image_url"),
                    json.dumps(analysis_result),
                    json.dumps(meal_data),
                    meal.get("created_at", datetime.now().isoformat()),
                    meal.get("updated_at", datetime.now().isoformat()),
                )

                with self.postgres_manager.get_raw_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(postgres_query, params)

            self.logger.info(f"✅ 食事記録データ移行完了: {len(sqlite_data)}件")
            return True

        except Exception as e:
            self.logger.error(f"❌ 食事記録データ移行エラー: {e}")
            return False

    def _get_sqlite_data(self, table_name: str) -> list[dict[str, Any]]:
        """SQLiteからテーブルデータ取得

        Args:
            table_name: テーブル名

        Returns:
            list[dict]: テーブルデータ
        """
        try:
            with self.sqlite_manager.get_connection() as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()

                # sqlite3.Rowを辞書に変換
                return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                self.logger.warning(f"テーブル {table_name} が存在しません")
                return []
            else:
                raise
        except Exception as e:
            self.logger.error(f"SQLiteデータ取得エラー ({table_name}): {e}")
            return []


def main():
    """メイン実行関数"""
    print("🚀 SQLite → PostgreSQL データ移行ツール")
    print("=" * 50)

    migrator = SQLiteToPostgreSQLMigrator()

    # 確認プロンプト
    confirm = input("データ移行を実行しますか？ (y/N): ")
    if confirm.lower() != "y":
        print("移行をキャンセルしました。")
        return

    # 移行実行
    success = migrator.migrate_all_data()

    if success:
        print("\n✅ データ移行が正常に完了しました！")
        print("PostgreSQLデータベースが使用可能です。")
    else:
        print("\n❌ データ移行中にエラーが発生しました。")
        print("ログを確認してください。")


if __name__ == "__main__":
    main()
