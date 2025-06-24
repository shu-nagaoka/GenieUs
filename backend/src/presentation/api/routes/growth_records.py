"""成長記録管理API"""

import json
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

# データファイルのパス
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
GROWTH_RECORDS_FILE = DATA_DIR / "growth_records.json"

def load_growth_records() -> Dict[str, Any]:
    """成長記録データを読み込み"""
    if GROWTH_RECORDS_FILE.exists():
        with open(GROWTH_RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_growth_records(data: Dict[str, Any]) -> None:
    """成長記録データを保存"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(GROWTH_RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

router = APIRouter(prefix="/growth-records", tags=["growth_records"])


class GrowthRecordCreateRequest(BaseModel):
    """成長記録作成リクエスト"""
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
    user_id: str = "frontend_user"


class GrowthRecordUpdateRequest(BaseModel):
    """成長記録更新リクエスト"""
    child_name: Optional[str] = None
    date: Optional[str] = None
    age_in_months: Optional[int] = None
    type: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    detected_by: Optional[str] = None
    confidence: Optional[float] = None
    emotions: Optional[List[str]] = None
    development_stage: Optional[str] = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_growth_record(
    request: GrowthRecordCreateRequest,
) -> Dict[str, Any]:
    """成長記録を作成"""
    try:
        records = load_growth_records()
        record_id = str(uuid4())
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")
        
        record_data = {
            "id": record_id,
            "user_id": user_id,
            **request_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        records[record_id] = record_data
        save_growth_records(records)
        
        return {
            "success": True,
            "id": record_id,
            "data": record_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_growth_records(
    user_id: str = "frontend_user",
    child_name: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """成長記録一覧を取得"""
    try:
        records = load_growth_records()
        user_records = [
            record for record in records.values()
            if record.get("user_id") == user_id
        ]
        
        # 子供の名前でフィルタリング
        if child_name:
            user_records = [
                record for record in user_records
                if record.get("child_name") == child_name
            ]
        
        # タイプでフィルタリング
        if type:
            user_records = [
                record for record in user_records
                if record.get("type") == type
            ]
        
        # カテゴリでフィルタリング
        if category:
            user_records = [
                record for record in user_records
                if record.get("category") == category
            ]
        
        # 日付でソート（新しい順）
        user_records.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "success": True,
            "data": user_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{record_id}")
async def get_growth_record(
    record_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """特定の成長記録を取得"""
    try:
        records = load_growth_records()
        if record_id not in records:
            return {
                "success": False,
                "message": "成長記録が見つかりません"
            }
        
        record = records[record_id]
        if record.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        return {
            "success": True,
            "data": record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{record_id}")
async def update_growth_record(
    record_id: str,
    request: GrowthRecordUpdateRequest,
) -> Dict[str, Any]:
    """成長記録を更新"""
    try:
        records = load_growth_records()
        if record_id not in records:
            return {
                "success": False,
                "message": "成長記録が見つかりません"
            }
        
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")
        
        record = records[record_id]
        if record.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        # 更新データをマージ
        record.update({
            **request_data,
            "updated_at": datetime.now().isoformat()
        })
        
        save_growth_records(records)
        
        return {
            "success": True,
            "data": record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{record_id}")
async def delete_growth_record(
    record_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """成長記録を削除"""
    try:
        records = load_growth_records()
        if record_id not in records:
            return {
                "success": False,
                "message": "成長記録が見つかりません"
            }
        
        record = records[record_id]
        if record.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        deleted_record = records.pop(record_id)
        save_growth_records(records)
        
        return {
            "success": True,
            "message": "成長記録を削除しました",
            "deleted_data": deleted_record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/milestones")
async def get_milestones(
    user_id: str = "frontend_user",
    child_name: Optional[str] = None,
) -> Dict[str, Any]:
    """マイルストーン記録を取得"""
    try:
        records = load_growth_records()
        user_records = [
            record for record in records.values()
            if record.get("user_id") == user_id and record.get("type") == "milestone"
        ]
        
        # 子供の名前でフィルタリング
        if child_name:
            user_records = [
                record for record in user_records
                if record.get("child_name") == child_name
            ]
        
        # 日付でソート（新しい順）
        user_records.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "success": True,
            "data": user_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_growth_timeline(
    user_id: str = "frontend_user",
    child_name: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """成長タイムラインを取得"""
    try:
        records = load_growth_records()
        user_records = [
            record for record in records.values()
            if record.get("user_id") == user_id
        ]
        
        # 子供の名前でフィルタリング
        if child_name:
            user_records = [
                record for record in user_records
                if record.get("child_name") == child_name
            ]
        
        # 日付でソート（新しい順）
        user_records.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # 制限を適用
        if limit:
            user_records = user_records[:limit]
        
        return {
            "success": True,
            "data": user_records,
            "total_count": len(user_records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))