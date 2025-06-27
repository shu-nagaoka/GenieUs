"""メモリー記録管理API - UseCase Pattern"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.usecases.memory_record_usecase import MemoryRecordUseCase
from src.presentation.api.dependencies import get_memory_record_usecase

router = APIRouter(prefix="/memories", tags=["memories"])


class MemoryRecordCreateRequest(BaseModel):
    """メモリー記録作成リクエスト"""

    title: str
    description: str
    date: str
    type: str  # photo, video, album
    category: str  # milestone, daily, family, special
    media_url: str | None = None
    thumbnail_url: str | None = None
    location: str | None = None
    tags: list[str] = []
    favorited: bool = False
    user_id: str = "frontend_user"


class MemoryRecordUpdateRequest(BaseModel):
    """メモリー記録更新リクエスト"""

    title: str | None = None
    description: str | None = None
    date: str | None = None
    type: str | None = None
    category: str | None = None
    media_url: str | None = None
    thumbnail_url: str | None = None
    location: str | None = None
    tags: list[str] | None = None
    favorited: bool | None = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_memory_record(
    request: MemoryRecordCreateRequest,
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """メモリー記録を作成"""
    try:
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")

        result = await memory_record_usecase.create_memory_record(user_id=user_id, record_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_memory_records(
    user_id: str = "frontend_user",
    type: str | None = None,
    category: str | None = None,
    favorited: bool | None = None,
    tags: str | None = None,
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """メモリー記録一覧を取得"""
    try:
        filters = {}
        if type:
            filters["type"] = type
        if category:
            filters["category"] = category
        if favorited is not None:
            filters["favorited"] = favorited
        if tags:
            filters["tags"] = tags

        result = await memory_record_usecase.get_memory_records(user_id, filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{memory_id}")
async def get_memory_record(
    memory_id: str,
    user_id: str = "frontend_user",
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """特定のメモリー記録を取得"""
    try:
        result = await memory_record_usecase.get_memory_record(user_id, memory_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{memory_id}")
async def update_memory_record(
    memory_id: str,
    request: MemoryRecordUpdateRequest,
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """メモリー記録を更新"""
    try:
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")

        result = await memory_record_usecase.update_memory_record(
            user_id=user_id, memory_id=memory_id, update_data=request_data,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{memory_id}")
async def delete_memory_record(
    memory_id: str,
    user_id: str = "frontend_user",
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """メモリー記録を削除"""
    try:
        result = await memory_record_usecase.delete_memory_record(user_id, memory_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/favorite/{memory_id}")
async def toggle_memory_favorite(
    memory_id: str,
    favorited: bool,
    user_id: str = "frontend_user",
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """メモリーのお気に入り状態を切り替え"""
    try:
        result = await memory_record_usecase.toggle_memory_favorite(
            user_id=user_id, memory_id=memory_id, favorited=favorited,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favorites")
async def get_favorite_memories(
    user_id: str = "frontend_user",
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """お気に入りメモリーを取得"""
    try:
        result = await memory_record_usecase.get_favorite_memories(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/albums")
async def get_albums(
    user_id: str = "frontend_user",
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """アルバム一覧を取得"""
    try:
        result = await memory_record_usecase.get_albums(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags")
async def get_memory_tags(
    user_id: str = "frontend_user",
    memory_record_usecase: MemoryRecordUseCase = Depends(get_memory_record_usecase),
) -> dict[str, Any]:
    """使用中のタグ一覧を取得"""
    try:
        result = await memory_record_usecase.get_memory_tags(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
