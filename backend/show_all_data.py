#!/usr/bin/env python3
"""Cloud SQL全データ表示スクリプト"""

import os
import sys
from pathlib import Path
import json

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.settings import AppSettings
from src.infrastructure.database.postgres_manager import PostgreSQLManager
from src.infrastructure.secrets.secret_manager import SecretManagerService


def show_all_data():
    """Cloud SQL全データ表示"""

    settings = AppSettings(
        DATABASE_TYPE="postgresql",
        CLOUD_SQL_CONNECTION_NAME="blog-sample-381923:us-central1:genieus-postgres-mini",
        POSTGRES_USER="genieus_user",
        POSTGRES_DB="genieus_db",
        GOOGLE_CLOUD_PROJECT="blog-sample-381923",
    )

    # ログ抑制
    import logging

    logging.getLogger().setLevel(logging.ERROR)

    secret_manager = SecretManagerService(settings=settings, logger=logging.getLogger())
    postgres_manager = PostgreSQLManager(settings=settings, logger=logging.getLogger(), secret_manager=secret_manager)

    print("🗄️ Cloud SQL全データ表示")
    print("=" * 60)

    with postgres_manager.get_raw_connection() as conn:
        cursor = conn.cursor()
        try:
            # 1. usersテーブル
            print("👥 USERS テーブル")
            print("-" * 40)
            cursor.execute(
                "SELECT user_id, email, name, provider, is_active, created_at FROM users ORDER BY created_at"
            )
            users = cursor.fetchall()

            for i, user in enumerate(users, 1):
                print(f"ユーザー {i}:")
                print(f"  user_id: {user[0]}")
                print(f"  email: {user[1]}")
                print(f"  name: {user[2]}")
                print(f"  provider: {user[3]}")
                print(f"  is_active: {user[4]}")
                print(f"  created_at: {user[5]}")
                print()

            # 2. familyテーブル
            print("👨‍👩‍👧‍👦 FAMILY テーブル")
            print("-" * 40)
            cursor.execute("SELECT user_id, family_name, family_data, created_at FROM family ORDER BY created_at")
            families = cursor.fetchall()

            for i, family in enumerate(families, 1):
                print(f"家族 {i}:")
                print(f"  user_id: {family[0]}")
                print(f"  family_name: {family[1]}")
                print(f"  family_data:")
                try:
                    family_data = family[2]
                    if isinstance(family_data, dict):
                        for key, value in family_data.items():
                            print(f"    {key}: {value}")
                    else:
                        print(f"    {family_data}")
                except:
                    print(f"    {family[2]}")
                print(f"  created_at: {family[3]}")
                print()

            # 3. 他のテーブルの件数
            print("📊 その他のテーブル")
            print("-" * 40)
            other_tables = ["growth_records", "meal_records", "schedule_events", "effort_reports", "memory_records"]

            for table in other_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count}件")

            print()

            # 統計情報
            print("📊 データベース統計")
            print("-" * 40)
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM family")
            family_count = cursor.fetchone()[0]

            total = user_count + family_count
            for table in other_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total += cursor.fetchone()[0]

            print(f"ユーザー: {user_count}件")
            print(f"家族: {family_count}件")
            print(f"その他: 0件")
            print(f"総レコード数: {total}件")

        finally:
            cursor.close()


if __name__ == "__main__":
    show_all_data()
