#!/usr/bin/env python3
"""Cloud SQL最小インスタンス接続テストスクリプト

Cloud SQLの最小インスタンス構成でPostgreSQL接続テストを実行
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


def test_cloud_sql_minimal():
    """Cloud SQL最小インスタンス接続テスト"""
    logger = setup_logger("cloud_sql_test", env="production")

    try:
        logger.info("🚀 Cloud SQL最小インスタンス接続テスト開始")

        # 最小インスタンス設定
        settings = AppSettings(
            DATABASE_TYPE="postgresql",
            GOOGLE_CLOUD_PROJECT="blog-sample-381923",
            # Cloud SQL最小インスタンス設定
            CLOUD_SQL_CONNECTION_NAME="blog-sample-381923:us-central1:genieus-postgres-mini",
            POSTGRES_USER="genieus_user",
            POSTGRES_PASSWORD="",  # Secret Managerから取得
            POSTGRES_DB="genieus_db",
            # 最小設定
            APP_NAME="GenieUs",
            ENVIRONMENT="production",
            PORT=8080,
            CORS_ORIGINS="*",
            JWT_SECRET="",  # Secret Managerから取得
            NEXTAUTH_SECRET="",  # Secret Managerから取得
            BUCKET_NAME="genieus-files-demo",
        )

        logger.info(f"📋 接続先: {settings.CLOUD_SQL_CONNECTION_NAME}")
        logger.info(f"📋 データベース: {settings.POSTGRES_DB}")
        logger.info(f"📋 ユーザー: {settings.POSTGRES_USER}")

        # Secret Manager初期化
        logger.info("🔐 Secret Manager初期化中...")
        secret_manager = SecretManagerService(settings=settings, logger=logger)

        # デモ用シークレット設定
        logger.info("🔐 デモ用シークレット設定中...")
        secret_setup_success = secret_manager.setup_demo_secrets()
        if not secret_setup_success:
            logger.warning("デモ用シークレット設定に一部失敗しましたが、継続します")

        # PostgreSQL接続テスト（Secret Manager統合）
        postgres_manager = PostgreSQLManager(settings=settings, logger=logger, secret_manager=secret_manager)

        # 1. 基本接続テスト
        logger.info("🔍 基本接続テスト実行中...")
        connection_success = postgres_manager.test_connection()

        if connection_success:
            logger.info("✅ Cloud SQL基本接続成功")
        else:
            logger.error("❌ Cloud SQL基本接続失敗")
            return False

        # 2. スキーマ初期化テスト
        logger.info("🔍 スキーマ初期化テスト実行中...")
        if not postgres_manager.is_database_initialized():
            logger.info("📋 スキーマ未初期化、初期化実行...")
            init_success = postgres_manager.initialize_database()
            if init_success:
                logger.info("✅ スキーマ初期化成功")
            else:
                logger.error("❌ スキーマ初期化失敗")
                return False
        else:
            logger.info("✅ スキーマ既に初期化済み")

        # 3. 基本CRUD操作テスト
        logger.info("🔍 基本CRUD操作テスト実行中...")

        # テストユーザー作成
        test_query = """
        INSERT INTO users (user_id, email, name, picture_url, provider) 
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            email = EXCLUDED.email,
            name = EXCLUDED.name,
            updated_at = CURRENT_TIMESTAMP
        """

        test_params = (
            "cloud_sql_test_user",
            "cloudsql@genieus.com",
            "Cloud SQLテストユーザー",
            "https://via.placeholder.com/150",
            "demo",
        )

        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(test_query, test_params)
                logger.info("✅ テストユーザー作成成功")
            finally:
                cursor.close()

        # テストデータ読み取り
        read_query = "SELECT user_id, email, name FROM users WHERE user_id = %s"
        read_params = ("cloud_sql_test_user",)

        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(read_query, read_params)
                result = cursor.fetchone()

                if result:
                    logger.info(f"✅ テストデータ読み取り成功: {result}")
                else:
                    logger.error("❌ テストデータ読み取り失敗")
                    return False
            finally:
                cursor.close()

        # 4. 家族データテスト
        logger.info("🔍 家族データ操作テスト実行中...")

        family_query = """
        INSERT INTO family (user_id, family_name, family_data, created_at, updated_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT DO NOTHING
        """

        family_params = (
            "cloud_sql_test_user",
            "Cloud SQLテスト家族",
            '{"children": [{"name": "テスト太郎", "age": 3}], "demo": true}',
        )

        with postgres_manager.get_raw_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(family_query, family_params)
                logger.info("✅ 家族データ作成成功")
            finally:
                cursor.close()

        # 5. 接続プール性能テスト
        logger.info("🔍 接続プール性能テスト実行中...")

        for i in range(5):
            with postgres_manager.get_raw_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    count = cursor.fetchone()[0]
                    logger.info(f"✅ 接続テスト{i + 1}: ユーザー数 {count}")
                finally:
                    cursor.close()

        logger.info("🎉 Cloud SQL最小インスタンス接続テスト完全成功！")

        # 6. 統計情報表示
        logger.info("📊 Cloud SQL接続統計:")
        logger.info("   - 基本接続: ✅")
        logger.info("   - スキーマ初期化: ✅")
        logger.info("   - CRUD操作: ✅")
        logger.info("   - JSON操作: ✅")
        logger.info("   - 接続プール: ✅")

        return True

    except Exception as e:
        logger.error(f"❌ Cloud SQL接続テストエラー: {e}")
        logger.exception("エラー詳細:")
        return False


def main():
    """メイン実行関数"""
    print("🚀 Cloud SQL最小インスタンス接続テスト（Secret Manager統合）")
    print("=" * 60)

    # Google Cloud認証確認
    print("🔐 Google Cloud認証確認中...")
    try:
        from google.auth import default

        credentials, project = default()
        print(f"✅ 認証成功: project={project}")
    except Exception as e:
        print(f"❌ Google Cloud認証エラー: {e}")
        print("以下のいずれかを実行してください:")
        print("  1. gcloud auth application-default login")
        print("  2. サービスアカウントキーの設定")
        return

    # テスト実行
    success = test_cloud_sql_minimal()

    if success:
        print("\n✅ Cloud SQL最小インスタンス接続テスト成功！")
        print("Secret Manager統合PostgreSQLが完全に動作しています。")
        print("🎯 デプロイ準備完了状態です！")
    else:
        print("\n❌ Cloud SQL接続テストに失敗しました。")
        print("設定とCloud SQLインスタンスを確認してください。")


if __name__ == "__main__":
    main()
