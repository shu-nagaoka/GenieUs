"""努力レポート管理API - UseCase Pattern"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.usecases.effort_report_usecase import EffortReportUseCase
from src.presentation.api.dependencies import get_effort_report_usecase

router = APIRouter(prefix="/effort-reports", tags=["effort_reports"])


class EffortReportCreateRequest(BaseModel):
    """努力レポート作成リクエスト"""

    period_days: int
    effort_count: int
    score: float
    highlights: list[str]
    categories: dict[str, int]
    summary: str
    achievements: list[str]
    user_id: str = "frontend_user"


class EffortReportUpdateRequest(BaseModel):
    """努力レポート更新リクエスト"""

    period_days: int | None = None
    effort_count: int | None = None
    score: float | None = None
    highlights: list[str] | None = None
    categories: dict[str, int] | None = None
    summary: str | None = None
    achievements: list[str] | None = None
    user_id: str = "frontend_user"


@router.post("/create")
async def create_effort_report(
    request: EffortReportCreateRequest,
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """努力レポートを作成"""
    try:
        request_data = request.model_dump()
        user_id = request_data.get("user_id", "frontend_user")

        result = await effort_report_usecase.create_effort_report(user_id=user_id, report_data=request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_effort_reports(
    user_id: str = "frontend_user",
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """努力レポート一覧を取得"""
    try:
        result = await effort_report_usecase.get_effort_reports(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{report_id}")
async def get_effort_report(
    report_id: str,
    user_id: str = "frontend_user",
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """特定の努力レポートを取得"""
    try:
        result = await effort_report_usecase.get_effort_report(user_id, report_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{report_id}")
async def update_effort_report(
    report_id: str,
    request: EffortReportUpdateRequest,
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """努力レポートを更新"""
    try:
        request_data = request.model_dump(exclude_unset=True)
        user_id = request_data.get("user_id", "frontend_user")

        result = await effort_report_usecase.update_effort_report(
            user_id=user_id,
            report_id=report_id,
            update_data=request_data,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{report_id}")
async def delete_effort_report(
    report_id: str,
    user_id: str = "frontend_user",
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """努力レポートを削除"""
    try:
        result = await effort_report_usecase.delete_effort_report(user_id, report_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_effort_report(
    user_id: str = "frontend_user",
    period_days: int = 7,
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """努力レポートを自動生成"""
    try:
        result = await effort_report_usecase.generate_effort_report(user_id=user_id, period_days=period_days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_effort_report(
    user_id: str = "frontend_user",
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """最新の努力レポートを取得"""
    try:
        reports_result = await effort_report_usecase.get_effort_reports(user_id)

        if reports_result.get("success") and reports_result.get("data"):
            # 最新のレポートを返す（リストの最初の要素）
            latest_report = reports_result["data"][0]
            return {"success": True, "data": latest_report}
        else:
            return {"success": False, "message": "努力レポートが見つかりません"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_effort_stats(
    user_id: str = "frontend_user",
    effort_report_usecase: EffortReportUseCase = Depends(get_effort_report_usecase),
) -> dict[str, Any]:
    """努力統計情報を取得"""
    try:
        reports_result = await effort_report_usecase.get_effort_reports(user_id)

        if not reports_result.get("success"):
            return reports_result

        reports = reports_result.get("data", [])

        if not reports:
            return {"success": True, "data": {"total_reports": 0, "average_score": 0.0, "total_efforts": 0}}

        # 統計計算
        total_reports = len(reports)
        total_score = sum(report.get("score", 0) for report in reports)
        average_score = total_score / total_reports if total_reports > 0 else 0.0
        total_efforts = sum(report.get("effort_count", 0) for report in reports)

        return {
            "success": True,
            "data": {
                "total_reports": total_reports,
                "average_score": round(average_score, 1),
                "total_efforts": total_efforts,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
