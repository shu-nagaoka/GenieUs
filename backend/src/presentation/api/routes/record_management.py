"""記録管理 API

子育て記録管理エンドポイント

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- FastAPI Depends統合パターン
- 段階的エラーハンドリング
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.application.usecases.record_management_usecase import RecordManagementUseCase
from src.presentation.api.dependencies import get_logger, get_record_management_usecase

router = APIRouter(prefix="/api/v1/record-management", tags=["record_management"])


class RecordSaveRequest(BaseModel):
    """記録保存リクエスト"""

    child_id: str
    event_type: str
    description: str
    metadata: dict[str, Any] | None = None


class RecordData(BaseModel):
    """記録データ"""

    id: str
    event_type: str
    description: str
    timestamp: str
    metadata: dict[str, Any] | None = None
    days_ago: int


class RecordSaveResponse(BaseModel):
    """記録保存レスポンス"""

    success: bool
    record_id: str | None = None
    child_id: str | None = None
    event_type: str | None = None
    timestamp: str | None = None
    error: str | None = None


class RecordListResponse(BaseModel):
    """記録一覧レスポンス"""

    success: bool
    child_id: str
    records: list[RecordData]
    total_count: int
    filter_event_type: str | None = None
    days_back: int
    error: str | None = None


class PatternData(BaseModel):
    """パターンデータ"""

    pattern: str
    confidence: float
    confidence_level: str
    interpretation: str


class PatternAnalysisResponse(BaseModel):
    """パターン分析レスポンス"""

    success: bool
    child_id: str
    analysis_period_days: int
    patterns: list[PatternData]
    pattern_count: int
    error: str | None = None


@router.post("/save", response_model=RecordSaveResponse)
async def save_child_record(
    request: RecordSaveRequest,
    record_management_usecase: RecordManagementUseCase = Depends(get_record_management_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """子どもの記録を保存

    Args:
        request: 記録保存リクエスト
        record_management_usecase: 記録管理UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        RecordSaveResponse: 保存結果

    """
    try:
        logger.info(f"記録保存API開始: child_id={request.child_id}, event_type={request.event_type}")

        if not request.description.strip():
            raise HTTPException(status_code=400, detail="記録の説明が空です。")

        # UseCase実行
        result = await record_management_usecase.save_child_record(
            child_id=request.child_id,
            event_type=request.event_type,
            description=request.description,
            metadata=request.metadata,
        )

        logger.info(f"記録保存API完了: child_id={request.child_id}, success={result.get('success', False)}")

        return RecordSaveResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"記録保存API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"記録保存中にエラーが発生しました: {e!s}")


@router.get("/records/{child_id}", response_model=RecordListResponse)
async def get_child_records(
    child_id: str,
    event_type: str | None = Query(None, description="フィルターするイベントタイプ"),
    days_back: int = Query(7, description="取得する過去の日数", ge=1, le=365),
    limit: int = Query(50, description="最大取得数", ge=1, le=1000),
    record_management_usecase: RecordManagementUseCase = Depends(get_record_management_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """子どもの記録を取得

    Args:
        child_id: 子どものID
        event_type: フィルターするイベントタイプ（オプション）
        days_back: 取得する過去の日数
        limit: 最大取得数
        record_management_usecase: 記録管理UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        RecordListResponse: 記録一覧

    """
    try:
        logger.info(f"記録取得API開始: child_id={child_id}, event_type={event_type}, days_back={days_back}")

        # UseCase実行
        result = await record_management_usecase.get_child_records(
            child_id=child_id,
            event_type=event_type,
            days_back=days_back,
            limit=limit,
        )

        logger.info(f"記録取得API完了: child_id={child_id}, count={result.get('total_count', 0)}")

        # レスポンスデータの変換
        records = []
        for record_data in result.get("records", []):
            records.append(RecordData(**record_data))

        return RecordListResponse(
            success=result.get("success", True),
            child_id=result["child_id"],
            records=records,
            total_count=result["total_count"],
            filter_event_type=result.get("filter_event_type"),
            days_back=result["days_back"],
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"記録取得API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"記録取得中にエラーが発生しました: {e!s}")


@router.get("/patterns/{child_id}", response_model=PatternAnalysisResponse)
async def get_record_patterns(
    child_id: str,
    analysis_days: int = Query(30, description="分析対象の日数", ge=7, le=365),
    record_management_usecase: RecordManagementUseCase = Depends(get_record_management_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """記録パターンの分析

    Args:
        child_id: 子どものID
        analysis_days: 分析対象の日数
        record_management_usecase: 記録管理UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        PatternAnalysisResponse: パターン分析結果

    """
    try:
        logger.info(f"パターン分析API開始: child_id={child_id}, analysis_days={analysis_days}")

        # UseCase実行
        result = await record_management_usecase.get_record_patterns(
            child_id=child_id,
            analysis_days=analysis_days,
        )

        logger.info(f"パターン分析API完了: child_id={child_id}, pattern_count={result.get('pattern_count', 0)}")

        # レスポンスデータの変換
        patterns = []
        for pattern_data in result.get("patterns", []):
            patterns.append(PatternData(**pattern_data))

        return PatternAnalysisResponse(
            success=result.get("success", True),
            child_id=result["child_id"],
            analysis_period_days=result["analysis_period_days"],
            patterns=patterns,
            pattern_count=result["pattern_count"],
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"パターン分析API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"パターン分析中にエラーが発生しました: {e!s}")


@router.get("/health")
async def health_check(
    logger: logging.Logger = Depends(get_logger),
):
    """記録管理サービスのヘルスチェック"""
    logger.info("記録管理API ヘルスチェック")
    return {
        "service": "record_management",
        "status": "healthy",
        "features": {"record_save": "available", "record_retrieval": "available", "pattern_analysis": "available"},
        "supported_event_types": ["feeding", "sleep", "mood", "activity", "milestone", "other"],
        "endpoints": [
            "/api/v1/record-management/save",
            "/api/v1/record-management/records/{child_id}",
            "/api/v1/record-management/patterns/{child_id}",
            "/api/v1/record-management/health",
        ],
    }
