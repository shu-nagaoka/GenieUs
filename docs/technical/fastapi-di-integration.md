# FastAPI DI統合ガイド

GenieUsプロジェクトにおけるFastAPI DependsとDIコンテナの統合実装ガイド

## 🎯 概要

dependency-injectorとFastAPI Dependsを統合し、グローバル変数を排除したクリーンな依存関係管理を実現します。

## 🏗️ アーキテクチャ概要

### 統合パターン
```
FastAPI Application
    ↓
DIContainer.wire()  ← モジュール自動配線
    ↓
@inject + Depends(Provide[])  ← エンドポイント依存関係注入
    ↓ 
ビジネスロジック実行
```

### 従来の問題点 vs 新パターン

| 項目 | 従来（グローバル変数） | 新パターン（FastAPI Depends） |
|------|-------------------|------------------------|
| **初期化** | `setup_routes(container, agent)` | `container.wire(modules=[...])` |
| **依存関係取得** | `_container.service()` | `Depends(Provide[Container.service])` |
| **テスタビリティ** | グローバル状態で困難 | `container.override()`で容易 |
| **型安全性** | 実行時エラーリスク | コンパイル時チェック |

## 📝 実装手順

### 1. DIコンテナ調整

```python
# src/di_provider/container.py
import logging
from dependency_injector import containers, providers
from src.tools.childcare_consultation_tool import create_childcare_consultation_tool

class DIContainer(containers.DeclarativeContainer):
    # 既存の設定...
    
    # ロガー（全層で統一）
    logger: providers.Provider[logging.Logger] = providers.Singleton(
        setup_logger,
        name=config.provided.APP_NAME,
        env=config.provided.ENVIRONMENT,
    )
    
    # Tools Layer - ロガー注入版
    childcare_consultation_tool: providers.Provider[FunctionTool] = providers.Factory(
        create_childcare_consultation_tool,
        usecase=pure_childcare_usecase,
        logger=logger,  # ⭐ ロガーも注入
    )
```

### 2. main.pyのアプリケーションファクトリー化

```python
# src/main.py
from dependency_injector.wiring import inject, Provide
from src.di_provider.container import DIContainer

def create_app() -> FastAPI:
    """FastAPIアプリケーションファクトリー"""
    # DIコンテナ初期化
    container = DIContainer()
    
    app = FastAPI(
        title="GenieUs API v2.0",
        description="Google ADK powered 次世代子育て支援 API",
        version="2.0.0",
        lifespan=lifespan,
    )
    
    # アプリケーションにコンテナを関連付け
    app.container = container
    
    # ⭐ 重要: wiringでFastAPI Dependsと統合
    container.wire(modules=[
        "src.presentation.api.routes.chat",
        "src.presentation.api.routes.health",
    ])
    
    # CORS設定
    app.add_middleware(CORSMiddleware, ...)
    
    # ルーター登録（グローバル変数不要）
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
    
    return app

# アプリケーション作成
app = create_app()

# ❌ 削除：グローバル初期化
# logger = setup_logger(__name__)  # これは削除

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """グローバル例外ハンドラー"""
    # ロガーもDIから取得可能
    return JSONResponse(
        status_code=500,
        content={"error": "内部サーバーエラーが発生しました"}
    )
```

### 3. API層のDepends化

```python
# src/presentation/api/routes/chat.py
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from src.di_provider.container import DIContainer

router = APIRouter()

# ❌ 削除：グローバル変数
# _container = None
# _childcare_agent = None

# ❌ 削除：setup_routes関数
# def setup_routes(container, childcare_agent): ...

@router.post("/chat", response_model=ChatResponse)
@inject  # ⭐ DI注入を有効化
async def chat_endpoint(
    request: ChatRequest,
    # ⭐ FastAPI Depends + DI統合
    tool = Depends(Provide[DIContainer.childcare_consultation_tool]),
    logger = Depends(Provide[DIContainer.logger]),
):
    """チャットエンドポイント（DI完全統合版）"""
    logger.info(
        "チャット要求受信",
        extra={
            "user_id": request.user_id,
            "session_id": request.session_id,
            "message_length": len(request.message)
        }
    )
    
    try:
        # ツール使用（DIから注入済み）
        tool_result = tool.func(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        if tool_result.get("success"):
            response_text = remove_follow_up_section(tool_result["response"])
            logger.info("チャット処理完了", extra={"session_id": request.session_id})
            
            return ChatResponse(
                response=response_text,
                status="success",
                session_id=request.session_id,
                follow_up_questions=extract_follow_up_questions(tool_result["response"])
            )
        else:
            raise HTTPException(status_code=500, detail="ツール実行エラー")
            
    except Exception as e:
        logger.error(
            "チャット処理エラー",
            extra={
                "error": str(e),
                "session_id": request.session_id
            }
        )
        raise HTTPException(
            status_code=500,
            detail="申し訳ございません。一時的な問題が発生しました。"
        )
```

