"""予定管理API"""

import json
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

# データファイルのパス
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
SCHEDULE_EVENTS_FILE = DATA_DIR / "schedules.json"

def load_schedule_events() -> Dict[str, Any]:
    """予定データを読み込み"""
    if SCHEDULE_EVENTS_FILE.exists():
        with open(SCHEDULE_EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_schedule_events(data: Dict[str, Any]) -> None:
    """予定データを保存"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(SCHEDULE_EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

router = APIRouter(prefix="/schedules", tags=["schedules"])


class ScheduleEventCreateRequest(BaseModel):
    """予定作成リクエスト"""
    title: str
    date: str
    time: str
    type: str  # vaccination, outing, checkup, other
    location: Optional[str] = None
    description: Optional[str] = None
    status: str = "upcoming"  # upcoming, completed, cancelled
    created_by: str = "genie"
    user_id: str = "frontend_user"


class ScheduleEventUpdateRequest(BaseModel):
    """予定更新リクエスト"""
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_schedule_event(
    request: ScheduleEventCreateRequest,
) -> Dict[str, Any]:
    """予定を作成"""
    try:
        events = load_schedule_events()
        event_id = str(uuid4())
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")
        
        event_data = {
            "id": event_id,
            "user_id": user_id,
            **request_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        events[event_id] = event_data
        save_schedule_events(events)
        
        return {
            "success": True,
            "id": event_id,
            "data": event_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_schedule_events(
    user_id: str = "frontend_user",
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """予定一覧を取得"""
    try:
        events = load_schedule_events()
        user_events = [
            event for event in events.values()
            if event.get("user_id") == user_id
        ]
        
        # ステータスでフィルタリング
        if status:
            user_events = [
                event for event in user_events
                if event.get("status") == status
            ]
        
        # 日付でソート
        user_events.sort(key=lambda x: x.get("date", ""))
        
        return {
            "success": True,
            "data": user_events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{event_id}")
async def get_schedule_event(
    event_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """特定の予定を取得"""
    try:
        events = load_schedule_events()
        if event_id not in events:
            return {
                "success": False,
                "message": "予定が見つかりません"
            }
        
        event = events[event_id]
        if event.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        return {
            "success": True,
            "data": event
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{event_id}")
async def update_schedule_event(
    event_id: str,
    request: ScheduleEventUpdateRequest,
) -> Dict[str, Any]:
    """予定を更新"""
    try:
        events = load_schedule_events()
        if event_id not in events:
            return {
                "success": False,
                "message": "予定が見つかりません"
            }
        
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")
        
        event = events[event_id]
        if event.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        # 更新データをマージ
        event.update({
            **request_data,
            "updated_at": datetime.now().isoformat()
        })
        
        save_schedule_events(events)
        
        return {
            "success": True,
            "data": event
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{event_id}")
async def delete_schedule_event(
    event_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """予定を削除"""
    try:
        events = load_schedule_events()
        if event_id not in events:
            return {
                "success": False,
                "message": "予定が見つかりません"
            }
        
        event = events[event_id]
        if event.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        deleted_event = events.pop(event_id)
        save_schedule_events(events)
        
        return {
            "success": True,
            "message": "予定を削除しました",
            "deleted_data": deleted_event
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/status/{event_id}")
async def update_schedule_status(
    event_id: str,
    status: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """予定のステータスを更新"""
    try:
        events = load_schedule_events()
        if event_id not in events:
            return {
                "success": False,
                "message": "予定が見つかりません"
            }
        
        event = events[event_id]
        if event.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        valid_statuses = ["upcoming", "completed", "cancelled"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"無効なステータス: {status}")
        
        event["status"] = status
        event["updated_at"] = datetime.now().isoformat()
        
        save_schedule_events(events)
        
        return {
            "success": True,
            "data": event
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))