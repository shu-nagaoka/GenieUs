"""Composition Root Pattern -

main.pyでの中央集約組み立てによる完全なDI統合アーキテクチャ
providers.Self問題を根本解決し、型安全な依存性注入を実現
"""

import logging
from typing import Any, Generic, TypeVar

from google.adk.tools import FunctionTool

from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.application.usecases.file_management_usecase import FileManagementUseCase
from src.application.usecases.growth_record_usecase import GrowthRecordUseCase
from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase
from src.application.usecases.memory_record_usecase import MemoryRecordUseCase
from src.application.usecases.record_management_usecase import RecordManagementUseCase
from src.application.usecases.schedule_event_usecase import ScheduleEventUseCase
from src.application.usecases.effort_report_usecase import EffortReportUseCase
from src.application.usecases.voice_analysis_usecase import VoiceAnalysisUseCase
from src.config.settings import AppSettings, get_settings
from src.infrastructure.adapters.file_operator import GcsFileOperator
from src.infrastructure.adapters.gemini_image_analyzer import GeminiImageAnalyzer
from src.infrastructure.adapters.gemini_voice_analyzer import GeminiVoiceAnalyzer
from src.infrastructure.adapters.memory_repositories import MemoryRepositoryFactory
from src.infrastructure.adapters.persistence.family_repository import FamilyRepository
from src.infrastructure.adapters.persistence.growth_record_repository import GrowthRecordRepository
from src.infrastructure.adapters.persistence.memory_record_repository import MemoryRecordRepository
from src.infrastructure.adapters.persistence.schedule_event_repository import ScheduleEventRepository
from src.infrastructure.adapters.persistence.effort_report_repository import EffortReportRepository
from src.share.logger import setup_logger

T = TypeVar("T")


class CompositionRootFactory:
    """CompositionRoot作成ファクトリー - Pure依存性組み立て"""

    @staticmethod
    def create(settings: AppSettings | None = None, logger: logging.Logger | None = None) -> "CompositionRoot":
        """CompositionRoot作成（本番・テスト統一）"""
        settings = settings or get_settings()
        logger = logger or setup_logger(name=settings.APP_NAME, env=settings.ENVIRONMENT)
        return CompositionRoot(settings=settings, logger=logger)


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

        # Build dependency tree
        self._build_infrastructure_layer()
        self._build_application_layer()
        self._build_tool_layer()

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

        # Family Repository
        family_repository = FamilyRepository(logger=self.logger)
        self._infrastructure.register("family_repository", family_repository)

        # Growth Record Repository
        growth_record_repository = GrowthRecordRepository(logger=self.logger)
        self._infrastructure.register("growth_record_repository", growth_record_repository)

        # Memory Record Repository
        memory_record_repository = MemoryRecordRepository(logger=self.logger)
        self._infrastructure.register("memory_record_repository", memory_record_repository)

        # Schedule Event Repository
        schedule_event_repository = ScheduleEventRepository(logger=self.logger)
        self._infrastructure.register("schedule_event_repository", schedule_event_repository)

        # Effort Report Repository
        effort_report_repository = EffortReportRepository(logger=self.logger)
        self._infrastructure.register("effort_report_repository", effort_report_repository)

        self.logger.info("Infrastructure層組み立て完了")

    def _build_application_layer(self) -> None:
        """Application層組み立て（UseCase）"""
        self.logger.info("Application層組み立て開始...")

        # Infrastructure依存関係取得
        image_analyzer = self._infrastructure.get_required("image_analyzer")
        voice_analyzer = self._infrastructure.get_required("voice_analyzer")
        file_operator = self._infrastructure.get_required("file_operator")
        repository_factory = self._infrastructure.get_required("repository_factory")
        family_repository = self._infrastructure.get_required("family_repository")
        growth_record_repository = self._infrastructure.get_required("growth_record_repository")
        memory_record_repository = self._infrastructure.get_required("memory_record_repository")
        schedule_event_repository = self._infrastructure.get_required("schedule_event_repository")
        effort_report_repository = self._infrastructure.get_required("effort_report_repository")

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
            schedule_event_repository=schedule_event_repository,
            logger=self.logger,
        )

        effort_report_usecase = EffortReportUseCase(
            effort_report_repository=effort_report_repository,
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

        self.logger.info("Tool層組み立て完了")

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

    # ========== One-time Assembly API (main.py only) ==========

    def get_all_tools(self) -> dict[str, FunctionTool]:
        """全ツール取得（main.pyでの一回限りの組み立て用）"""
        return {name: tool for name, tool in self._tools._services.items() if tool is not None}
