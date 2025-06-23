# DI統合マイグレーションガイド

GenieUsプロジェクトの既存コードをロガーDI化 + FastAPI Depends統合に移行するための実践ガイド

## 🎯 マイグレーション概要

### 移行前の問題
- **混在するロガー初期化**: 各ファイルで`setup_logger(__name__)`を個別呼び出し
- **グローバル変数依存**: `_container`、`_childcare_agent`によるAPI設計
- **テスト困難**: グローバル状態とハードコーディングされた依存関係

### 移行後の改善
- **統一ロガー管理**: DIコンテナからの一元的な注入
- **FastAPI Depends統合**: `@inject` + `Depends(Provide[])`による宣言的DI
- **テスタビリティ向上**: `container.override()`による簡単なモック注入

## 📋 マイグレーション手順

### Phase 1: DIコンテナ準備

#### 1.1 container.pyの更新

```python
# src/di_provider/container.py
class DIContainer(containers.DeclarativeContainer):
    # 既存の設定...
    
    # ⭐ 追加: ロガー統一管理
    logger: providers.Provider[logging.Logger] = providers.Singleton(
        setup_logger,
        name=config.provided.APP_NAME,
        env=config.provided.ENVIRONMENT,
    )
    
    # ⭐ 更新: ツールにロガー注入
    childcare_consultation_tool: providers.Provider[FunctionTool] = providers.Factory(
        create_childcare_consultation_tool,
        usecase=pure_childcare_usecase,
        logger=logger,  # 追加
    )
```

#### 1.2 ツール層の更新

```python
# src/tools/childcare_consultation_tool.py

# ❌ 削除: 個別ロガー初期化
# logger = logging.getLogger(__name__)

# ✅ 更新: ロガー注入版
def create_childcare_consultation_tool(
    usecase: PureChildcareUseCase,
    logger: logging.Logger  # 追加
) -> FunctionTool:
    """子育て相談FunctionToolを作成（ロガー注入版）"""
    
    def childcare_consultation_function(...) -> dict[str, Any]:
        try:
            logger.info("相談処理開始", extra={"session_id": session_id})
            # 既存処理...
            logger.info("相談処理完了", extra={"session_id": session_id})
            return response
        except Exception as e:
            # ❌ 削除: 局所ロガー生成
            # logger = logging.getLogger(__name__)
            
            # ✅ 使用: 注入されたロガー
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

#### 1.3 エージェント層の更新

```python
# src/agents/di_based_childcare_agent.py

# ❌ 削除: 個別ロガー初期化
# logger = setup_logger(__name__)

# ✅ 更新: ロガー注入版
def create_childcare_agent(
    childcare_tool: FunctionTool,
    logger: logging.Logger  # 追加
) -> Agent:
    """注入されたツールとロガーを使用する子育て相談エージェント"""
    logger.info("子育て相談エージェント作成開始")
    
    try:
        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="GenieChildcareConsultant",
            # 既存設定...
        )
        logger.info("子育て相談エージェント作成完了")
        return agent
    except Exception as e:
        logger.error(f"子育て相談エージェント作成エラー: {e}")
        raise

# 他のヘルパー関数も同様に更新
def get_childcare_agent(
    agent_type: str, 
    childcare_tool: FunctionTool,
    logger: logging.Logger  # 追加
) -> Agent:
    if agent_type == "advanced":
        return create_childcare_agent(childcare_tool, logger)
    elif agent_type == "simple":
        return create_simple_childcare_agent(childcare_tool, logger)
    else:
        logger.warning(f"未対応のエージェントタイプ: {agent_type}, simpleを使用")
        return create_simple_childcare_agent(childcare_tool, logger)
```

### Phase 2: main.pyアプリケーションファクトリー化

#### 2.1 現在のmain.pyパターン

```python
# ❌ 現在の実装（削除対象）
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI application starting...")
    container = get_container()
    childcare_tool = container.childcare_consultation_tool()
    childcare_agent = get_childcare_agent("simple", childcare_tool)
    setup_routes(container, childcare_agent)  # グローバル変数設定
    yield
    logger.info("FastAPI application shutting down...")

app = FastAPI(lifespan=lifespan)
logger = setup_logger(__name__)  # 個別初期化
```

#### 2.2 新しいファクトリーパターン

```python
# ✅ 新しい実装
from dependency_injector.wiring import inject, Provide

