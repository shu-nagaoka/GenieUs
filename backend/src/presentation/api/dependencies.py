"""FastAPI依存性注入設定"""

from typing import Any

from fastapi import Request

from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.application.usecases.growth_record_usecase import GrowthRecordUseCase
from src.application.usecases.memory_record_usecase import MemoryRecordUseCase
from src.application.usecases.schedule_event_usecase import ScheduleEventUseCase
from src.application.usecases.effort_report_usecase import EffortReportUseCase


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


# DIコンテナからUseCaseを取得する汎用的な関数
def get_usecase(request: Request, usecase_name: str) -> Any:
    """指定されたUseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required(usecase_name)
