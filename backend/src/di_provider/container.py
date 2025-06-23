import logging
from typing import Any

from dependency_injector import containers, providers

from src.application.interface.protocols.file_operator import FileOperatorProtocol
from src.application.interface.protocols.image_analyzer import ImageAnalyzerProtocol
from src.application.interface.protocols.voice_analyzer import VoiceAnalyzerProtocol
from src.application.usecases.file_management_usecase import FileManagementUseCase
from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase
from src.application.usecases.record_management_usecase import RecordManagementUseCase
from src.application.usecases.voice_analysis_usecase import VoiceAnalysisUseCase
from src.config.settings import AppSettings, get_settings
from src.infrastructure.adapters.file_operator import GcsFileOperator
from src.infrastructure.adapters.gemini_image_analyzer import GeminiImageAnalyzer
from src.infrastructure.adapters.gemini_voice_analyzer import GeminiVoiceAnalyzer
from src.infrastructure.adapters.memory_repositories import MemoryRepositoryFactory
from src.share.logger import setup_logger


# ========== Agent層ファクトリー関数（循環import回避） ==========
def _create_tool_registry(container, logger):
    """ツールレジストリ作成"""
    from src.agents.config.tool_registry import ToolRegistry

    return ToolRegistry(container, logger)


def _create_agent_factory(tool_registry, logger):
    """エージェントファクトリー作成"""
    from src.agents.config.agent_factory import AgentFactory

    return AgentFactory(tool_registry, logger)


class DIContainer(containers.DeclarativeContainer):
    """統合DIContainer - 型安全providers形式

    dependency-injector v4.x系の型アノテーション付きパターンを使用
    Protocol型指定により型安全性とIDEサポートを向上
    """

    # ========== CORE LAYER ==========

    config: providers.Provider[AppSettings] = providers.Singleton(get_settings)

    logger: providers.Provider[logging.Logger] = providers.Singleton(
        lambda config: setup_logger(name=config.APP_NAME, env=config.ENVIRONMENT),
        config=config,
    )

    # ========== INFRASTRUCTURE LAYER ==========

    file_operator: providers.Provider[FileOperatorProtocol] = providers.Singleton(
        GcsFileOperator,
        project_id=config.provided.GOOGLE_CLOUD_PROJECT,
        logger=logger,
    )

    image_analyzer: providers.Provider[ImageAnalyzerProtocol] = providers.Singleton(
        GeminiImageAnalyzer,
        logger=logger,
    )

    voice_analyzer: providers.Provider[VoiceAnalyzerProtocol] = providers.Singleton(
        GeminiVoiceAnalyzer,
        logger=logger,
    )

    repository_factory: providers.Provider[MemoryRepositoryFactory] = providers.Singleton(MemoryRepositoryFactory)

    # ========== APPLICATION LAYER ==========

    image_analysis_usecase: providers.Provider[ImageAnalysisUseCase] = providers.Factory(
        ImageAnalysisUseCase,
        image_analyzer=image_analyzer,
        logger=logger,
    )

    file_management_usecase: providers.Provider[FileManagementUseCase] = providers.Factory(
        FileManagementUseCase,
        file_operator=file_operator,
        logger=logger,
    )

    voice_analysis_usecase: providers.Provider[VoiceAnalysisUseCase] = providers.Factory(
        VoiceAnalysisUseCase,
        voice_analyzer=voice_analyzer,
        logger=logger,
    )

    record_management_usecase: providers.Provider[RecordManagementUseCase] = providers.Factory(
        RecordManagementUseCase,
        child_record_repository=repository_factory.provided.get_child_record_repository(),
        logger=logger,
    )

    # ========== AGENT LAYER ==========
    # NOTE: Agent層は循環import回避のため関数内importを使用

    tool_registry: providers.Provider[Any] = providers.Singleton(
        _create_tool_registry,
        container=providers.Self,
        logger=logger,
    )

    agent_factory: providers.Provider[Any] = providers.Singleton(
        _create_agent_factory,
        tool_registry=tool_registry,
        logger=logger,
    )
