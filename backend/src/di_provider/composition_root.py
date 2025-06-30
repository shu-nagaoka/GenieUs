"""Composition Root Pattern -

main.pyでの中央集約組み立てによる完全なDI統合アーキテクチャ
providers.Self問題を根本解決し、型安全な依存性注入を実現
"""

import logging
from typing import Any, Generic, TypeVar

from google.adk.tools import FunctionTool
from src.agents.routing_strategy import RoutingStrategy
from src.application.usecases.agent_info_usecase import AgentInfoUseCase
from src.application.usecases.chat_support_usecase import ChatSupportUseCase
from src.application.usecases.effort_report_usecase import EffortReportUseCase
from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.application.usecases.file_management_usecase import FileManagementUseCase
from src.application.usecases.growth_record_usecase import GrowthRecordUseCase
from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase
from src.application.usecases.interactive_confirmation_usecase import (
    InteractiveConfirmationUseCase,
)
from src.application.usecases.meal_plan_management_usecase import (
    MealPlanManagementUseCase,
)
from src.application.usecases.meal_record_usecase import MealRecordUseCase
from src.application.usecases.memory_record_usecase import MemoryRecordUseCase
from src.application.usecases.record_management_usecase import RecordManagementUseCase
from src.application.usecases.schedule_event_usecase import ScheduleEventUseCase
from src.application.usecases.search_history_usecase import SearchHistoryUseCase
from src.application.usecases.streaming_chat_usecase import StreamingChatUseCase
from src.application.usecases.user_management_usecase import UserManagementUseCase
from src.application.usecases.voice_analysis_usecase import VoiceAnalysisUseCase
from src.config.settings import AppSettings, get_settings
from src.infrastructure.adapters.file_operator import GcsFileOperator
from src.infrastructure.adapters.gemini_image_analyzer import GeminiImageAnalyzer
from src.infrastructure.adapters.gemini_voice_analyzer import GeminiVoiceAnalyzer
from src.infrastructure.adapters.meal_plan_manager import InMemoryMealPlanManager
from src.infrastructure.adapters.memory_repositories import MemoryRepositoryFactory
# 削除: 重複インポート行

# PostgreSQL永続化レイヤー
from src.infrastructure.adapters.persistence.postgresql.family_repository import (
    FamilyRepository as PostgreSQLFamilyRepository,
)
from src.infrastructure.adapters.persistence.postgresql.effort_report_repository import (
    EffortReportRepository as PostgreSQLEffortReportRepository,
)
from src.infrastructure.adapters.persistence.postgresql.schedule_record_repository import (
    ScheduleRecordRepository as PostgreSQLScheduleRecordRepository,
)
from src.infrastructure.adapters.persistence.postgresql.user_repository import (
    UserRepository as PostgreSQLUserRepository,
)
from src.infrastructure.adapters.persistence.postgresql.meal_record_repository import (
    MealRecordRepository as PostgreSQLMealRecordRepository,
)
from src.infrastructure.adapters.persistence.postgresql.growth_record_repository import (
    GrowthRecordRepository as PostgreSQLGrowthRecordRepository,
)
from src.infrastructure.adapters.persistence.postgresql.memory_record_repository import (
    MemoryRecordRepository as PostgreSQLMemoryRecordRepository,
)
from src.infrastructure.adapters.persistence.postgresql.schedule_event_repository import (
    ScheduleEventRepository as PostgreSQLScheduleEventRepository,
)
# SQLite永続化レイヤー - 正規のSQLite実装のみ
from src.infrastructure.adapters.persistence.sqlite.effort_report_repository_sqlite import (
    EffortReportRepository as SQLiteEffortReportRepository,
)
from src.infrastructure.adapters.persistence.sqlite.family_repository_sqlite import (
    FamilyRepository as SQLiteFamilyRepository,
)
from src.infrastructure.adapters.persistence.sqlite.growth_record_repository_sqlite import (
    GrowthRecordRepository as SQLiteGrowthRecordRepository,
)
from src.infrastructure.adapters.persistence.sqlite.memory_record_repository_sqlite import (
    MemoryRecordRepository as SQLiteMemoryRecordRepository,
)
from src.infrastructure.adapters.persistence.sqlite.schedule_record_repository_sqlite import (
    ScheduleRecordRepository as SQLiteScheduleRecordRepository,
)

