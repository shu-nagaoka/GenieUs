"""音声解析 API

子育て記録用音声解析エンドポイント

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

from src.application.usecases.voice_analysis_usecase import VoiceAnalysisUseCase
from src.presentation.api.dependencies import get_logger, get_voice_analysis_usecase

router = APIRouter(prefix="/api/v1/voice-analysis", tags=["voice_analysis"])


class VoiceAnalysisRequest(BaseModel):
    """音声解析リクエスト"""

    voice_text: str
    child_id: str = "default_child"
    analysis_context: dict[str, Any] | None = None


class VoiceEventData(BaseModel):
    """音声イベントデータ"""

    type: str
    description: str
    time: str | None = None
    confidence: float
    details: dict[str, Any] | None = None


class VoiceAnalysisResponse(BaseModel):
    """音声解析レスポンス"""

    success: bool
    child_id: str
    events: list[VoiceEventData]
    overall_confidence: float
    insights: list[str]
    emotional_tone: str
    timestamp: str | None = None
    ai_model: str | None = None
    error: str | None = None


@router.post("/analyze", response_model=VoiceAnalysisResponse)
async def analyze_child_voice(
    request: VoiceAnalysisRequest,
    voice_analysis_usecase: VoiceAnalysisUseCase = Depends(get_voice_analysis_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """子どもの音声テキストを分析してデータを抽出

    Args:
        request: 音声解析リクエスト
        voice_analysis_usecase: 音声解析UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        VoiceAnalysisResponse: 分析結果

    """
    try:
        logger.info(f"音声解析API開始: child_id={request.child_id}, text_length={len(request.voice_text)}")

        if not request.voice_text.strip():
            raise HTTPException(status_code=400, detail="音声テキストが空です。")

        # UseCase実行
        result = await voice_analysis_usecase.analyze_child_voice(
            voice_text=request.voice_text,
            child_id=request.child_id,
            analysis_context=request.analysis_context,
        )

        logger.info(f"音声解析API完了: child_id={request.child_id}, success={result.get('success', True)}")

        # イベントデータの変換
        events = []
        for event_data in result.get("events", []):
            events.append(VoiceEventData(**event_data))

        return VoiceAnalysisResponse(
            success=result.get("success", True),
            child_id=result["child_id"],
            events=events,
            overall_confidence=result["overall_confidence"],
            insights=result["insights"],
            emotional_tone=result["emotional_tone"],
            timestamp=result.get("timestamp"),
            ai_model=result.get("ai_model"),
            error=result.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"音声解析API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"音声解析中にエラーが発生しました: {e!s}")


@router.post("/analyze/upload", response_model=VoiceAnalysisResponse)
async def analyze_uploaded_voice(
    file: UploadFile = File(...),
    child_id: str = Form(default="default_child"),
    analysis_type: str = Form(default="general"),
    voice_analysis_usecase: VoiceAnalysisUseCase = Depends(get_voice_analysis_usecase),
    logger: logging.Logger = Depends(get_logger),
):
    """アップロードされた音声ファイルを直接分析（※音声認識機能は未実装）

    Args:
        file: アップロード音声ファイル
        child_id: 子どものID
        analysis_type: 分析タイプ
        voice_analysis_usecase: 音声解析UseCase（DI注入）
        logger: ロガー（DI注入）

    Returns:
        VoiceAnalysisResponse: 分析結果

    """
    try:
        logger.info(f"音声ファイル分析API開始: child_id={child_id}, filename={file.filename}")

        # ファイル形式チェック
        if not file.filename or not file.filename.lower().endswith((".wav", ".mp3", ".m4a", ".flac", ".ogg")):
            raise HTTPException(
                status_code=400,
                detail="サポートされていないファイル形式です。WAV、MP3、M4A、FLAC、OGGのみ対応しています。",
            )

        # ファイルサイズチェック
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="ファイルサイズが10MBを超えています。")

        # 現在は音声認識機能が未実装のため、ダミーレスポンスを返す
        logger.warning("音声認識機能は未実装です。ダミーレスポンスを返します。")

        dummy_result = {
            "success": True,
            "child_id": child_id,
            "events": [
                {
                    "type": "voice_upload",
                    "description": f"音声ファイル '{file.filename}' がアップロードされました",
                    "time": "now",
                    "confidence": 0.8,
                    "details": {
                        "file_size": len(file_content),
                        "file_name": file.filename,
                        "status": "音声認識機能は開発中です",
                    },
                },
            ],
            "overall_confidence": 0.5,
            "insights": [
                "音声ファイルのアップロードが完了しました",
                "音声認識機能は現在開発中です",
                "将来的には自動的に音声をテキストに変換し、詳細な分析を提供予定です",
            ],
            "emotional_tone": "neutral",
            "timestamp": None,
            "ai_model": "development_placeholder",
        }

        # イベントデータの変換
        events = []
        for event_data in dummy_result.get("events", []):
            events.append(VoiceEventData(**event_data))

        return VoiceAnalysisResponse(
            success=dummy_result["success"],
            child_id=dummy_result["child_id"],
            events=events,
            overall_confidence=dummy_result["overall_confidence"],
            insights=dummy_result["insights"],
            emotional_tone=dummy_result["emotional_tone"],
            timestamp=dummy_result.get("timestamp"),
            ai_model=dummy_result.get("ai_model"),
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"音声ファイル分析API実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"音声ファイル分析中にエラーが発生しました: {e!s}")


@router.get("/health")
async def health_check(
    logger: logging.Logger = Depends(get_logger),
):
    """音声解析サービスのヘルスチェック"""
    logger.info("音声解析API ヘルスチェック")
    return {
        "service": "voice_analysis",
        "status": "healthy",
        "features": {"text_analysis": "available", "voice_recognition": "under_development"},
        "endpoints": [
            "/api/v1/voice-analysis/analyze",
            "/api/v1/voice-analysis/analyze/upload",
            "/api/v1/voice-analysis/health",
        ],
    }
