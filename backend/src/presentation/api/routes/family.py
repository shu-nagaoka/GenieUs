"""家族情報管理API"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.presentation.api.dependencies import get_family_management_usecase


router = APIRouter(prefix="/family", tags=["family"])


class FamilyRegistrationRequest(BaseModel):
    """家族情報登録リクエスト"""

    parent_name: str = ""
    family_structure: str = ""
    concerns: str = ""
    children: list[dict] = []
    user_id: str = "frontend_user"  # user_idフィールドを追加


class FamilyUpdateRequest(BaseModel):
    """家族情報更新リクエスト"""

    parent_name: str = ""
    family_structure: str = ""
    concerns: str = ""
    children: list[dict] = []
    user_id: str = "frontend_user"  # user_idフィールドを追加


@router.post("/register")
async def register_family_info(
    request: FamilyRegistrationRequest,
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> Dict[str, Any]:
    """家族情報を登録"""
    try:
        # リクエストボディからuser_idを取得、なければデフォルト値を使用
        request_data = request.dict()
        user_id = request_data.get("user_id", "frontend_user")

        result = await family_usecase.register_family_info(user_id=user_id, family_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_family_info(
    user_id: str = "frontend_user",  # 本来はJWTから取得
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> Dict[str, Any]:
    """家族情報を取得"""
    try:
        family_info = await family_usecase.get_family_info(user_id)

        if family_info:
            return {"success": True, "data": family_info}
        else:
            return {"success": False, "message": "家族情報が見つかりません"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update")
async def update_family_info(
    request: FamilyUpdateRequest,
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> Dict[str, Any]:
    """家族情報を更新"""
    try:
        # リクエストボディからuser_idを取得、なければデフォルト値を使用
        request_data = request.dict()
        user_id = request_data.get("user_id", "frontend_user")

        result = await family_usecase.update_family_info(user_id=user_id, family_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_family_info(
    user_id: str = "frontend_user",  # 本来はJWTから取得
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> Dict[str, Any]:
    """家族情報を削除"""
    try:
        result = await family_usecase.delete_family_info(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
