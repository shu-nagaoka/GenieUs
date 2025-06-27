"""予定管理API - UseCase Pattern"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.usecases.schedule_event_usecase import ScheduleEventUseCase
from src.presentation.api.dependencies import get_schedule_event_usecase

router = APIRouter(prefix="/schedules", tags=["schedules"])


class ScheduleEventCreateRequest(BaseModel):
    """予定作成リクエスト"""

    title: str
    date: str
    time: str
    type: str  # vaccination, outing, checkup, other
    location: str | None = None
    description: str | None = None
    status: str = "upcoming"  # upcoming, completed, cancelled
    created_by: str = "genie"
    user_id: str = "frontend_user"


class ScheduleEventUpdateRequest(BaseModel):
    """予定更新リクエスト"""

    title: str | None = None
    date: str | None = None
    time: str | None = None
    type: str | None = None
    location: str | None = None
    description: str | None = None
    status: str | None = None
    created_by: str | None = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_schedule_event(
    request: ScheduleEventCreateRequest,
    schedule_event_usecase: ScheduleEventUseCase = Depends(get_schedule_event_usecase),
) -> dict[str, Any]:
    """予定を作成"""
    try:
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")

        result = await schedule_event_usecase.create_schedule_event(user_id=user_id, event_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_schedule_events(
    user_id: str = "frontend_user",
    status: str | None = None,
    schedule_event_usecase: ScheduleEventUseCase = Depends(get_schedule_event_usecase),
) -> dict[str, Any]:
    """予定一覧を取得"""
    try:
        filters = {}
        if status:
            filters["status"] = status

        result = await schedule_event_usecase.get_schedule_events(user_id, filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{event_id}")
async def get_schedule_event(
    event_id: str,
    user_id: str = "frontend_user",
    schedule_event_usecase: ScheduleEventUseCase = Depends(get_schedule_event_usecase),
) -> dict[str, Any]:
    """特定の予定を取得"""
    try:
        result = await schedule_event_usecase.get_schedule_event(user_id, event_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{event_id}")
async def update_schedule_event(
    event_id: str,
    request: ScheduleEventUpdateRequest,
    schedule_event_usecase: ScheduleEventUseCase = Depends(get_schedule_event_usecase),
) -> dict[str, Any]:
    """予定を更新"""
    try:
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")

        result = await schedule_event_usecase.update_schedule_event(
            user_id=user_id, event_id=event_id, update_data=request_data,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{event_id}")
async def delete_schedule_event(
    event_id: str,
    user_id: str = "frontend_user",
    schedule_event_usecase: ScheduleEventUseCase = Depends(get_schedule_event_usecase),
) -> dict[str, Any]:
    """予定を削除"""
    try:
        result = await schedule_event_usecase.delete_schedule_event(user_id, event_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/status/{event_id}")
async def update_schedule_status(
    event_id: str,
    status: str,
    user_id: str = "frontend_user",
    schedule_event_usecase: ScheduleEventUseCase = Depends(get_schedule_event_usecase),
) -> dict[str, Any]:
    """予定のステータスを更新"""
    try:
        result = await schedule_event_usecase.update_schedule_status(user_id=user_id, event_id=event_id, status=status)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
