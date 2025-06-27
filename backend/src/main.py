import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.agents.agent_manager import AgentManager
from src.di_provider.composition_root import CompositionRootFactory
from src.presentation.api.routes.admin import router as admin_router
from src.presentation.api.routes.agents import router as agents_router
from src.presentation.api.routes.auth import router as auth_router
from src.presentation.api.routes.effort_reports import router as effort_reports_router
from src.presentation.api.routes.family import router as family_router
from src.presentation.api.routes.file_upload import router as file_upload_router
from src.presentation.api.routes.growth_records import router as growth_records_router
from src.presentation.api.routes.meal_plans import router as meal_plans_router
from src.presentation.api.routes.memories import router as memories_router
from src.presentation.api.routes.schedules import router as schedules_router
from src.presentation.api.routes.streaming_chat import router as streaming_chat_router


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

        # AgentManagerに必要なツールとルーティング戦略を注入
        all_tools = composition_root.get_all_tools()
        routing_strategy = composition_root.get_routing_strategy()
        agent_manager = AgentManager(
            tools=all_tools,
            logger=logger,
            settings=composition_root.settings,
            routing_strategy=routing_strategy,
        )
        agent_manager.initialize_all_components()
        logger.info("✅ AgentManager初期化完了（Pure Composition Root + ルーティング戦略）")

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

# CORS設定（動的ポート対応）
def get_cors_origins():
    """環境変数からCORS許可オリジンを動的に構築"""
    origins = []

    # デフォルトオリジン
    default_origins = ["http://localhost:3000", "http://localhost:3001"]
    origins.extend(default_origins)

    # 環境変数で追加オリジンを指定可能
    if os.getenv("CORS_ORIGINS"):
        additional_origins = os.getenv("CORS_ORIGINS").split(",")
        origins.extend([origin.strip() for origin in additional_origins])

    # フロントエンドポートが環境変数で指定されている場合
    frontend_port = os.getenv("FRONTEND_PORT")
    if frontend_port:
        origins.append(f"http://localhost:{frontend_port}")

    return list(set(origins))  # 重複除去

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌊 ストリーミングチャットルーター（リアルタイム進捗表示）
app.include_router(streaming_chat_router, tags=["streaming"])

# 👨‍👩‍👧‍👦 家族情報管理ルーター
app.include_router(family_router, prefix="/api", tags=["family"])

# 📊 CRUD機能ルーター（Genieツール連携用）
app.include_router(effort_reports_router, prefix="/api", tags=["effort_reports"])
app.include_router(schedules_router, prefix="/api", tags=["schedules"])
app.include_router(growth_records_router, prefix="/api", tags=["growth_records"])
app.include_router(memories_router, prefix="/api", tags=["memories"])
app.include_router(file_upload_router, prefix="/api", tags=["files"])

# 🍽️ 食事プラン管理ルーター
app.include_router(meal_plans_router, prefix="/api", tags=["meal_plans"])

# 🔐 認証ルーター
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# 🛠️ 管理者ルーター
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])

# 🤖 エージェント情報ルーター
app.include_router(agents_router, prefix="/api", tags=["agents"])


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
    # 環境変数からポート設定を取得（デフォルト: 8000）
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    log_level = os.getenv("LOG_LEVEL", "info")
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"🚀 Starting FastAPI server on {host}:{port}")
    print(f"📡 CORS Origins: {get_cors_origins()}")

    # FastAPIサーバー起動
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )
