#!/usr/bin/env python3
"""Cloud SQL CRUD操作テストスクリプト

ローカルホストアプリケーションがCloud SQLで編集・削除操作を
正常に実行できるかテストします。
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.settings import AppSettings
from src.infrastructure.database.postgres_manager import PostgreSQLManager
from src.infrastructure.secrets.secret_manager import SecretManagerService
from src.share.logger import setup_logger


def test_crud_operations():
    """CRUD操作テスト実行"""
    logger = setup_logger("crud_test", env="development")

    try:
        logger.info("🚀 Cloud SQL CRUD操作テスト開始")

        # 設定初期化
        settings = AppSettings(
            DATABASE_TYPE="postgresql",
            CLOUD_SQL_CONNECTION_NAME="blog-sample-381923:us-central1:genieus-postgres-mini",
            POSTGRES_USER="genieus_user",
            POSTGRES_DB="genieus_db",
            GOOGLE_CLOUD_PROJECT="blog-sample-381923",
            APP_NAME="GenieUs",
            ENVIRONMENT="development",
        )

        logger.info(f"📋 データベースタイプ: {settings.DATABASE_TYPE}")
        logger.info(f"📋 接続先: {settings.CLOUD_SQL_CONNECTION_NAME}")

        # Secret Manager + PostgreSQL初期化
        secret_manager = SecretManagerService(settings=settings, logger=logger)
        postgres_manager = PostgreSQLManager(settings=settings, logger=logger, secret_manager=secret_manager)

        # 1. 初期データ確認
        logger.info("🔍 初期データ確認中...")
        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                logger.info(f"✅ 既存ユーザー数: {user_count}")

                cursor.execute("SELECT user_id, name FROM users LIMIT 3")
                users = cursor.fetchall()
                logger.info(f"📋 既存ユーザー: {users}")
            finally:
                cursor.close()

        # 2. 新規データ作成（CREATE）
        logger.info("🔍 新規データ作成テスト実行中...")
        test_user_id = "crud_test_user"

        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                # ユーザー作成
                cursor.execute(
                    """INSERT INTO users (user_id, email, name, picture_url, provider) 
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (user_id) DO UPDATE SET 
                           name = EXCLUDED.name,
                           updated_at = CURRENT_TIMESTAMP""",
                    (test_user_id, "crud@test.com", "CRUDテストユーザー", "https://via.placeholder.com/150", "test"),
                )
                logger.info("✅ CREATE: テストユーザー作成成功")

                # 家族データ作成
                cursor.execute(
                    """INSERT INTO family (user_id, family_name, family_data) 
                       VALUES (%s, %s, %s)
                       ON CONFLICT DO NOTHING""",
                    (test_user_id, "CRUDテスト家族", '{"children": [{"name": "テスト太郎", "age": 5}], "test": true}'),
                )
                logger.info("✅ CREATE: 家族データ作成成功")
            finally:
                cursor.close()

        # 3. データ読み取り（READ）
        logger.info("🔍 データ読み取りテスト実行中...")
        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT user_id, name, email FROM users WHERE user_id = %s", (test_user_id,))
                user = cursor.fetchone()
                if user:
                    logger.info(f"✅ READ: ユーザーデータ読み取り成功: {user}")
                else:
                    logger.error("❌ READ: ユーザーデータが見つかりません")
                    return False

                cursor.execute("SELECT family_name, family_data FROM family WHERE user_id = %s", (test_user_id,))
                family = cursor.fetchone()
                if family:
                    logger.info(f"✅ READ: 家族データ読み取り成功: {family}")
                else:
                    logger.error("❌ READ: 家族データが見つかりません")
                    return False
            finally:
                cursor.close()

        # 4. データ更新（UPDATE）
        logger.info("🔍 データ更新テスト実行中...")
        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                # ユーザー名更新
                cursor.execute(
                    "UPDATE users SET name = %s WHERE user_id = %s", ("CRUDテストユーザー（更新済み）", test_user_id)
                )
                updated_rows = cursor.rowcount
                logger.info(f"✅ UPDATE: ユーザー更新成功 ({updated_rows}行)")

                # 家族データ更新
                cursor.execute(
                    "UPDATE family SET family_data = %s WHERE user_id = %s",
                    ('{"children": [{"name": "テスト太郎", "age": 6, "updated": true}], "test": true}', test_user_id),
                )
                updated_rows = cursor.rowcount
                logger.info(f"✅ UPDATE: 家族データ更新成功 ({updated_rows}行)")
            finally:
                cursor.close()

        # 5. 更新確認
        logger.info("🔍 更新データ確認中...")
        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT name FROM users WHERE user_id = %s", (test_user_id,))
                updated_name = cursor.fetchone()[0]
                logger.info(f"✅ 更新確認: ユーザー名 = {updated_name}")

                cursor.execute("SELECT family_data FROM family WHERE user_id = %s", (test_user_id,))
                updated_family = cursor.fetchone()[0]
                logger.info(f"✅ 更新確認: 家族データ = {updated_family}")
            finally:
                cursor.close()

        # 6. データ削除（DELETE）
        logger.info("🔍 データ削除テスト実行中...")
        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                # 家族データ削除（外部キー制約のため先に削除）
                cursor.execute("DELETE FROM family WHERE user_id = %s", (test_user_id,))
                deleted_families = cursor.rowcount
                logger.info(f"✅ DELETE: 家族データ削除成功 ({deleted_families}行)")

                # ユーザーデータ削除
                cursor.execute("DELETE FROM users WHERE user_id = %s", (test_user_id,))
                deleted_users = cursor.rowcount
                logger.info(f"✅ DELETE: ユーザーデータ削除成功 ({deleted_users}行)")
            finally:
                cursor.close()

        # 7. 削除確認
        logger.info("🔍 削除確認中...")
        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = %s", (test_user_id,))
                remaining_users = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM family WHERE user_id = %s", (test_user_id,))
                remaining_families = cursor.fetchone()[0]

                if remaining_users == 0 and remaining_families == 0:
                    logger.info("✅ DELETE確認: テストデータ完全削除成功")
                else:
                    logger.error(
                        f"❌ DELETE確認: データが残っています (ユーザー: {remaining_users}, 家族: {remaining_families})"
                    )
                    return False
            finally:
                cursor.close()

        # 8. 最終統計
        logger.info("📊 最終統計表示")
        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                final_user_count = cursor.fetchone()[0]
                logger.info(f"📊 最終ユーザー数: {final_user_count}")

                cursor.execute("SELECT COUNT(*) FROM family")
                final_family_count = cursor.fetchone()[0]
                logger.info(f"📊 最終家族数: {final_family_count}")
            finally:
                cursor.close()

        logger.info("🎉 Cloud SQL CRUD操作テスト完全成功！")

        # 9. CRUD操作統計
        logger.info("📋 CRUD操作統計:")
        logger.info("   - CREATE (作成): ✅")
        logger.info("   - READ (読み取り): ✅")
        logger.info("   - UPDATE (更新): ✅")
        logger.info("   - DELETE (削除): ✅")

        return True

    except Exception as e:
        logger.error(f"❌ Cloud SQL CRUD操作テストエラー: {e}")
        logger.exception("エラー詳細:")
        return False


def main():
    """メイン実行関数"""
    print("🚀 Cloud SQL CRUD操作テスト（ローカルホスト→Cloud SQL）")
    print("=" * 60)

    success = test_crud_operations()

    if success:
        print("\n✅ Cloud SQL CRUD操作テスト成功！")
        print("ローカルホストアプリケーションでCloud SQLの完全CRUD操作が可能です。")
        print("🎯 編集・削除機能が完全に動作しています！")
    else:
        print("\n❌ Cloud SQL CRUD操作テストに失敗しました。")
        print("設定とCloud SQL接続を確認してください。")


if __name__ == "__main__":
    main()