### 4. エージェント・ツール層のロガー注入

```python
# src/agents/di_based_childcare_agent.py
def create_childcare_agent(
    childcare_tool: FunctionTool,
    logger: logging.Logger  # ⭐ 追加：ロガーも注入
) -> Agent:
    """注入されたツールとロガーを使用する子育て相談エージェント"""
    logger.info("子育て相談エージェント作成開始")
    
    try:
        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="GenieChildcareConsultant",
            description="DIコンテナーベースの子育て相談エージェント",
            instruction="...",
            tools=[childcare_tool],
        )
        logger.info("子育て相談エージェント作成完了")
        return agent
    except Exception as e:
        logger.error(f"子育て相談エージェント作成エラー: {e}")
        raise

# src/tools/childcare_consultation_tool.py
def create_childcare_consultation_tool(
    usecase: PureChildcareUseCase,
    logger: logging.Logger  # ⭐ 追加：ロガーも注入
) -> FunctionTool:
    """子育て相談FunctionToolを作成（ロガー注入版）"""
    
    def childcare_consultation_function(...) -> dict[str, Any]:
        try:
            logger.info("相談処理開始", extra={"session_id": session_id})
            # 処理...
            logger.info("相談処理完了", extra={"session_id": session_id})
            return response
        except Exception as e:
            logger.error(
                "子育て相談ツールでエラー",
                extra={
                    "error": str(e),
                    "session_id": session_id,
                    "user_id": user_id
                }
            )
            return fallback_response
    
    return FunctionTool(func=childcare_consultation_function)
```

## 🧪 テスト統合

### DIコンテナオーバーライド

```python
# tests/test_chat_api.py
import pytest
from dependency_injector import providers
from src.main import create_app

@pytest.fixture
def app_with_mock():
    app = create_app()
    
    # ⭐ テスト用にコンテナをオーバーライド
    with app.container.childcare_consultation_tool.override(mock_tool):
        with app.container.logger.override(mock_logger):
            yield app

def test_chat_endpoint_success(app_with_mock):
    with TestClient(app_with_mock) as client:
        response = client.post("/api/v1/chat", json={
            "message": "テストメッセージ",
            "user_id": "test_user",
            "session_id": "test_session"
        })
        assert response.status_code == 200
```

## 🔧 マイグレーション手順

### Phase 1: 準備
1. DIコンテナにロガー注入設定追加
2. ツール・エージェント作成関数にlogger引数追加

### Phase 2: 統合
1. main.pyをアプリケーションファクトリーパターンに変更
2. container.wire()設定追加

### Phase 3: API更新
1. chat.pyでグローバル変数削除
2. @inject + Depends(Provide[])パターン導入

### Phase 4: 検証
1. 既存エンドポイントが正常動作することを確認
2. テストコードでcontainer.override()を活用

## 🎯 メリット

### 1. テスタビリティ向上
- `container.override()`でモック注入が容易
- 依存関係が明示的でテストケース作成が簡単

### 2. 型安全性
- IDEでの自動補完とタイプチェック
- コンパイル時の依存関係検証

### 3. スケーラビリティ
- 新しいエンドポイント追加時の作業量削減
- 統一された依存関係管理パターン

### 4. 保守性
- グローバル変数の排除
- 明示的な依存関係による可読性向上

## 📋 チェックリスト

### 実装完了確認
- [ ] DIコンテナにロガー注入設定追加
- [ ] main.pyアプリケーションファクトリー化
- [ ] container.wire()設定完了
- [ ] API層でDepends(Provide[])パターン使用
- [ ] グローバル変数（_container, _agent）削除
- [ ] エージェント・ツール作成関数にlogger引数追加

### 動作確認
- [ ] 既存APIエンドポイント正常動作
- [ ] ログ出力が統一フォーマットで記録
- [ ] テストコードが正常実行
- [ ] IDEでの型チェックパス

この統合により、GenieUsプロジェクトのDI管理が大幅に改善され、保守性・テスタビリティ・型安全性が向上します。