# JSON永続化レイヤー - 暫定的に必要なもののみ（将来削除予定）
from src.infrastructure.adapters.persistence.json.meal_record_repository import (
    MealRecordRepository as JSONMealRecordRepository,
)
from src.infrastructure.adapters.persistence.json.user_repository import UserRepository as JSONUserRepository
from src.infrastructure.database.data_migrator import DataMigrator
from src.infrastructure.database.sqlite_manager import DatabaseMigrator, SQLiteManager
from src.infrastructure.database.postgres_manager import PostgreSQLManager
from src.presentation.api.middleware.auth_middleware import (
    AuthMiddleware,
    GoogleTokenVerifier,
    JWTAuthenticator,
)
from src.share.logger import setup_logger

T = TypeVar("T")


class CompositionRootFactory:
    """CompositionRoot作成ファクトリー - Pure依存性組み立て（シングルトン）"""
    _instance: "CompositionRoot | None" = None

    @classmethod
    def create(cls, settings: AppSettings | None = None, logger: logging.Logger | None = None) -> "CompositionRoot":
        """CompositionRoot作成（シングルトンパターン）"""
        if cls._instance is None:
            settings = settings or get_settings()
            logger = logger or setup_logger(name=settings.APP_NAME, env=settings.ENVIRONMENT)
            cls._instance = CompositionRoot(settings=settings, logger=logger)
            logger.info("🏗️ CompositionRootシングルトン初期化完了")
        return cls._instance


class ServiceRegistry(Generic[T]):
    """型安全なサービスレジストリ"""

    def __init__(self) -> None:
        self._services: dict[str, T] = {}

    def register(self, name: str, service: T) -> None:
        """サービス登録"""
        self._services[name] = service

    def get(self, name: str) -> T | None:
        """サービス取得"""
        return self._services.get(name)

    def get_required(self, name: str) -> T:
        """必須サービス取得（存在しない場合は例外）"""
        service = self.get(name)
        if service is None:
            raise ValueError(f"Required service not found: {name}")
        return service


