"""
CRUD API エンドポイント
Genieのツールから呼び出される基本的なCRUD操作を提供
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
import json

# 一時的なインメモリストレージ（後でデータベースに置き換え）
EFFORT_REPORTS = {}
SCHEDULE_EVENTS = {}
GROWTH_RECORDS = {}
MEMORY_RECORDS = {}
FAMILY_INFO = {}

router = APIRouter(prefix="/api/v1", tags=["crud"])

# ===== データモデル定義 =====

class EffortReportCreate(BaseModel):
    period_days: int
    effort_count: int
    score: float
    highlights: List[str]
    categories: Dict[str, int]
    summary: str
    achievements: List[str]

class ScheduleEventCreate(BaseModel):
    title: str
    date: str
    time: str
    type: str  # vaccination, outing, checkup, other
    location: Optional[str] = None
    description: Optional[str] = None
    status: str = "upcoming"  # upcoming, completed, cancelled
    created_by: str = "genie"

class GrowthRecordCreate(BaseModel):
    child_name: str
    date: str
    age_in_months: int
    type: str  # physical, emotional, cognitive, milestone, photo
    category: str
    title: str
    description: str
    value: Optional[str] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    detected_by: str = "genie"
    confidence: Optional[float] = None
    emotions: Optional[List[str]] = None
    development_stage: Optional[str] = None

class MemoryRecordCreate(BaseModel):
    title: str
    description: str
    date: str
    type: str  # photo, video, album
    category: str  # milestone, daily, family, special
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []
    favorited: bool = False

# ===== 努力レポート CRUD =====

@router.post("/effort-reports")
async def create_effort_report(report: EffortReportCreate):
    """新しい努力レポートを作成"""
    report_id = str(uuid4())
    report_data = {
        "id": report_id,
        **report.dict(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    EFFORT_REPORTS[report_id] = report_data
    return {"success": True, "id": report_id, "data": report_data}

@router.get("/effort-reports")
async def get_effort_reports():
    """努力レポート一覧を取得"""
    return {"success": True, "data": list(EFFORT_REPORTS.values())}

@router.get("/effort-reports/{report_id}")
async def get_effort_report(report_id: str):
    """特定の努力レポートを取得"""
    if report_id not in EFFORT_REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"success": True, "data": EFFORT_REPORTS[report_id]}

@router.put("/effort-reports/{report_id}")
async def update_effort_report(report_id: str, report: EffortReportCreate):
    """努力レポートを更新"""
    if report_id not in EFFORT_REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    
    EFFORT_REPORTS[report_id].update({
        **report.dict(),
        "updated_at": datetime.now().isoformat()
    })
    return {"success": True, "data": EFFORT_REPORTS[report_id]}

@router.delete("/effort-reports/{report_id}")
async def delete_effort_report(report_id: str):
    """努力レポートを削除"""
    if report_id not in EFFORT_REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    
    deleted_report = EFFORT_REPORTS.pop(report_id)
    return {"success": True, "message": "Report deleted successfully", "deleted_data": deleted_report}

# ===== 予定管理 CRUD =====

@router.post("/schedules")
async def create_schedule_event(event: ScheduleEventCreate):
    """新しい予定を作成"""
    event_id = str(uuid4())
    event_data = {
        "id": event_id,
        **event.dict(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    SCHEDULE_EVENTS[event_id] = event_data
    return {"success": True, "id": event_id, "data": event_data}

@router.get("/schedules")
async def get_schedule_events():
    """予定一覧を取得"""
    return {"success": True, "data": list(SCHEDULE_EVENTS.values())}

@router.get("/schedules/{event_id}")
async def get_schedule_event(event_id: str):
    """特定の予定を取得"""
    if event_id not in SCHEDULE_EVENTS:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True, "data": SCHEDULE_EVENTS[event_id]}

@router.put("/schedules/{event_id}")
async def update_schedule_event(event_id: str, event: ScheduleEventCreate):
    """予定を更新"""
    if event_id not in SCHEDULE_EVENTS:
        raise HTTPException(status_code=404, detail="Event not found")
    
    SCHEDULE_EVENTS[event_id].update({
        **event.dict(),
        "updated_at": datetime.now().isoformat()
    })
    return {"success": True, "data": SCHEDULE_EVENTS[event_id]}

@router.delete("/schedules/{event_id}")
async def delete_schedule_event(event_id: str):
    """予定を削除"""
    if event_id not in SCHEDULE_EVENTS:
        raise HTTPException(status_code=404, detail="Event not found")
    
    deleted_event = SCHEDULE_EVENTS.pop(event_id)
    return {"success": True, "message": "Event deleted successfully", "deleted_data": deleted_event}

# ===== 成長記録 CRUD =====

@router.post("/growth-records")
async def create_growth_record(record: GrowthRecordCreate):
    """新しい成長記録を作成"""
    record_id = str(uuid4())
    record_data = {
        "id": record_id,
        **record.dict(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    GROWTH_RECORDS[record_id] = record_data
    return {"success": True, "id": record_id, "data": record_data}

@router.get("/growth-records")
async def get_growth_records():
    """成長記録一覧を取得"""
    return {"success": True, "data": list(GROWTH_RECORDS.values())}

@router.get("/growth-records/{record_id}")
async def get_growth_record(record_id: str):
    """特定の成長記録を取得"""
    if record_id not in GROWTH_RECORDS:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"success": True, "data": GROWTH_RECORDS[record_id]}

@router.put("/growth-records/{record_id}")
async def update_growth_record(record_id: str, record: GrowthRecordCreate):
    """成長記録を更新"""
    if record_id not in GROWTH_RECORDS:
        raise HTTPException(status_code=404, detail="Record not found")
    
    GROWTH_RECORDS[record_id].update({
        **record.dict(),
        "updated_at": datetime.now().isoformat()
    })
    return {"success": True, "data": GROWTH_RECORDS[record_id]}

@router.delete("/growth-records/{record_id}")
async def delete_growth_record(record_id: str):
    """成長記録を削除"""
    if record_id not in GROWTH_RECORDS:
        raise HTTPException(status_code=404, detail="Record not found")
    
    deleted_record = GROWTH_RECORDS.pop(record_id)
    return {"success": True, "message": "Record deleted successfully", "deleted_data": deleted_record}

# ===== メモリー記録 CRUD =====

@router.post("/memories")
async def create_memory_record(memory: MemoryRecordCreate):
    """新しいメモリー記録を作成"""
    memory_id = str(uuid4())
    memory_data = {
        "id": memory_id,
        **memory.dict(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    MEMORY_RECORDS[memory_id] = memory_data
    return {"success": True, "id": memory_id, "data": memory_data}

@router.get("/memories")
async def get_memory_records():
    """メモリー記録一覧を取得"""
    return {"success": True, "data": list(MEMORY_RECORDS.values())}

@router.get("/memories/{memory_id}")
async def get_memory_record(memory_id: str):
    """特定のメモリー記録を取得"""
    if memory_id not in MEMORY_RECORDS:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True, "data": MEMORY_RECORDS[memory_id]}

@router.put("/memories/{memory_id}")
async def update_memory_record(memory_id: str, memory: MemoryRecordCreate):
    """メモリー記録を更新"""
    if memory_id not in MEMORY_RECORDS:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    MEMORY_RECORDS[memory_id].update({
        **memory.dict(),
        "updated_at": datetime.now().isoformat()
    })
    return {"success": True, "data": MEMORY_RECORDS[memory_id]}

@router.delete("/memories/{memory_id}")
async def delete_memory_record(memory_id: str):
    """メモリー記録を削除"""
    if memory_id not in MEMORY_RECORDS:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    deleted_memory = MEMORY_RECORDS.pop(memory_id)
    return {"success": True, "message": "Memory deleted successfully", "deleted_data": deleted_memory}

# ===== ヘルスチェック =====

@router.get("/health")
async def health_check():
    """CRUD API のヘルスチェック"""
    return {
        "success": True,
        "message": "CRUD API is healthy",
        "stats": {
            "effort_reports": len(EFFORT_REPORTS),
            "schedule_events": len(SCHEDULE_EVENTS),
            "growth_records": len(GROWTH_RECORDS),
            "memory_records": len(MEMORY_RECORDS)
        }
    }