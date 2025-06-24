"""努力レポート管理API"""

import json
import os
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

# データファイルのパス
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
EFFORT_REPORTS_FILE = DATA_DIR / "effort_reports.json"

def load_effort_reports() -> Dict[str, Any]:
    """努力レポートデータを読み込み"""
    if EFFORT_REPORTS_FILE.exists():
        with open(EFFORT_REPORTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_effort_reports(data: Dict[str, Any]) -> None:
    """努力レポートデータを保存"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(EFFORT_REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

router = APIRouter(prefix="/effort-reports", tags=["effort_reports"])


class EffortReportCreateRequest(BaseModel):
    """努力レポート作成リクエスト"""
    period_days: int
    effort_count: int
    score: float
    highlights: List[str]
    categories: Dict[str, int]
    summary: str
    achievements: List[str]
    user_id: str = "frontend_user"


class EffortReportUpdateRequest(BaseModel):
    """努力レポート更新リクエスト"""
    period_days: Optional[int] = None
    effort_count: Optional[int] = None
    score: Optional[float] = None
    highlights: Optional[List[str]] = None
    categories: Optional[Dict[str, int]] = None
    summary: Optional[str] = None
    achievements: Optional[List[str]] = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_effort_report(
    request: EffortReportCreateRequest,
) -> Dict[str, Any]:
    """努力レポートを作成"""
    try:
        reports = load_effort_reports()
        report_id = str(uuid4())
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")
        
        report_data = {
            "id": report_id,
            "user_id": user_id,
            **request_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        reports[report_id] = report_data
        save_effort_reports(reports)
        
        return {
            "success": True,
            "id": report_id,
            "data": report_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_effort_reports(
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """努力レポート一覧を取得"""
    try:
        reports = load_effort_reports()
        user_reports = [
            report for report in reports.values()
            if report.get("user_id") == user_id
        ]
        
        return {
            "success": True,
            "data": user_reports
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{report_id}")
async def get_effort_report(
    report_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """特定の努力レポートを取得"""
    try:
        reports = load_effort_reports()
        if report_id not in reports:
            return {
                "success": False,
                "message": "努力レポートが見つかりません"
            }
        
        report = reports[report_id]
        if report.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        return {
            "success": True,
            "data": report
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{report_id}")
async def update_effort_report(
    report_id: str,
    request: EffortReportUpdateRequest,
) -> Dict[str, Any]:
    """努力レポートを更新"""
    try:
        reports = load_effort_reports()
        if report_id not in reports:
            return {
                "success": False,
                "message": "努力レポートが見つかりません"
            }
        
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")
        
        report = reports[report_id]
        if report.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        # 更新データをマージ
        report.update({
            **request_data,
            "updated_at": datetime.now().isoformat()
        })
        
        save_effort_reports(reports)
        
        return {
            "success": True,
            "data": report
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{report_id}")
async def delete_effort_report(
    report_id: str,
    user_id: str = "frontend_user",
) -> Dict[str, Any]:
    """努力レポートを削除"""
    try:
        reports = load_effort_reports()
        if report_id not in reports:
            return {
                "success": False,
                "message": "努力レポートが見つかりません"
            }
        
        report = reports[report_id]
        if report.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
        
        deleted_report = reports.pop(report_id)
        save_effort_reports(reports)
        
        return {
            "success": True,
            "message": "努力レポートを削除しました",
            "deleted_data": deleted_report
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))