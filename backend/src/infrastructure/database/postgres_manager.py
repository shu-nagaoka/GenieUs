"""PostgreSQL データベース管理クラス - Cloud SQL対応版

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import logging
import os
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator

import psycopg2
from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import AppSettings


class PostgreSQLManager:
    """Cloud SQL PostgreSQL データベース管理クラス

    Cloud SQL Connector、SQLAlchemy、psycopg2を統合した
    高性能PostgreSQL接続管理システム
    """

    def __init__(self, settings: AppSettings, logger: logging.Logger, secret_manager=None):
        """PostgreSQL管理システム初期化

        Args:
            settings: アプリケーション設定
            logger: DIコンテナから注入されるロガー
            secret_manager: Secret Managerサービス（オプション）
        """
        self.settings = settings
        self.logger = logger
        self.secret_manager = secret_manager
        self._engine: Engine | None = None
        self._session_maker: sessionmaker[Session] | None = None
        self._connector: Connector | None = None

        # Secret ManagerからPostgreSQLパスワード取得
        if self.secret_manager:
            try:
                self.postgres_password = self.secret_manager.get_postgres_password()
                self.logger.info("✅ Secret ManagerからPostgreSQLパスワード取得成功")
            except Exception as e:
                self.logger.warning(f"Secret Managerパスワード取得失敗、環境変数使用: {e}")
                self.postgres_password = settings.POSTGRES_PASSWORD
        else:
            self.postgres_password = settings.POSTGRES_PASSWORD

        # 接続設定を初期化
        self._initialize_connection_config()

        self.logger.info(f"PostgreSQLManager初期化完了: {self.settings.DATABASE_TYPE}")

    def _initialize_connection_config(self) -> None:
        """データベース接続設定の初期化"""
        try:
            if self.settings.DATABASE_TYPE == "postgresql":
                # Cloud SQL接続の場合
                if self.settings.CLOUD_SQL_CONNECTION_NAME:
                    self._setup_cloud_sql_connection()
                else:
                    # 直接PostgreSQL接続の場合
                    self._setup_direct_postgresql_connection()
            else:
                self.logger.warning("PostgreSQL以外のデータベースタイプが指定されています")

        except Exception as e:
            self.logger.error(f"PostgreSQL接続設定初期化エラー: {e}")
            raise RuntimeError(f"PostgreSQL接続設定に失敗しました: {e}") from e

    def _setup_cloud_sql_connection(self) -> None:
        """Cloud SQL Connector接続設定"""
        try:
            self.logger.info("Cloud SQL Connector接続設定を開始")

            # Cloud SQL Connectorを初期化
            self._connector = Connector()

            # Cloud SQL Connector用のカスタムcreator関数を定義
            def getconn():
                return self._connector.connect(
                    self.settings.CLOUD_SQL_CONNECTION_NAME,
                    "pg8000",
                    user=self.settings.POSTGRES_USER,
                    password=self.postgres_password,
                    db=self.settings.POSTGRES_DB,
                )

            # SQLAlchemyエンジン作成（Cloud SQL Connector使用）
            self._engine = create_engine(
                "postgresql+pg8000://",  # pg8000ドライバー使用
                creator=getconn,  # カスタム接続関数
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,  # 30分でコネクション再作成
                echo=self.settings.LOG_LEVEL == "DEBUG",
            )

            self._session_maker = sessionmaker(bind=self._engine)

            self.logger.info(f"Cloud SQL接続設定完了: {self.settings.CLOUD_SQL_CONNECTION_NAME}")

        except Exception as e:
            self.logger.error(f"Cloud SQL接続設定エラー: {e}")
            raise

    def _setup_direct_postgresql_connection(self) -> None:
        """直接PostgreSQL接続設定"""
        try:
            self.logger.info("直接PostgreSQL接続設定を開始")

            # 通常のPostgreSQL接続文字列
            connection_string = self._build_direct_connection_string()
            self._engine = create_engine(
                connection_string,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=self.settings.LOG_LEVEL == "DEBUG",
            )

            self._session_maker = sessionmaker(bind=self._engine)

            self.logger.info(f"PostgreSQL直接接続設定完了: {self.settings.POSTGRES_HOST}:{self.settings.POSTGRES_PORT}")

        except Exception as e:
            self.logger.error(f"PostgreSQL直接接続設定エラー: {e}")
            raise

    def _build_cloud_sql_connection_string(self) -> str:
        """Cloud SQL接続文字列構築"""
        # ローカル開発環境の場合はCloud SQL Connectorを使用
        return (
            f"postgresql+psycopg2://{self.settings.POSTGRES_USER}:{self.postgres_password}@/{self.settings.POSTGRES_DB}"
        )

    def _build_direct_connection_string(self) -> str:
        """直接PostgreSQL接続文字列構築"""
        return (
            f"postgresql+psycopg2://{self.settings.POSTGRES_USER}:"
            f"{self.postgres_password}@"
            f"{self.settings.POSTGRES_HOST}:{self.settings.POSTGRES_PORT}/"
            f"{self.settings.POSTGRES_DB}"
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """SQLAlchemyセッション取得（コンテキストマネージャー）

        Returns:
            Session: SQLAlchemyセッション

        Raises:
            RuntimeError: データベース接続エラー
        """
        if not self._session_maker:
            raise RuntimeError("PostgreSQL接続が初期化されていません")

        session = self._session_maker()
        try:
            self.logger.debug("PostgreSQLセッション開始")
            yield session
            session.commit()
            self.logger.debug("PostgreSQLセッション正常終了")
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"PostgreSQLセッションエラー: {e}")
            raise RuntimeError(f"データベース操作に失敗しました: {e}") from e
        except Exception as e:
            session.rollback()
            self.logger.error(f"予期しないセッションエラー: {e}")
            raise
        finally:
            session.close()

    @contextmanager
    def get_raw_connection(self) -> Generator[Any, None, None]:
        """生のpsycopg2接続取得（低レベルAPI用）

        Returns:
            psycopg2.Connection: 生のPostgreSQL接続

        Raises:
            RuntimeError: データベース接続エラー
        """
        connection = None
        try:
            if self.settings.CLOUD_SQL_CONNECTION_NAME and self._connector:
                # Cloud SQL Connector使用
                connection = self._connector.connect(
                    self.settings.CLOUD_SQL_CONNECTION_NAME,
                    "pg8000",
                    user=self.settings.POSTGRES_USER,
                    password=self.postgres_password,
                    db=self.settings.POSTGRES_DB,
                )
            else:
                # 直接接続
                connection = psycopg2.connect(
                    host=self.settings.POSTGRES_HOST,
                    port=self.settings.POSTGRES_PORT,
                    user=self.settings.POSTGRES_USER,
                    password=self.postgres_password,
                    database=self.settings.POSTGRES_DB,
                )

            connection.autocommit = False
            self.logger.debug("PostgreSQL生接続開始")
            yield connection
            connection.commit()
            self.logger.debug("PostgreSQL生接続正常終了")

        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            self.logger.error(f"PostgreSQL生接続エラー: {e}")
            raise RuntimeError(f"データベース接続に失敗しました: {e}") from e
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"予期しない接続エラー: {e}")
            raise
        finally:
            if connection:
                connection.close()

    def test_connection(self) -> bool:
        """データベース接続テスト

        Returns:
            bool: 接続成功時True
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1 as test"))
                test_value = result.scalar()

                if test_value == 1:
                    self.logger.info("PostgreSQL接続テスト成功")
                    return True
                else:
                    self.logger.error(f"PostgreSQL接続テスト失敗: 予期しない結果 {test_value}")
                    return False

        except Exception as e:
            self.logger.error(f"PostgreSQL接続テストエラー: {e}")
            return False

    def create_tables_from_sql(self, sql_file_path: str) -> bool:
        """SQLファイルからテーブル作成

        Args:
            sql_file_path: SQLファイルパス

        Returns:
            bool: 作成成功時True
        """
        try:
            with open(sql_file_path, "r", encoding="utf-8") as file:
                sql_content = file.read()

            with self.get_session() as session:
                # PostgreSQL特有の構文（トリガー関数など）を考慮した分割
                # $$ で囲まれた関数定義は分割しない
                statements = []
                current_statement = ""
                in_function = False

                for line in sql_content.split("\n"):
                    line = line.strip()
                    if not line or line.startswith("--"):
                        continue

                    current_statement += line + "\n"

                    # 関数定義の開始/終了を検出
                    if "$$" in line:
                        in_function = not in_function

                    # セミコロンで終了し、関数内でない場合は文を終了
                    if line.endswith(";") and not in_function:
                        statements.append(current_statement.strip())
                        current_statement = ""

                # 残った文があれば追加
                if current_statement.strip():
                    statements.append(current_statement.strip())

                for statement in statements:
                    if statement:
                        session.execute(text(statement))

                self.logger.info(f"SQLファイルからテーブル作成完了: {sql_file_path}")
                return True

        except Exception as e:
            self.logger.error(f"SQLファイルからのテーブル作成エラー: {e}")
            return False

    def execute_sql_file(self, sql_file_path: str) -> bool:
        """SQLファイル実行

        Args:
            sql_file_path: SQLファイルパス

        Returns:
            bool: 実行成功時True
        """
        try:
            with open(sql_file_path, "r", encoding="utf-8") as file:
                sql_content = file.read()

            with self.get_session() as session:
                session.execute(text(sql_content))

                self.logger.info(f"SQLファイル実行完了: {sql_file_path}")
                return True

        except Exception as e:
            self.logger.error(f"SQLファイル実行エラー: {e}")
            return False

    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """SQLiteManager互換のget_connectionメソッド

        既存のRepositoryクラスとの互換性確保のため、
        get_raw_connectionのエイリアスとして実装

        Returns:
            psycopg2.Connection: 生のPostgreSQL接続
        """
        with self.get_raw_connection() as connection:
            yield connection

    def initialize_database(self) -> bool:
        """データベーススキーマ初期化

        PostgreSQL用のテーブル作成とデモデータ投入を実行

        Returns:
            bool: 初期化成功時True
        """
        try:
            schema_file_path = os.path.join(os.path.dirname(__file__), "postgres_schema.sql")

            if not os.path.exists(schema_file_path):
                self.logger.error(f"PostgreSQLスキーマファイルが見つかりません: {schema_file_path}")
                return False

            success = self.create_tables_from_sql(schema_file_path)
            if success:
                self.logger.info("PostgreSQLデータベース初期化完了")
            else:
                self.logger.error("PostgreSQLデータベース初期化に失敗")

            return success

        except Exception as e:
            self.logger.error(f"PostgreSQLデータベース初期化エラー: {e}")
            return False

    def is_database_initialized(self) -> bool:
        """データベース初期化確認

        Returns:
            bool: 初期化済みの場合True
        """
        try:
            with self.get_session() as session:
                # usersテーブルの存在確認
                result = session.execute(
                    text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'users'
                    );
                """)
                )

                exists = result.scalar()
                self.logger.debug(f"PostgreSQLデータベース初期化確認: {exists}")
                return bool(exists)

        except Exception as e:
            self.logger.error(f"PostgreSQLデータベース初期化確認エラー: {e}")
            return False

    def close_connections(self) -> None:
        """全接続を閉じる"""
        try:
            if self._engine:
                self._engine.dispose()
                self.logger.info("PostgreSQLエンジン接続プール閉鎖完了")

            if self._connector:
                self._connector.close()
                self.logger.info("Cloud SQL Connector閉鎖完了")

        except Exception as e:
            self.logger.error(f"PostgreSQL接続閉鎖エラー: {e}")

    def execute_update(self, query: str, params: tuple = ()) -> None:
        """SQLiteManager互換のexecute_updateメソッド

        SQLiteの?プレースホルダーをPostgreSQLの%s形式に変換して実行

        Args:
            query: SQL文（SQLite形式）
            params: パラメータタプル
        """
        try:
            # SQLite形式（?）からPostgreSQL形式（%s）に変換
            postgres_query = query.replace("?", "%s")

            with self.get_raw_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(postgres_query, params)
                    self.logger.debug(f"PostgreSQL update実行完了: {cursor.rowcount}行影響")

        except Exception as e:
            self.logger.error(f"PostgreSQL update実行エラー: {e}")
            raise RuntimeError(f"SQLの実行に失敗しました: {e}") from e

    def execute_query(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        """SQLiteManager互換のexecute_queryメソッド

        SQLiteの?プレースホルダーをPostgreSQLの%s形式に変換して実行

        Args:
            query: SQL文（SQLite形式）
            params: パラメータタプル

        Returns:
            list[dict]: クエリ結果
        """
        try:
            # SQLite形式（?）からPostgreSQL形式（%s）に変換
            postgres_query = query.replace("?", "%s")

            with self.get_raw_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(postgres_query, params)

                    # カラム名取得
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()

                        # 辞書形式に変換
                        result = [dict(zip(columns, row)) for row in rows]
                        self.logger.debug(f"PostgreSQL query実行完了: {len(result)}行取得")
                        return result
                    else:
                        return []

        except Exception as e:
            self.logger.error(f"PostgreSQL query実行エラー: {e}")
            raise RuntimeError(f"SQLの実行に失敗しました: {e}") from e

    def __del__(self) -> None:
        """デストラクタ - 接続リソース解放"""
        self.close_connections()
