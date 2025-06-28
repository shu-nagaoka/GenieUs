"""FastAPI依存性注入設定

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- FastAPI Depends統合パターン
- CompositionRoot経由DI注入
"""

import logging
from typing import Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.agents.agent_manager import AgentManager
from src.application.usecases.agent_info_usecase import AgentInfoUseCase
from src.application.usecases.chat_support_usecase import ChatSupportUseCase
from src.application.usecases.effort_report_usecase import EffortReportUseCase
from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.application.usecases.growth_record_usecase import GrowthRecordUseCase
from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase
from src.application.usecases.meal_plan_management_usecase import MealPlanManagementUseCase
from src.application.usecases.memory_record_usecase import MemoryRecordUseCase
from src.application.usecases.record_management_usecase import RecordManagementUseCase
from src.application.usecases.schedule_event_usecase import ScheduleEventUseCase
from src.application.usecases.search_history_usecase import SearchHistoryUseCase
from src.application.usecases.streaming_chat_usecase import StreamingChatUseCase
from src.application.usecases.user_management_usecase import UserManagementUseCase
from src.application.usecases.voice_analysis_usecase import VoiceAnalysisUseCase


def get_family_management_usecase(request: Request) -> FamilyManagementUseCase:
    """家族管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("family_management")


def get_growth_record_usecase(request: Request) -> GrowthRecordUseCase:
    """成長記録管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("growth_record_management")


def get_memory_record_usecase(request: Request) -> MemoryRecordUseCase:
    """メモリー記録管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("memory_record_management")


def get_schedule_event_usecase(request: Request) -> ScheduleEventUseCase:
    """予定イベント管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("schedule_event_management")


def get_effort_report_usecase(request: Request) -> EffortReportUseCase:
    """努力レポート管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("effort_report_management")


def get_meal_plan_management_usecase(request: Request) -> MealPlanManagementUseCase:
    """食事プラン管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("meal_plan_management")


def get_chat_support_usecase(request: Request) -> ChatSupportUseCase:
    """チャットサポートUseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("chat_support")


def get_agent_info_usecase(request: Request) -> AgentInfoUseCase:
    """エージェント情報UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("agent_info")


def get_streaming_chat_usecase(request: Request) -> StreamingChatUseCase:
    """ストリーミングチャットUseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("streaming_chat")


def get_user_management_usecase(request: Request) -> UserManagementUseCase:
    """ユーザー管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("user_management")


def get_image_analysis_usecase(request: Request) -> ImageAnalysisUseCase:
    """画像解析UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("image_analysis")


def get_voice_analysis_usecase(request: Request) -> VoiceAnalysisUseCase:
    """音声解析UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("voice_analysis")


def get_record_management_usecase(request: Request) -> RecordManagementUseCase:
    """記録管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("record_management")


def get_search_history_usecase(request: Request) -> SearchHistoryUseCase:
    """検索履歴UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("search_history")


# ========== AgentManager & Logger DI Functions ==========


def get_agent_manager(request: Request) -> AgentManager:
    """AgentManagerを取得（DI注入パターン）"""
    return request.app.agent_manager


def get_logger(request: Request) -> logging.Logger:
    """ロガーを取得（DI注入パターン）"""
    return request.app.logger


# ========== Generic UseCase Getter ==========


def get_usecase(request: Request, usecase_name: str) -> Any:
    """指定されたUseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required(usecase_name)


# ========== Authentication Dependencies ==========

# HTTPBearerスキーマ（再利用可能）
security = HTTPBearer(auto_error=False)


def get_auth_middleware(request: Request):
    """認証ミドルウェアを取得"""
    composition_root = request.app.composition_root
    return composition_root.get_auth_middleware()


async def get_current_user_required(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """必須認証 - 認証が必要なエンドポイント用"""
    auth_middleware = get_auth_middleware(request)
    return await auth_middleware.require_authentication(credentials)


async def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any] | None:
    """オプション認証 - 認証が任意のエンドポイント用"""
    auth_middleware = get_auth_middleware(request)
    return await auth_middleware.optional_authentication(credentials)


def get_user_id_required(
    current_user: dict[str, Any] = Depends(get_current_user_required),
) -> str:
    """認証必須でuser_idを取得"""
    return current_user["user_id"]


def get_user_id_optional(
    current_user: dict[str, Any] | None = Depends(get_current_user_optional),
) -> str | None:
    """認証任意でuser_idを取得"""
    return current_user["user_id"] if current_user else None