class CompositionRoot:
    """アプリケーション全体の依存関係組み立て（main.py中央集約）

    - 初期化時に全依存関係を組み立て
    - シングルトン管理で性能確保
    - テスト時のモック注入対応
    """

    def __init__(self, settings: AppSettings, logger: logging.Logger) -> None:
        """Pure Composition Root初期化

        Args:
            settings: アプリケーション設定（必須注入）
            logger: ロガー（必須注入）

        """
        # Core components - 完全外部注入
        self.settings = settings
        self.logger = logger

        # Service registries
        self._usecases = ServiceRegistry[Any]()
        self._tools = ServiceRegistry[FunctionTool]()
        self._infrastructure = ServiceRegistry[Any]()
        self._routing_strategy: RoutingStrategy | None = None

        # Build dependency tree
        self._build_infrastructure_layer()
        self._build_application_layer()
        self._build_tool_layer()
        self._build_agent_registry()  # ルーティング戦略より先に初期化
        self._build_routing_strategy()

        self.logger.info("✅ CompositionRoot初期化完了: 全依存関係組み立て成功")

    def _build_infrastructure_layer(self) -> None:
        """Infrastructure層組み立て"""
        self.logger.info("Infrastructure層組み立て開始...")

        # Repository Factory
        repository_factory = MemoryRepositoryFactory()
        self._infrastructure.register("repository_factory", repository_factory)

        # File Operator
        file_operator = GcsFileOperator(project_id=self.settings.GOOGLE_CLOUD_PROJECT, logger=self.logger)
        self._infrastructure.register("file_operator", file_operator)

        # AI Analyzers
        image_analyzer = GeminiImageAnalyzer(logger=self.logger)
        voice_analyzer = GeminiVoiceAnalyzer(logger=self.logger)

        self._infrastructure.register("image_analyzer", image_analyzer)
        self._infrastructure.register("voice_analyzer", voice_analyzer)

        # JSON リポジトリは削除: PostgreSQL優先、SQLiteフォールバック方式に統一

        # Meal Plan Manager
        meal_plan_manager = InMemoryMealPlanManager(logger=self.logger)
        self._infrastructure.register("meal_plan_manager", meal_plan_manager)

        # Authentication components
        google_verifier = GoogleTokenVerifier(logger=self.logger)
        jwt_authenticator = JWTAuthenticator(settings=self.settings, logger=self.logger)
        auth_middleware = AuthMiddleware(
            settings=self.settings,
            logger=self.logger,
            google_verifier=google_verifier,
            jwt_authenticator=jwt_authenticator,
        )

        self._infrastructure.register("google_verifier", google_verifier)
        self._infrastructure.register("jwt_authenticator", jwt_authenticator)
        self._infrastructure.register("auth_middleware", auth_middleware)

        # Database components
        self.logger.info(f"🔍 データベース設定確認: DATABASE_TYPE={self.settings.DATABASE_TYPE}")
        
        if self.settings.DATABASE_TYPE == "sqlite":
            self.logger.info("🗃️ SQLiteブランチに入ります")
            sqlite_manager = SQLiteManager(settings=self.settings, logger=self.logger)
            database_migrator = DatabaseMigrator(sqlite_manager=sqlite_manager, logger=self.logger)

            self._infrastructure.register("sqlite_manager", sqlite_manager)
            self._infrastructure.register("database_migrator", database_migrator)

            # データベース初期化（必要に応じて）
            if not database_migrator.is_database_initialized():
                self.logger.info("データベース未初期化のため、初期化を実行")
                database_migrator.initialize_database()

            # User Repository (SQLite版) - JSONからSQLite実装に変更
            from src.infrastructure.adapters.persistence.json.user_repository import UserRepository as JSONUserRepository
            user_repository = JSONUserRepository(sqlite_manager=sqlite_manager, logger=self.logger)
            self._infrastructure.register("user_repository", user_repository)

            # Data Migrator (JSON → SQLite)
            data_migrator = DataMigrator(settings=self.settings, sqlite_manager=sqlite_manager, logger=self.logger)
            self._infrastructure.register("data_migrator", data_migrator)

            # Meal Record Repository (SQLite版) - 暫定的にJSONフォールバック
            meal_record_repository = JSONMealRecordRepository(logger=self.logger)
            self._infrastructure.register("meal_record_repository", meal_record_repository)

            # Schedule Record Repository (SQLite版)
            schedule_record_repository = SQLiteScheduleRecordRepository(sqlite_manager=sqlite_manager, logger=self.logger)
            self._infrastructure.register("schedule_record_repository", schedule_record_repository)

            # Family Repository (SQLite版)
            family_repository = SQLiteFamilyRepository(sqlite_manager=sqlite_manager, logger=self.logger)
            self._infrastructure.register("family_repository", family_repository)

            # Effort Report Repository (SQLite版)
            effort_report_repository = SQLiteEffortReportRepository(sqlite_manager=sqlite_manager, logger=self.logger)
            self._infrastructure.register("effort_report_repository", effort_report_repository)

            # Growth Record Repository (SQLite版)
            growth_record_repository = SQLiteGrowthRecordRepository(sqlite_manager=sqlite_manager, logger=self.logger)
            self._infrastructure.register("growth_record_repository", growth_record_repository)

            # Memory Record Repository (SQLite版)
            memory_record_repository = SQLiteMemoryRecordRepository(sqlite_manager=sqlite_manager, logger=self.logger)
            self._infrastructure.register("memory_record_repository", memory_record_repository)

        elif self.settings.DATABASE_TYPE == "postgresql":
            self.logger.info(f"🐘 PostgreSQLブランチに入りました: DATABASE_TYPE={self.settings.DATABASE_TYPE}")
            # PostgreSQL Database Manager（Secret Manager統合）
            try:
                # Secret Manager初期化（オプション）
                from src.infrastructure.secrets.secret_manager import SecretManagerService

                secret_manager = SecretManagerService(settings=self.settings, logger=self.logger)
                self._infrastructure.register("secret_manager", secret_manager)
                self.logger.info("✅ Secret Manager統合成功")
            except Exception as e:
                self.logger.warning(f"Secret Manager初期化失敗、環境変数フォールバック: {e}")
                secret_manager = None

            # PostgreSQL Database Manager
            postgres_manager = PostgreSQLManager(
                settings=self.settings, logger=self.logger, secret_manager=secret_manager
            )
            self._infrastructure.register("postgres_manager", postgres_manager)

            # PostgreSQL接続テスト（リトライ機能付き）
            max_retries = 3
            connection_success = False

            for attempt in range(max_retries):
                try:
                    if postgres_manager.test_connection():
                        self.logger.info(f"✅ PostgreSQL接続テスト成功 (試行 {attempt + 1})")
                        connection_success = True
                        break
                    else:
                        self.logger.warning(f"⚠️ PostgreSQL接続テスト失敗 (試行 {attempt + 1})")
                except Exception as e:
                    self.logger.warning(f"⚠️ PostgreSQL接続エラー (試行 {attempt + 1}): {e}")

                if attempt < max_retries - 1:
                    import time

                    self.logger.info(f"🔄 {2**attempt}秒後にリトライします...")
                    time.sleep(2**attempt)

            if not connection_success:
                self.logger.error("❌ PostgreSQL接続テストに失敗しました（全試行終了）")
                # フォールバック: SQLiteに切り替え
                self.logger.warning("🔄 SQLiteフォールバックモードに切り替えます")
                self.settings.DATABASE_TYPE = "sqlite"
                return self._build_infrastructure_layer()  # SQLiteで再試行

            # PostgreSQLデータベース初期化（必要に応じて）
            try:
                if not postgres_manager.is_database_initialized():
                    self.logger.info("📋 PostgreSQLデータベース未初期化のため、初期化を実行")
                    if not postgres_manager.initialize_database():
                        self.logger.error("❌ PostgreSQLデータベース初期化に失敗しました")
                        raise RuntimeError("PostgreSQLデータベース初期化に失敗しました")
                else:
                    self.logger.info("✅ PostgreSQLデータベース既に初期化済み")
            except Exception as e:
                self.logger.error(f"❌ PostgreSQL初期化エラー: {e}")
                # フォールバック: SQLiteに切り替え
                self.logger.warning("🔄 SQLiteフォールバックモードに切り替えます")
                self.settings.DATABASE_TYPE = "sqlite"
                return self._build_infrastructure_layer()  # SQLiteで再試行

            # User Repository (PostgreSQL版)
            user_repository = PostgreSQLUserRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("user_repository", user_repository)

            # Meal Record Repository (PostgreSQL版)
            meal_record_repository = PostgreSQLMealRecordRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("meal_record_repository", meal_record_repository)

            # Schedule Record Repository (PostgreSQL版)
            schedule_record_repository = PostgreSQLScheduleRecordRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("schedule_record_repository", schedule_record_repository)

            # Family Repository (PostgreSQL版)
            family_repository = PostgreSQLFamilyRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("family_repository", family_repository)

            # Effort Report Repository (PostgreSQL版)
            effort_report_repository = PostgreSQLEffortReportRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("effort_report_repository", effort_report_repository)

            # Growth Record Repository (PostgreSQL版)
            growth_record_repository = PostgreSQLGrowthRecordRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("growth_record_repository", growth_record_repository)

            # Memory Record Repository (PostgreSQL版)
            memory_record_repository = PostgreSQLMemoryRecordRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("memory_record_repository", memory_record_repository)

            # Schedule Event Repository (PostgreSQL版)
            schedule_event_repository = PostgreSQLScheduleEventRepository(postgres_manager=postgres_manager, logger=self.logger)
            self._infrastructure.register("schedule_event_repository", schedule_event_repository)
        else:
            self.logger.warning(f"未サポートのデータベースタイプ: {self.settings.DATABASE_TYPE}")
            raise ValueError(f"未サポートのデータベースタイプ: {self.settings.DATABASE_TYPE}")

        self.logger.info("Infrastructure層組み立て完了")

    def _build_application_layer(self) -> None:
        """Application層組み立て（UseCase）"""
        self.logger.info("Application層組み立て開始...")

        # Infrastructure依存関係取得
        image_analyzer = self._infrastructure.get_required("image_analyzer")
        voice_analyzer = self._infrastructure.get_required("voice_analyzer")
        file_operator = self._infrastructure.get_required("file_operator")
        repository_factory = self._infrastructure.get_required("repository_factory")
        # Family repository - SQLite版優先、フォールバックでJSON版
        family_repository = self._infrastructure.get("family_repository") or self._infrastructure.get_required(
            "family_repository_json"
        )
        # Growth record repository - SQLite版優先、フォールバックでJSON版
        growth_record_repository = self._infrastructure.get(
            "growth_record_repository"
        ) or self._infrastructure.get_required("growth_record_repository_json")
        # Memory record repository - SQLite版優先、フォールバックでJSON版
        memory_record_repository = self._infrastructure.get(
            "memory_record_repository"
        ) or self._infrastructure.get_required("memory_record_repository_json")
        schedule_event_repository = self._infrastructure.get_required("schedule_event_repository")
        schedule_record_repository = self._infrastructure.get_required("schedule_record_repository")
        # Meal record repository - SQLite版のみ使用可能
        meal_record_repository = self._infrastructure.get_required("meal_record_repository")
        # Effort report repository - SQLite版優先、フォールバックでJSON版
        effort_report_repository = self._infrastructure.get(
            "effort_report_repository"
        ) or self._infrastructure.get_required("effort_report_repository_json")
        meal_plan_manager = self._infrastructure.get_required("meal_plan_manager")

        # UseCases組み立て
        image_analysis_usecase = ImageAnalysisUseCase(image_analyzer=image_analyzer, logger=self.logger)

        voice_analysis_usecase = VoiceAnalysisUseCase(voice_analyzer=voice_analyzer, logger=self.logger)

        file_management_usecase = FileManagementUseCase(file_operator=file_operator, logger=self.logger)

        record_management_usecase = RecordManagementUseCase(
            child_record_repository=repository_factory.get_child_record_repository(),
            logger=self.logger,
        )

        family_management_usecase = FamilyManagementUseCase(
            family_repository=family_repository,
            logger=self.logger,
        )

        growth_record_usecase = GrowthRecordUseCase(
            growth_record_repository=growth_record_repository,
            family_repository=family_repository,
            logger=self.logger,
        )

        memory_record_usecase = MemoryRecordUseCase(
            memory_record_repository=memory_record_repository,
            logger=self.logger,
        )

        schedule_event_usecase = ScheduleEventUseCase(
            schedule_record_repository=schedule_record_repository,
            logger=self.logger,
        )

        effort_report_usecase = EffortReportUseCase(
            effort_report_repository=effort_report_repository,
            meal_record_repository=meal_record_repository,
            schedule_record_repository=schedule_record_repository,
            family_repository=family_repository,
            ai_analyzer=image_analyzer,
            logger=self.logger,
        )

        meal_plan_management_usecase = MealPlanManagementUseCase(
            meal_plan_manager=meal_plan_manager,
            logger=self.logger,
        )

        chat_support_usecase = ChatSupportUseCase(
            logger=self.logger,
        )

        agent_info_usecase = AgentInfoUseCase(
            logger=self.logger,
        )

        streaming_chat_usecase = StreamingChatUseCase(
            chat_support_usecase=chat_support_usecase,
            agent_info_usecase=agent_info_usecase,
            logger=self.logger,
        )

        search_history_usecase = SearchHistoryUseCase(
            search_history_repository=repository_factory.get_search_history_repository(),
            logger=self.logger,
        )

        # Meal Record UseCase (食事記録機能) - 先に作成
        if self.settings.DATABASE_TYPE == "sqlite":
            meal_record_repository = self._infrastructure.get("meal_record_repository")
            meal_record_usecase = MealRecordUseCase(
                meal_record_repository=meal_record_repository,
                logger=self.logger,
            )
        else:
            meal_record_usecase = None

        interactive_confirmation_usecase = InteractiveConfirmationUseCase(
            meal_record_usecase=meal_record_usecase,
            logger=self.logger,
        )

        # UseCase登録
        self._usecases.register("image_analysis", image_analysis_usecase)
        self._usecases.register("voice_analysis", voice_analysis_usecase)
        self._usecases.register("file_management", file_management_usecase)
        self._usecases.register("record_management", record_management_usecase)
        self._usecases.register("family_management", family_management_usecase)
        self._usecases.register("growth_record_management", growth_record_usecase)
        self._usecases.register("memory_record_management", memory_record_usecase)
        self._usecases.register("schedule_event_management", schedule_event_usecase)
        self._usecases.register("effort_report_management", effort_report_usecase)
        self._usecases.register("meal_plan_management", meal_plan_management_usecase)
        self._usecases.register("chat_support", chat_support_usecase)
        self._usecases.register("agent_info", agent_info_usecase)
        self._usecases.register("streaming_chat", streaming_chat_usecase)
        self._usecases.register("search_history", search_history_usecase)
        self._usecases.register("interactive_confirmation", interactive_confirmation_usecase)

        # Meal Record UseCase 登録
        if meal_record_usecase:
            self._usecases.register("meal_record", meal_record_usecase)

        # User Management UseCase (認証統合)
        if self.settings.DATABASE_TYPE == "sqlite":
            user_repository = self._infrastructure.get("user_repository")
            jwt_authenticator = self._infrastructure.get("jwt_authenticator")
            user_management_usecase = UserManagementUseCase(
                user_repository=user_repository,
                jwt_authenticator=jwt_authenticator,
                logger=self.logger,
            )
            self._usecases.register("user_management", user_management_usecase)

        self.logger.info("Application層組み立て完了")

    def _build_tool_layer(self) -> None:
        """Tool層組み立て（ADK FunctionTool）"""
        self.logger.info("Tool層組み立て開始...")

        # 画像分析ツール
        image_usecase = self._usecases.get_required("image_analysis")
        image_tool = self._create_image_analysis_tool(image_usecase)
        self._tools.register("image_analysis", image_tool)

        # 音声分析ツール
        voice_usecase = self._usecases.get_required("voice_analysis")
        voice_tool = self._create_voice_analysis_tool(voice_usecase)
        self._tools.register("voice_analysis", voice_tool)

        # ファイル管理ツール
        file_usecase = self._usecases.get_required("file_management")
        file_tool = self._create_file_management_tool(file_usecase)
        self._tools.register("file_management", file_tool)

        # 記録管理ツール
        record_usecase = self._usecases.get_required("record_management")
        record_tool = self._create_record_management_tool(record_usecase)
        self._tools.register("record_management", record_tool)

        # Google Search ツール
        google_search_tool = self._create_google_search_tool()
        self._tools.register("google_search", google_search_tool)

        # Interactive Confirmation ツール（Human-in-the-Loop機能）
        interactive_confirmation_tool = self._create_interactive_confirmation_tool()
        self._tools.register("interactive_confirmation", interactive_confirmation_tool)

        # Meal Management Integration ツール（食事管理統合）
        meal_integration_tool = self._create_meal_management_integration_tool()
        self._tools.register("meal_management_integration", meal_integration_tool)

        # Meal Record ツール（食事記録CRUD）
        meal_record_tool = self._create_meal_record_tool()
        self._tools.register("meal_record", meal_record_tool)

        # Schedule ツール（スケジュール管理）
        schedule_tool = self._create_schedule_tool()
        self._tools.register("schedule", schedule_tool)

        # Growth Record ツール（成長記録管理）
        growth_record_tool = self._create_growth_record_tool()
        self._tools.register("growth_record", growth_record_tool)

        # Meal Plan ツール（食事プラン管理）
        meal_plan_tool = self._create_meal_plan_tool()
        self._tools.register("meal_plan", meal_plan_tool)

        self.logger.info("Tool層組み立て完了")

    def _build_agent_registry(self) -> None:
        """Agent Registry組み立て（ADKルーティング統合用）"""
        self.logger.info("Agent Registry組み立て開始...")

        from src.agents.agent_registry import AgentRegistry

        # AgentRegistryを初期化（ツール群を渡す）
        self._registry = AgentRegistry(self.get_all_tools(), self.logger)

        # エージェントを事前初期化（ADKルーティングで専門エージェントが必要）
        self._registry.initialize_all_agents()

        self.logger.info("Agent Registry組み立て完了")

    def _create_image_analysis_tool(self, usecase: ImageAnalysisUseCase) -> FunctionTool:
        """画像分析ツール作成"""
        from src.tools.image_analysis_tool import create_image_analysis_tool

        return create_image_analysis_tool(image_analysis_usecase=usecase, logger=self.logger)

    def _create_voice_analysis_tool(self, usecase: VoiceAnalysisUseCase) -> FunctionTool:
        """音声分析ツール作成"""
        from src.tools.voice_analysis_tool import create_voice_analysis_tool

        return create_voice_analysis_tool(voice_analysis_usecase=usecase, logger=self.logger)

    def _create_file_management_tool(self, usecase: FileManagementUseCase) -> FunctionTool:
        """ファイル管理ツール作成"""
        from src.tools.file_management_tool import create_file_management_tool

        return create_file_management_tool(file_management_usecase=usecase, logger=self.logger)

    def _create_record_management_tool(self, usecase: RecordManagementUseCase) -> FunctionTool:
        """記録管理ツール作成"""
        from src.tools.record_management_tool import create_record_management_tool

        return create_record_management_tool(record_management_usecase=usecase, logger=self.logger)

    def _create_google_search_tool(self):
        """Google Search ツール作成"""
        from google.adk.tools import google_search

        self.logger.info("Google Search ツールが利用可能です")
        return google_search

    def _create_interactive_confirmation_tool(self) -> FunctionTool:
        """Interactive Confirmation ツール作成（Human-in-the-Loop）"""
        from src.tools.interactive_confirmation_tool import InteractiveConfirmationTool

        tool_instance = InteractiveConfirmationTool(logger=self.logger)

        # FunctionToolとしてラップ
        return FunctionTool(func=tool_instance.ask_user_confirmation)

    def _create_meal_management_integration_tool(self) -> FunctionTool:
        """Meal Management Integration ツール作成（食事管理統合）"""
        from src.tools.meal_management_integration_tool import (
            create_meal_management_integration_tool,
        )

        interactive_confirmation_usecase = self._usecases.get_required("interactive_confirmation")
        return create_meal_management_integration_tool(
            interactive_confirmation_usecase=interactive_confirmation_usecase, logger=self.logger
        )

    def _create_meal_record_tool(self) -> FunctionTool:
        """Meal Record ツール作成（食事記録CRUD）"""
        from src.tools.meal_record_tool import create_meal_record_tool

        meal_record_usecase = self._usecases.get("meal_record")
        if meal_record_usecase is None:
            self.logger.warning("MealRecordUseCase が利用できません。SQLiteモードでない可能性があります。")
            # ダミーツールを返すか、Noneを返すかの選択
            from google.adk.tools import FunctionTool

            return FunctionTool(func=lambda: {"error": "MealRecord機能が利用できません"})

        return create_meal_record_tool(meal_record_usecase=meal_record_usecase, logger=self.logger)

    def _create_schedule_tool(self) -> FunctionTool:
        """Schedule ツール作成（スケジュール管理）"""
        from src.tools.schedule_tool_adk import create_schedule_tool

        schedule_usecase = self._usecases.get("schedule_event_management")
        if schedule_usecase is None:
            self.logger.warning("ScheduleEventUseCase が利用できません。")
            from google.adk.tools import FunctionTool

            return FunctionTool(func=lambda: {"error": "Schedule機能が利用できません"})

        return create_schedule_tool(schedule_usecase=schedule_usecase, logger=self.logger)

    def _create_growth_record_tool(self) -> FunctionTool:
        """Growth Record ツール作成（成長記録管理）"""
        from src.tools.growth_record_tool_adk import create_growth_record_tool

        growth_record_usecase = self._usecases.get("growth_record_management")
        if growth_record_usecase is None:
            self.logger.warning("GrowthRecordUseCase が利用できません。")
            from google.adk.tools import FunctionTool

            return FunctionTool(func=lambda: {"error": "GrowthRecord機能が利用できません"})

        return create_growth_record_tool(growth_record_usecase=growth_record_usecase, logger=self.logger)

    def _create_meal_plan_tool(self) -> FunctionTool:
        """Meal Plan ツール作成（食事プラン管理）"""
        from src.tools.meal_plan_tool_adk import create_meal_plan_tool

        meal_plan_usecase = self._usecases.get("meal_plan_management")
        if meal_plan_usecase is None:
            self.logger.warning("MealPlanManagementUseCase が利用できません。")
            from google.adk.tools import FunctionTool

            return FunctionTool(func=lambda: {"error": "MealPlan機能が利用できません"})

        return create_meal_plan_tool(meal_plan_usecase=meal_plan_usecase, logger=self.logger)

    # ========== One-time Assembly API (main.py only) ==========

    def _build_routing_strategy(self) -> None:
        """意図ベースルーティング戦略の組み立て"""
        from src.agents.intent_based_routing_strategy import IntentBasedRoutingStrategy

        self._routing_strategy = IntentBasedRoutingStrategy(logger=self.logger)
        self.logger.info("意図ベースルーティング戦略を使用")

    def get_all_tools(self) -> dict[str, FunctionTool]:
        """全ツール取得（main.pyでの一回限りの組み立て用）"""
        return {name: tool for name, tool in self._tools._services.items() if tool is not None}

    def get_routing_strategy(self) -> RoutingStrategy:
        """ルーティング戦略取得"""
        if self._routing_strategy is None:
            raise ValueError("ルーティング戦略が初期化されていません")
        return self._routing_strategy

    # ========== Authentication API ==========

    def get_auth_middleware(self) -> AuthMiddleware:
        """認証ミドルウェア取得"""
        return self._infrastructure.get("auth_middleware")

    def get_google_verifier(self) -> GoogleTokenVerifier:
        """Google Token検証器取得"""
        return self._infrastructure.get("google_verifier")

    def get_jwt_authenticator(self) -> JWTAuthenticator:
        """JWT認証器取得"""
        return self._infrastructure.get("jwt_authenticator")

    # ========== Database API ==========

    def get_sqlite_manager(self) -> SQLiteManager:
        """SQLiteマネージャー取得"""
        return self._infrastructure.get("sqlite_manager")

    def get_database_migrator(self) -> DatabaseMigrator:
        """データベースマイグレーター取得"""
        return self._infrastructure.get("database_migrator")

    def get_data_migrator(self) -> DataMigrator:
        """データマイグレーター取得"""
        return self._infrastructure.get("data_migrator")

    # ========== Agent Registry API ==========

    def get_agent_registry(self):
        """AgentRegistry取得"""
        if not hasattr(self, "_registry") or not self._registry:
            raise ValueError("AgentRegistryが初期化されていません")
        return self._registry
