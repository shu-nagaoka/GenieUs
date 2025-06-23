import logging
import subprocess
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.di_provider.factory import get_container
from src.presentation.api.routes import health_router
from src.presentation.api.routes.multiagent_chat import router as multiagent_chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時処理
    temp_logger = logging.getLogger(__name__)
    temp_logger.info("FastAPI application starting...")

    # 🔧 DIコンテナー・AgentManager初期化（アプリケーション全体で1度だけ）
    try:
        # DIコンテナの初期化
        container = get_container()
        logger = container.logger()
        logger.info("✅ DIコンテナー初期化完了")

        # AgentManagerによる一元管理開始（直接作成）
        from src.agents.agent_manager import AgentManager

        agent_manager = AgentManager(container)
        agent_manager.initialize_all_agents()
        logger.info("✅ AgentManager初期化完了（個別エージェント + マルチエージェントパイプライン）")

        # FastAPIアプリにコンテナとAgentManagerを関連付け
        app.container = container
        app.agent_manager = agent_manager
        logger.info("✅ FastAPIアプリ関連付け完了")

        # DI統合ルーターのワイヤリング設定
        container.wire(
            modules=[
                "src.presentation.api.routes.multiagent_chat",  # マルチエージェントチャット
            ],
        )
        logger.info("✅ DI統合ルーターワイヤリング完了")

    except Exception as e:
        temp_logger.error(f"❌ アプリケーション初期化失敗: {e}")
        raise

    yield

    # 終了時処理
    temp_logger.info("FastAPI application shutting down...")


# ADKファースト: シンプルなFastAPIアプリケーション
app = FastAPI(
    title="GenieUs API v2.0",
    description="「見えない成長に、光をあてる。不安な毎日を、自信に変える。」- Google ADK powered 次世代子育て支援 API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS設定（フロントエンド連携用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js開発サーバー
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MVP必要最低限のルーター登録
app.include_router(health_router, prefix="/api/v1", tags=["health"])

# 🤖 マルチエージェントチャットルーター（agent-to-agentルーティング）
app.include_router(multiagent_chat_router, prefix="/api/v1/multiagent", tags=["multiagent"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """グローバル例外ハンドラー（DEVELOPMENT_GUIDELINES.md準拠）"""
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
        "docs": "/docs",
        "available_endpoints": {
            "health": "/api/v1/health",
            "multiagent_chat": "/api/v1/multiagent/chat",
        },
        "v2_endpoints": {
            "comprehensive_consultation": "/api/v1/consultation",
            "pipeline_info": "/api/v1/consultation/pipelines",
            "system_info": "/api/v1/consultation/system-info",
        },
        "note": "シンプル版では健康チェックとマルチエージェント相談機能のみ提供しています",
    }


def start_adk_web():
    """ADK Web UIを起動"""
    temp_logger = logging.getLogger(__name__)
    temp_logger.info("Starting ADK Web UI on port 8001...")
    try:
        subprocess.run([sys.executable, "-m", "google.adk", "web", "--port", "8001"], check=True)
    except subprocess.CalledProcessError as e:
        temp_logger.error(f"Failed to start ADK Web UI: {e}")
    except KeyboardInterrupt:
        temp_logger.info("ADK Web UI stopped by user")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "adk":
        # ADK Web UI起動
        start_adk_web()
    else:
        # FastAPI起動
        uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
