"""SQLiteデータベース管理クラス - Composition Root統合版"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from src.config.settings import AppSettings


class SQLiteManager:
    """SQLiteデータベース管理クラス"""

    def __init__(self, settings: AppSettings, logger: logging.Logger):
        self.settings = settings
        self.logger = logger
        self.db_path = self._parse_database_url(settings.DATABASE_URL)

        # データベースディレクトリを作成
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"SQLiteManager初期化: {self.db_path}")

    def _parse_database_url(self, database_url: str) -> Path:
        """DATABASE_URLからファイルパスを解析"""
        if database_url.startswith("sqlite:///"):
            file_path = database_url.replace("sqlite:///", "")
            # 相対パスの場合は絶対パスに変換
            if not file_path.startswith("/"):
                return Path(self.settings.ROOT_DIR) / file_path
            return Path(file_path)
        else:
            raise ValueError(f"サポートされていないDATABASE_URL: {database_url}")

    @contextmanager
    def get_connection(self):
        """データベース接続取得（コンテキストマネージャー）"""
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
            self.logger.debug(f"SQLite接続開始: {self.db_path}")
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"SQLite接続エラー: {e}")
            raise
        finally:
            if connection:
                connection.close()
                self.logger.debug("SQLite接続終了")

    def execute_query(self, query: str, params: tuple | None = None) -> list[dict[str, Any]]:
        """SELECT クエリ実行"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                results = [dict(row) for row in cursor.fetchall()]
                self.logger.debug(f"クエリ実行成功: {len(results)}件取得")
                return results
        except Exception as e:
            self.logger.error(f"クエリ実行エラー: {e}, query: {query}")
            raise

    def execute_update(self, query: str, params: tuple | None = None) -> int:
        """INSERT/UPDATE/DELETE クエリ実行"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params or ())
                affected_rows = cursor.rowcount
                conn.commit()
                self.logger.debug(f"更新クエリ実行成功: {affected_rows}行影響")
                return affected_rows
        except Exception as e:
            self.logger.error(f"更新クエリ実行エラー: {e}, query: {query}")
            raise

    def execute_batch(self, queries: list[tuple]) -> None:
        """バッチ実行（トランザクション）"""
        try:
            with self.get_connection() as conn:
                for query, params in queries:
                    conn.execute(query, params or ())
                conn.commit()
                self.logger.info(f"バッチ実行成功: {len(queries)}クエリ")
        except Exception as e:
            self.logger.error(f"バッチ実行エラー: {e}")
            raise


class DatabaseMigrator:
    """データベースマイグレーション管理"""

    def __init__(self, sqlite_manager: SQLiteManager, logger: logging.Logger):
        self.sqlite_manager = sqlite_manager
        self.logger = logger

    def initialize_database(self) -> None:
        """データベース初期化"""
        self.logger.info("データベース初期化開始")

        try:
            # マイグレーション管理テーブル作成
            self._create_migration_table()

            # 基本テーブル作成
            self._create_users_table()
            self._create_family_info_table()
            self._create_child_records_table()
            self._create_growth_records_table()
            self._create_memory_records_table()
            self._create_schedule_events_table()
            self._create_effort_reports_table()
            self._create_meal_plans_table()

            # マイグレーション記録
            self._record_migration("001_initial_schema", "基本スキーマ作成")

            self.logger.info("データベース初期化完了")

        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {e}")
            raise

    def _create_migration_table(self) -> None:
        """マイグレーション管理テーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("マイグレーション管理テーブル作成完了")

    def _create_users_table(self) -> None:
        """ユーザーテーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            google_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            picture_url TEXT,
            locale TEXT,
            verified_email BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("ユーザーテーブル作成完了")

    def _create_family_info_table(self) -> None:
        """家族情報テーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS family_info (
            family_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            parent_name TEXT NOT NULL,
            family_structure TEXT,
            concerns TEXT,
            living_area TEXT,
            children TEXT,  -- JSON形式で保存
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("家族情報テーブル作成完了")

    def _create_child_records_table(self) -> None:
        """子供記録テーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS child_records (
            id TEXT PRIMARY KEY,
            child_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            event_type TEXT NOT NULL,
            value REAL,
            unit TEXT,
            text_data TEXT,
            metadata TEXT,  -- JSON形式
            confidence REAL DEFAULT 1.0,
            source TEXT DEFAULT 'manual',
            parent_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("子供記録テーブル作成完了")

    def _create_growth_records_table(self) -> None:
        """成長記録テーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS growth_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            child_id TEXT NOT NULL,
            record_date TEXT NOT NULL,
            height_cm REAL,
            weight_kg REAL,
            head_circumference_cm REAL,
            chest_circumference_cm REAL,
            milestone_description TEXT,
            notes TEXT,
            photo_paths TEXT,  -- JSON array
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("成長記録テーブル作成完了")

    def _create_memory_records_table(self) -> None:
        """思い出記録テーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS memory_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            child_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            tags TEXT,  -- JSON array
            media_paths TEXT,  -- JSON array
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("思い出記録テーブル作成完了")

    def _create_schedule_events_table(self) -> None:
        """予定イベントテーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS schedule_events (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            child_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            event_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            location TEXT,
            event_type TEXT,
            reminder_minutes INTEGER,
            is_completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("予定イベントテーブル作成完了")

    def _create_effort_reports_table(self) -> None:
        """努力レポートテーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS effort_reports (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            daily_effort_summary TEXT,
            challenges TEXT,  -- JSON array
            achievements TEXT,  -- JSON array
            reflection TEXT,
            goals_for_tomorrow TEXT,
            mood_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("努力レポートテーブル作成完了")

    def _create_meal_plans_table(self) -> None:
        """食事プランテーブル作成"""
        query = """
        CREATE TABLE IF NOT EXISTS meal_plans (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            child_id TEXT,
            week_start TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_by TEXT DEFAULT 'user',
            meals TEXT,  -- JSON形式
            nutrition_goals TEXT,  -- JSON形式
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
        )
        """
        self.sqlite_manager.execute_update(query)
        self.logger.debug("食事プランテーブル作成完了")

    def _record_migration(self, name: str, description: str) -> None:
        """マイグレーション実行記録"""
        # 重複チェック
        existing = self.sqlite_manager.execute_query(
            "SELECT id FROM migrations WHERE name = ?",
            (name,),
        )

        if not existing:
            self.sqlite_manager.execute_update(
                "INSERT INTO migrations (name, description) VALUES (?, ?)",
                (name, description),
            )
            self.logger.info(f"マイグレーション記録: {name}")

    def check_migration_status(self) -> list[dict[str, Any]]:
        """マイグレーション状態確認"""
        try:
            return self.sqlite_manager.execute_query(
                "SELECT * FROM migrations ORDER BY executed_at DESC",
            )
        except Exception:
            # マイグレーションテーブルが存在しない場合
            return []

    def is_database_initialized(self) -> bool:
        """データベース初期化済みかチェック"""
        try:
            migrations = self.check_migration_status()
            return any(m["name"] == "001_initial_schema" for m in migrations)
        except Exception:
            return False
