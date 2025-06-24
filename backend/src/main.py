import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.di_provider.composition_root import CompositionRootFactory
from src.presentation.api.routes.multiagent_chat import router as multiagent_chat_router
from src.presentation.api.routes.streaming_chat import router as streaming_chat_router
from src.presentation.api.routes.family import router as family_router
from src.presentation.api.routes.effort_reports import router as effort_reports_router
from src.presentation.api.routes.schedules import router as schedules_router
from src.presentation.api.routes.growth_records import router as growth_records_router
from src.presentation.api.routes.memories import router as memories_router
from src.presentation.api.routes.file_upload import router as file_upload_router
from src.agents.agent_manager import AgentManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理 - Pure CompositionRoot Pattern"""
    # 起動時処理
    temp_logger = logging.getLogger(__name__)
    temp_logger.info("FastAPI application starting...")

    # 🎯 CompositionRoot一元初期化（アプリケーション全体で1度だけ）
    try:
        composition_root = CompositionRootFactory.create()
        logger = composition_root.logger
        logger.info("✅ CompositionRoot初期化完了")

        # AgentManagerに必要なツールのみ注入
        all_tools = composition_root.get_all_tools()
        agent_manager = AgentManager(tools=all_tools, logger=logger, settings=composition_root.settings)
        agent_manager.initialize_all_components()
        logger.info("✅ AgentManager初期化完了（Pure Composition Root）")

        # FastAPIアプリには必要なコンポーネントのみ注入
        app.agent_manager = agent_manager
        app.logger = logger
        app.composition_root = composition_root  # 家族管理UseCaseアクセス用
        logger.info("✅ FastAPIアプリ関連付け完了（Pure CompositionRoot）")

    except Exception as e:
        temp_logger.error(f"❌ アプリケーション初期化失敗: {e}")
        raise

    yield

    # 終了時処理
    temp_logger.info("FastAPI application shutting down...")


# FastAPIアプリケーション作成
app = FastAPI(
    title="GenieUs API",
    description="見えない成長に、光をあてる。不安な毎日を、自信に変える。",
    version="1.0.0-mvp",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MVP必要最低限のルーター登録
# app.include_router(health_router, prefix="/api/v1", tags=["health"])

# 🤖 マルチエージェントチャットルーター（CompositionRoot統合）
app.include_router(multiagent_chat_router, prefix="/api/v1/multiagent", tags=["multiagent"])

# 🌊 ストリーミングチャットルーター（リアルタイム進捗表示）
app.include_router(streaming_chat_router, prefix="/api/v1/streaming", tags=["streaming"])

# 👨‍👩‍👧‍👦 家族情報管理ルーター
app.include_router(family_router, prefix="/api/v1", tags=["family"])

# 📊 CRUD機能ルーター（Genieツール連携用）
app.include_router(effort_reports_router, prefix="/api/v1", tags=["effort_reports"])
app.include_router(schedules_router, prefix="/api/v1", tags=["schedules"])
app.include_router(growth_records_router, prefix="/api/v1", tags=["growth_records"])
app.include_router(memories_router, prefix="/api/v1", tags=["memories"])
app.include_router(file_upload_router, tags=["files"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """グローバル例外ハンドラー（Pure CompositionRoot）"""
    # 注入されたロガーを取得
    if hasattr(request.app, "logger"):
        logger = request.app.logger
        logger.error(f"Unhandled exception at {request.url.path}: {exc}")
    else:
        temp_logger = logging.getLogger(__name__)
        temp_logger.error(f"Unhandled exception at {request.url.path}: {exc}")

    return JSONResponse(
        status_code=500,
        content={"error": "内部サーバーエラーが発生しました", "message": "しばらく時間をおいて再度お試しください"},
    )


@app.get("/")
async def root():
    """ルートエンドポイント（MVP版）"""
    return {
        "message": "GenieUs API - MVP版 - 見えない成長に、光をあてる。",
        "status": "running",
        "version": "1.0.0-mvp",
        "architecture": "Pure CompositionRoot Pattern",
        "docs": "/docs",
        "available_endpoints": {
            "multiagent_chat": "/api/v1/multiagent/chat",
            "streaming_chat": "/api/v1/streaming/streaming-chat",
            "family_register": "/api/v1/family/register",
            "family_info": "/api/v1/family/info",
            "family_update": "/api/v1/family/update",
            "family_delete": "/api/v1/family/delete",
            "effort_reports_crud": "/api/v1/effort-reports/*",
            "schedules_crud": "/api/v1/schedules/*",
            "growth_records_crud": "/api/v1/growth-records/*",
            "memories_crud": "/api/v1/memories/*",
        },
    }


if __name__ == "__main__":
    # FastAPIサーバー起動
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
