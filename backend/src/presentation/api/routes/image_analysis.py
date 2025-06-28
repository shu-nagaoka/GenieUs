"""画像解析 API

子育て記録用画像解析エンドポイント

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- FastAPI Depends統合パターン
- 段階的エラーハンドリング
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase
from src.presentation.api.dependencies import get_image_analysis_usecase, get_logger

router = APIRouter(prefix="/api/v1/image-analysis", tags=["image_analysis"])


class ImageAnalysisRequest(BaseModel):
    """画像解析リクエスト"""

    image_path: str
    child_id: str = "default_child"
    analysis_context: dict[str, Any] | None = None


class ImageAnalysisResponse(BaseModel):
    """画像解析レスポンス"""

    success: bool
    child_id: str
    detected_items: list[str]
    confidence: float
    suggestions: list[str]
    emotion_detected: str
    activity_type: str
    extracted_events: list[dict[str, Any]]
    safety_concerns: list[str] | None = None
    has_safety_concerns: bool
    timestamp: str | None = None
    ai_model: str | None = None
    error: str | None = None


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_child_image(
    request: ImageAnalysisRequest,
    image_analysis_usecase: ImageAnalysisUseCase = Depends(get_image_analysis_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """子どもの画像を分析してデータを抽出

    Args:
        request: 画像解析リクエスト
        image_analysis_usecase: 画像解析UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        ImageAnalysisResponse: 分析結果

    """
    try:
        logger.info(f"画像解析API開始: child_id={request.child_id}, image_path={request.image_path}")

        # UseCase実行
        result = await image_analysis_usecase.analyze_child_image(
            image_path=request.image_path,
            child_id=request.child_id,
            analysis_context=request.analysis_context,
        )

        logger.info(f"画像解析API完了: child_id={request.child_id}, success={result.get('success', True)}")

        return ImageAnalysisResponse(**result)

    except Exception as e:
        logger.error(f"画像解析API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"画像解析中にエラーが発生しました: {e!s}")


@router.post("/analyze/upload", response_model=ImageAnalysisResponse)
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    child_id: str = Form(default="default_child"),
    analysis_type: str = Form(default="general"),
    image_analysis_usecase: ImageAnalysisUseCase = Depends(get_image_analysis_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """アップロードされた画像を直接分析

    Args:
        file: アップロードファイル
        child_id: 子どものID
        analysis_type: 分析タイプ
        image_analysis_usecase: 画像解析UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        ImageAnalysisResponse: 分析結果

    """
    try:
        logger.info(f"画像アップロード分析API開始: child_id={child_id}, filename={file.filename}")

        # ファイル形式チェック
        if not file.filename or not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            raise HTTPException(
                status_code=400,
                detail="サポートされていないファイル形式です。PNG、JPG、JPEG、GIF、WebPのみ対応しています。",
            )

        # ファイルサイズチェック
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="ファイルサイズが5MBを超えています。")

        # 一時的にファイルを保存
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # UseCase実行
            result = await image_analysis_usecase.analyze_child_image(
                image_path=temp_file_path,
                child_id=child_id,
                analysis_context={"analysis_type": analysis_type},
            )

            logger.info(f"画像アップロード分析API完了: child_id={child_id}, success={result.get('success', True)}")

            return ImageAnalysisResponse(**result)

        finally:
            # 一時ファイルを削除
            try:
                os.unlink(temp_file_path)
            except OSError:
                logger.warning(f"一時ファイルの削除に失敗: {temp_file_path}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"画像アップロード分析API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"画像分析中にエラーが発生しました: {e!s}")


@router.get("/health")
async def health_check(
    logger: logging.Logger = Depends(get_logger),
):
    """画像解析サービスのヘルスチェック"""
    logger.info("画像解析API ヘルスチェック")
    return {
        "service": "image_analysis",
        "status": "healthy",
        "endpoints": [
            "/api/v1/image-analysis/analyze",
            "/api/v1/image-analysis/analyze/upload",
            "/api/v1/image-analysis/health",
        ],
    }
