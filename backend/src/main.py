import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
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
from src.presentation.api.routes.image_analysis import router as image_analysis_router
from src.presentation.api.routes.meal_plans import router as meal_plans_router
from src.presentation.api.routes.meal_records import router as meal_records_router
from src.presentation.api.routes.memories import router as memories_router
from src.presentation.api.routes.record_management import (
    router as record_management_router,
)
from src.presentation.api.routes.schedules import router as schedules_router
from src.presentation.api.routes.search_history import router as search_history_router
from src.presentation.api.routes.streaming_chat import router as streaming_chat_router
from src.presentation.api.routes.voice_analysis import router as voice_analysis_router
from src.presentation.api.routes.interactive_confirmation import router as interactive_confirmation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理 - Pure CompositionRoot Pattern"""
    # 起動時処理
    temp_logger = logging.getLogger(__name__)
    temp_logger.info("FastAPI application starting...")

    import time

    start_time = time.time()

    # 🎯 CompositionRoot一元初期化（アプリケーション全体で1度だけ）
    try:
        # Cloud Run用環境変数で軽量起動モードを確認
        # Cloud Run環境では常に軽量起動（起動後に遅延初期化）
        is_production = os.getenv("ENVIRONMENT") == "production"
        
        if is_production:
            temp_logger.info("🚀 Cloud Run本番環境: 軽量起動モード")
            # 軽量起動で8080ポートでリッスン開始
            app.agent_manager = None
            app.logger = temp_logger
            app.composition_root = None
            app._initialization_started = False
        else:
            temp_logger.info("💻 ローカル環境: 完全初期化モード")
            try:
                composition_root = CompositionRootFactory.create()
                temp_logger.info("✅ CompositionRootFactory.create() 完了")
                
                logger = composition_root.logger
                logger.info("✅ CompositionRoot初期化完了")

                # AgentManagerに必要なツールとルーティング戦略、AgentRegistryを注入
                logger.info("ツール取得開始...")
                all_tools = composition_root.get_all_tools()
                logger.info(f"✅ ツール取得完了: {len(all_tools)}個")
                
                logger.info("ルーティング戦略取得開始...")
                routing_strategy = composition_root.get_routing_strategy()
                logger.info("✅ ルーティング戦略取得完了")
                
                logger.info("エージェントレジストリ取得開始...")
                agent_registry = composition_root.get_agent_registry()
                logger.info("✅ エージェントレジストリ取得完了")
                
                logger.info("AgentManager初期化開始...")
                agent_manager = AgentManager(
                    tools=all_tools,
                    logger=logger,
                    settings=composition_root.settings,
                    routing_strategy=routing_strategy,
                    agent_registry=agent_registry,
                    composition_root=composition_root,
                )
                logger.info("✅ AgentManagerインスタンス作成完了")
                
                logger.info("AgentManagerコンポーネント初期化開始...")
                agent_manager.initialize_all_components()
                logger.info("✅ AgentManager初期化完了（Pure Composition Root + ルーティング戦略）")

                # FastAPIアプリには必要なコンポーネントのみ注入
                app.agent_manager = agent_manager
                app.logger = logger
                app.composition_root = composition_root  # 家族管理UseCaseアクセス用
                logger.info("✅ FastAPIアプリ注入完了")
                
            except Exception as init_error:
                temp_logger.error(f"❌ 初期化段階でエラー: {init_error}")
                import traceback
                temp_logger.error(f"❌ スタックトレース: {traceback.format_exc()}")
                raise

        initialization_time = time.time() - start_time
        current_logger = app.logger if hasattr(app, "logger") else temp_logger
        current_logger.info(f"✅ FastAPIアプリ関連付け完了 - 初期化時間: {initialization_time:.2f}秒")

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


# 本番環境での遅延初期化ミドルウェア
@app.middleware("http")
async def lazy_initialization_middleware(request: Request, call_next):
    """本番環境でのみ動作する遅延初期化ミドルウェア"""
    if (os.getenv("ENVIRONMENT") == "production" and 
        hasattr(request.app, "_initialization_started") and 
        not request.app._initialization_started and
        request.url.path not in ["/health", "/", "/docs", "/openapi.json"]):
        
        temp_logger = logging.getLogger(__name__)
        temp_logger.info("🔄 本番環境: 遅延初期化開始...")
        
        try:
            composition_root = CompositionRootFactory.create()
            logger = composition_root.logger
            logger.info("✅ 遅延CompositionRoot初期化完了")

            # AgentManager初期化
            all_tools = composition_root.get_all_tools()
            routing_strategy = composition_root.get_routing_strategy()
            agent_registry = composition_root.get_agent_registry()
            
            agent_manager = AgentManager(
                tools=all_tools,
                logger=logger,
                settings=composition_root.settings,
                routing_strategy=routing_strategy,
                agent_registry=agent_registry,
                composition_root=composition_root,
            )
            agent_manager.initialize_all_components()
            
            # FastAPIアプリに注入
            request.app.agent_manager = agent_manager
            request.app.logger = logger
            request.app.composition_root = composition_root
            request.app._initialization_started = True
            
            logger.info("✅ 遅延初期化完了")
            
        except Exception as e:
            temp_logger.error(f"❌ 遅延初期化失敗: {e}")
            # 初期化に失敗してもヘルスチェックは通す
            pass
    
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌊 ストリーミングチャットルーター（リアルタイム進捗表示）
app.include_router(streaming_chat_router, tags=["streaming"])

# 🤝 Interactive Confirmation ルーター（Human-in-the-Loop）
app.include_router(interactive_confirmation_router, prefix="/api/streaming", tags=["interactive"])

# 👨‍👩‍👧‍👦 家族情報管理ルーター
app.include_router(family_router, prefix="/api", tags=["family"])

# 📊 CRUD機能ルーター（Genieツール連携用）
app.include_router(effort_reports_router, prefix="/api", tags=["effort_reports"])
app.include_router(schedules_router, prefix="/api", tags=["schedules"])
app.include_router(growth_records_router, prefix="/api", tags=["growth_records"])
app.include_router(memories_router, prefix="/api", tags=["memories"])
app.include_router(file_upload_router, tags=["files"])

# 🍽️ 食事プラン管理ルーター
app.include_router(meal_plans_router, prefix="/api", tags=["meal_plans"])

# 🍽️ 食事記録管理ルーター
app.include_router(meal_records_router, prefix="/api/v1", tags=["meal_records"])

# 🔐 認証ルーター
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# 🛠️ 管理者ルーター
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])

# 🤖 エージェント情報ルーター
app.include_router(agents_router, prefix="/api", tags=["agents"])

# 🖼️ 画像解析ルーター
app.include_router(image_analysis_router, tags=["image_analysis"])

# 🎙️ 音声解析ルーター
app.include_router(voice_analysis_router, tags=["voice_analysis"])

# 📝 記録管理ルーター
app.include_router(record_management_router, tags=["record_management"])

# 🔍 検索履歴ルーター
app.include_router(search_history_router, tags=["search_history"])


# 軽量ヘルスチェックエンドポイント（Cloud Run用）
@app.get("/health")
async def health_check():
    """軽量ヘルスチェックエンドポイント - CompositionRoot初期化を待たない"""
    return {"status": "healthy", "service": "genius-backend"}


# 深いヘルスチェックエンドポイント（依存関係確認）
@app.get("/health/deep")
async def deep_health_check(request):
    """深いヘルスチェック - 依存関係が初期化されているかチェック"""
    try:
        # CompositionRootが初期化されているかチェック
        if not hasattr(request.app, "composition_root"):
            return {"status": "initializing", "service": "genius-backend", "message": "Dependencies not ready"}

        return {"status": "ready", "service": "genius-backend", "dependencies": "initialized"}
    except Exception as e:
        return {"status": "error", "service": "genius-backend", "error": str(e)}


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
            "image_analysis": "/api/v1/image-analysis/*",
            "voice_analysis": "/api/v1/voice-analysis/*",
            "record_management": "/api/v1/record-management/*",
            "search_history": "/api/v1/search-history/*",
        },
    }


if __name__ == "__main__":
    print("=== GenieUs Backend Starting ===")
    print(f"Python version: {os.sys.version}")
    print(f"Environment variables:")
    print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not_set')}")
    print(f"  PORT: {os.getenv('PORT', 'not_set')}")
    print(f"  FAST_STARTUP: {os.getenv('FAST_STARTUP', 'not_set')}")
    print(f"  GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT', 'not_set')}")
    
    try:
        # 環境変数からポート設定を取得（デフォルト: 8080でCloud Runと統一）
        port = int(os.getenv("PORT", "8080"))
        host = os.getenv("HOST", "0.0.0.0")
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        reload = os.getenv("RELOAD", "false").lower() == "true"

        print(f"🚀 Starting FastAPI server on {host}:{port}")
        print(f"📡 CORS Origins: {get_cors_origins()}")
        print("=== Starting uvicorn server ===")

        # FastAPIサーバー起動
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
        )
    except Exception as e:
        print(f"❌ Critical startup error: {e}")
        import traceback
        traceback.print_exc()
        raise