def create_app() -> FastAPI:
    """FastAPIアプリケーションファクトリー"""
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
    
    # 設定...
    app.add_middleware(CORSMiddleware, ...)
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    
    return app

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理（DI統合版）"""
    # 起動時処理
    # ログも含めてすべてDIから取得可能
    yield
    # 終了時処理

# アプリケーション作成
app = create_app()

# ❌ 削除: 個別ロガー初期化
# logger = setup_logger(__name__)
```

### Phase 3: API層のDepends化

#### 3.1 現在のchat.pyパターン

```python
# ❌ 現在の実装（削除対象）
logger = setup_logger(__name__)  # 個別初期化

# グローバル変数
_container = None
_childcare_agent = None

def setup_routes(container, childcare_agent):
    """グローバル変数設定（非推奨パターン）"""
    global _container, _childcare_agent
    _container = container
    _childcare_agent = childcare_agent

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info("チャット要求受信")
    # グローバル変数に依存
    tool = _container.childcare_consultation_tool()
    # 処理...
```

#### 3.2 新しいDependsパターン

```python
# ✅ 新しい実装
from dependency_injector.wiring import inject, Provide
from fastapi import Depends

router = APIRouter()

# ❌ 削除: グローバル変数
# _container = None
# _childcare_agent = None
# logger = setup_logger(__name__)

# ❌ 削除: setup_routes関数
# def setup_routes(container, childcare_agent): ...

@router.post("/chat", response_model=ChatResponse)
@inject  # DI注入を有効化
async def chat_endpoint(
    request: ChatRequest,
    # FastAPI Depends + DI統合
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

### Phase 4: テスト更新

#### 4.1 新しいテストパターン

```python
# tests/test_chat_api.py
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from src.main import create_app

@pytest.fixture
def app_with_mock():
    """DIコンテナをモックで上書きしたアプリケーション"""
    app = create_app()
    
    # モックツール作成
    mock_tool = Mock()
    mock_tool.func.return_value = {
        "success": True,
        "response": "テスト応答",
        "metadata": {"test": True}
    }
    
    # モックロガー作成
    mock_logger = Mock()
    
    # ⭐ DIコンテナをオーバーライド
    with app.container.childcare_consultation_tool.override(mock_tool):
        with app.container.logger.override(mock_logger):
            yield app, mock_tool, mock_logger

def test_chat_endpoint_success(app_with_mock):
    """チャットエンドポイント正常系テスト"""
    app, mock_tool, mock_logger = app_with_mock
    
    with TestClient(app) as client:
        response = client.post("/api/v1/chat", json={
            "message": "テストメッセージ",
            "user_id": "test_user",
            "session_id": "test_session"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "テスト応答"
        assert data["status"] == "success"
        
        # モック呼び出し確認
        mock_tool.func.assert_called_once()
        mock_logger.info.assert_called()
```

## 🔧 マイグレーション実行

### ステップ1: バックアップ
```bash
# 現在の実装をバックアップ
cp -r backend/src backend/src.backup.$(date +%Y%m%d)
```

### ステップ2: Phase順実行
```bash
# Phase 1: DIコンテナ準備
# 1. container.pyの更新
# 2. ツール・エージェント層のロガー注入対応

# Phase 2: main.pyファクトリー化
# 3. create_app()関数作成
# 4. container.wire()設定

# Phase 3: API層Depends化
# 5. chat.pyのグローバル変数削除
# 6. @inject + Depends(Provide[])導入

# Phase 4: テスト更新
# 7. container.override()を使ったテストケース作成
```

### ステップ3: 動作確認
```bash
# サーバー起動確認
./scripts/start-dev.sh

# エンドポイント動作確認
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "テスト", "user_id": "test", "session_id": "test"}'

# テスト実行確認
cd backend && uv run pytest
```

## 📋 完了チェックリスト

### Phase 1: DIコンテナ準備
- [ ] container.pyにlogger providers追加
- [ ] ツール作成関数にlogger引数追加
- [ ] エージェント作成関数にlogger引数追加
- [ ] 個別setup_logger呼び出し削除

### Phase 2: main.pyファクトリー化
- [ ] create_app()関数実装
- [ ] container.wire()設定
- [ ] 個別ロガー初期化削除
- [ ] lifespan関数適応

### Phase 3: API層Depends化
- [ ] @injectデコレータ追加
- [ ] Depends(Provide[])パターン実装
- [ ] グローバル変数削除
- [ ] setup_routes関数削除

### Phase 4: テスト更新
- [ ] container.override()を使ったテストケース作成
- [ ] モックロガー・ツールの動作確認
- [ ] 既存テストの更新

### 動作確認
- [ ] 開発サーバー正常起動
- [ ] チャットエンドポイント正常動作
- [ ] ログ出力が統一フォーマット
- [ ] テストケース正常実行
- [ ] 型チェックパス

## 🔍 トラブルシューティング

### よくある問題

#### 1. wiringエラー
```
ERROR: Module 'src.presentation.api.routes.chat' not found
```
**解決**: モジュールパスの確認、import可能性の検証

#### 2. Provideエラー
```
ERROR: Provider 'DIContainer.logger' not found
```
**解決**: container.py のproviders設定確認

#### 3. 循環import
```
ERROR: Circular import detected
```
**解決**: import順序の調整、遅延importの活用

この段階的なマイグレーションにより、GenieUsプロジェクトは現代的なDI統合パターンに移行し、保守性・テスタビリティが大幅に向上します。