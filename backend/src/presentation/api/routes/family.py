"""家族情報管理API"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.presentation.api.dependencies import (
    get_family_management_usecase,
    get_user_id_optional,
)

router = APIRouter(prefix="/family", tags=["family"])


class FamilyRegistrationRequest(BaseModel):
    """家族情報登録リクエスト"""

    parent_name: str = ""
    family_structure: str = ""
    concerns: str = ""
    living_area: str = ""  # 居住エリア情報
    children: list[dict] = []


class FamilyUpdateRequest(BaseModel):
    """家族情報更新リクエスト"""

    parent_name: str = ""
    family_structure: str = ""
    concerns: str = ""
    living_area: str = ""  # 居住エリア情報
    children: list[dict] = []


@router.post("/register")
async def register_family_info(
    request: FamilyRegistrationRequest,
    user_id: str = Depends(get_user_id_optional),  # 認証統合（オプション）
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> dict[str, Any]:
    """家族情報を登録"""
    try:
        # 認証ユーザーIDまたはデフォルトを使用
        effective_user_id = user_id or "frontend_user"
        request_data = request.dict()

        result = await family_usecase.register_family_info(user_id=effective_user_id, family_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_family_info(
    user_id: str = Depends(get_user_id_optional),  # 認証統合（オプション）
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> dict[str, Any]:
    """家族情報を取得"""
    try:
        # 認証ユーザーIDまたはデフォルトを使用
        effective_user_id = user_id or "frontend_user"
        family_info = await family_usecase.get_family_info(effective_user_id)

        if family_info:
            return {"success": True, "data": family_info}
        else:
            return {"success": False, "message": "家族情報が見つかりません"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update")
async def update_family_info(
    request: FamilyUpdateRequest,
    user_id: str = Depends(get_user_id_optional),  # 認証統合（オプション）
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> dict[str, Any]:
    """家族情報を更新"""
    try:
        # 認証ユーザーIDまたはデフォルトを使用
        effective_user_id = user_id or "frontend_user"
        request_data = request.dict()

        result = await family_usecase.update_family_info(user_id=effective_user_id, family_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_family_info(
    user_id: str = Depends(get_user_id_optional),  # 認証統合（オプション）
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> dict[str, Any]:
    """家族情報を削除"""
    try:
        # 認証ユーザーIDまたはデフォルトを使用
        effective_user_id = user_id or "frontend_user"
        result = await family_usecase.delete_family_info(effective_user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
