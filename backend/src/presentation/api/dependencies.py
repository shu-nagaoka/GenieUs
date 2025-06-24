"""FastAPI依存性注入設定"""

from typing import Any

from fastapi import Request

from src.application.usecases.family_management_usecase import FamilyManagementUseCase


def get_family_management_usecase(request: Request) -> FamilyManagementUseCase:
    """家族管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("family_management")


# DIコンテナからUseCaseを取得する汎用的な関数
def get_usecase(request: Request, usecase_name: str) -> Any:
    """指定されたUseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required(usecase_name)