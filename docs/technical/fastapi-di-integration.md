# FastAPI DI統合ガイド

GenieUsプロジェクトにおけるFastAPI DependsとComposition Root統合実装ガイド

## 🎯 概要

**⚠️ 重要**: GenieUsは現在**Composition Root**パターンを採用しています。dependency-injectorは廃止され、main.pyでの中央集約組み立てにより依存関係を管理します。

## 🏗️ アーキテクチャ概要

### 現行パターン（Composition Root）
```
FastAPI Application
    ↓
CompositionRootFactory.create()  ← main.pyで中央集約組み立て
    ↓
@inject + Depends(Provide[])  ← エンドポイント依存関係注入
    ↓ 
ビジネスロジック実行
```

### 従来の問題点 vs 新パターン（Composition Root）

| 項目 | 従来（グローバル変数） | 新パターン（Composition Root） |
|------|-------------------|--------------------------|
| **初期化** | `setup_routes(container, agent)` | `CompositionRootFactory.create()` |
| **依存関係取得** | `_container.service()` | `composition_root.get_service()` |
| **テスタビリティ** | グローバル状態で困難 | 明示的注入で容易 |
| **型安全性** | 実行時エラーリスク | コンパイル時チェック |
| **集約場所** | 各モジュールで分散 | main.pyで中央集約 |

## 📝 実装手順

### 1. Composition Root設計

```python
# src/di_provider/composition_root.py
import logging
from google.adk.tools import FunctionTool
from src.config.settings import AppSettings, get_settings
from src.share.logger import setup_logger

class CompositionRootFactory:
    """CompositionRoot作成ファクトリー - Pure依存性組み立て"""

    @staticmethod
    def create(settings: AppSettings | None = None, logger: logging.Logger | None = None) -> "CompositionRoot":
        """CompositionRoot作成（本番・テスト統一）"""
        settings = settings or get_settings()
        logger = logger or setup_logger(name=settings.APP_NAME, env=settings.ENVIRONMENT)
        return CompositionRoot(settings=settings, logger=logger)

class CompositionRoot:
    """アプリケーション全体の依存関係組み立て（main.py中央集約）"""

    def __init__(self, settings: AppSettings, logger: logging.Logger) -> None:
        # Core components - 完全外部注入
        self.settings = settings
        self.logger = logger

        # Service registries
        self._usecases = ServiceRegistry[Any]()
        self._tools = ServiceRegistry[FunctionTool]()
        self._infrastructure = ServiceRegistry[Any]()

        # Build dependency tree
        self._build_infrastructure_layer()
        self._build_application_layer()
        self._build_tool_layer()
```

### 2. main.pyのComposition Root統合

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.di_provider.composition_root import CompositionRootFactory

# ⭐ Composition Root - アプリケーション状態管理
composition_root = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    global composition_root
    
    try:
        # ⭐ 重要: Composition Root作成（中央集約組み立て）
        composition_root = CompositionRootFactory.create()
        
        # エージェント初期化
        all_tools = composition_root.get_all_tools()
        agent_manager = AgentManager(tools=all_tools, logger=composition_root.logger)
        agent_manager.initialize_all_components()
        
        composition_root.logger.info("✅ アプリケーション初期化完了")
        yield
        
    except Exception as e:
        if composition_root:
            composition_root.logger.error(f"❌ アプリケーション初期化失敗: {e}")
        raise
    finally:
        if composition_root:
            composition_root.logger.info("🔄 アプリケーション終了処理完了")

app = FastAPI(
    title="GenieUs API v2.0",
    description="Google ADK powered 次世代子育て支援 API", 
    version="2.0.0",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(CORSMiddleware, ...)

# ルーター登録
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(family_router, prefix="/api/v1", tags=["family"])
```

### 3. API層のComposition Root統合

```python
# src/presentation/api/routes/chat.py
from fastapi import APIRouter, HTTPException
from src.presentation.api.dependencies import get_composition_root

router = APIRouter()

# ❌ 削除：グローバル変数
# _container = None
# _childcare_agent = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    # ⭐ Composition Root経由で依存関係取得
    composition_root = Depends(get_composition_root),
):
    """チャットエンドポイント（Composition Root統合版）"""
    logger = composition_root.logger
    
    logger.info(
        "チャット要求受信",
        extra={
            "user_id": request.user_id,
            "session_id": request.session_id,
            "message_length": len(request.message)
        }
    )
    
    try:
        # エージェントマネージャー取得
        agent_manager = composition_root.get_agent_manager()
        
        # チャット処理実行
        response = await agent_manager.process_chat(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        logger.info("チャット処理完了", extra={"session_id": request.session_id})
        
        return ChatResponse(
            response=response.text,
            status="success",
            session_id=request.session_id,
            follow_up_questions=response.follow_up_questions
        )
            
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

# src/presentation/api/dependencies.py
from fastapi import Depends
from src.di_provider.composition_root import CompositionRoot

def get_composition_root() -> CompositionRoot:
    """Composition Root取得（FastAPI Depends）"""
    from src.main import composition_root
    
    if composition_root is None:
        raise RuntimeError("Composition Root not initialized")
    
    return composition_root
```

### 4. ツール層のComposition Root統合

```python
# src/tools/growth_record_tool.py
from google.adk.tools import FunctionTool
import logging

class GrowthRecordTool:
    """成長記録管理ツール（Composition Root統合版）"""

    def __init__(self, growth_record_usecase, logger: logging.Logger):
        self.growth_record_usecase = growth_record_usecase
        self.logger = logger  # ⭐ Composition Rootから注入されたロガー

    def create_growth_record(self, child_id: str, record_data: dict) -> dict:
        """成長記録作成"""
        try:
            self.logger.info("成長記録作成開始", extra={"child_id": child_id})
            
            result = self.growth_record_usecase.create_record(
                child_id=child_id,
                record_data=record_data
            )
            
            self.logger.info("成長記録作成完了", extra={"child_id": child_id})
            return {"success": True, "record_id": result.id}
            
        except Exception as e:
            self.logger.error(
                "成長記録作成エラー",
                extra={
                    "error": str(e),
                    "child_id": child_id
                }
            )
            return {"success": False, "error": str(e)}

    def get_function_declarations(self) -> list:
        """ADK FunctionTool用の関数定義取得"""
        return [
            {
                "name": "create_growth_record",
                "description": "子どもの成長記録を作成します",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "child_id": {"type": "string", "description": "子どもID"},
                        "record_data": {"type": "object", "description": "記録データ"}
                    },
                    "required": ["child_id", "record_data"]
                }
            }
        ]

# Composition Root統合（composition_root.py内）
def _create_growth_record_tool(self, usecase) -> FunctionTool:
    """成長記録管理ツール作成"""
    growth_record_tool = GrowthRecordTool(
        growth_record_usecase=usecase,
        logger=self.logger  # ⭐ Composition Rootのロガー注入
    )
    
    return FunctionTool(
        function_declarations=growth_record_tool.get_function_declarations()
    )
```

## 🧪 テスト統合

### Composition Rootモック化

```python
# tests/test_chat_api.py
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from src.main import app
from src.di_provider.composition_root import CompositionRoot

@pytest.fixture
def mock_composition_root():
    """テスト用Composition Rootモック"""
    mock_root = Mock(spec=CompositionRoot)
    mock_root.logger = Mock()
    mock_agent_manager = Mock()
    mock_agent_manager.process_chat.return_value = Mock(
        text="テスト応答",
        follow_up_questions=["フォローアップ質問"]
    )
    mock_root.get_agent_manager.return_value = mock_agent_manager
    return mock_root

@pytest.fixture
def app_with_mock(mock_composition_root):
    """モック化されたアプリケーション"""
    # ⭐ テスト用にComposition Rootをオーバーライド
    with patch("src.main.composition_root", mock_composition_root):
        yield app

def test_chat_endpoint_success(app_with_mock, mock_composition_root):
    with TestClient(app_with_mock) as client:
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
        mock_composition_root.get_agent_manager.assert_called_once()
```

## 🔧 マイグレーション手順

### Phase 1: Composition Root構築
1. `CompositionRootFactory.create()`実装
2. Infrastructure/Application/Tool層の組み立てロジック実装
3. 全依存関係の中央集約化

### Phase 2: main.py統合
1. lifespanでComposition Root初期化
2. エージェント初期化処理統合
3. グローバル変数elimination

### Phase 3: API層更新
1. `get_composition_root()` dependencies作成
2. 各エンドポイントでComposition Root経由の依存関係取得
3. グローバル変数（_container, _agent）削除

### Phase 4: ツール層統合
1. ツールクラスにlogger注入
2. Composition Root内でのツール作成メソッド実装
3. FunctionTool統合

### Phase 5: 検証
1. 既存エンドポイント正常動作確認
2. テストコードでComposition Rootモック化
3. ログ出力統一確認

## 🎯 メリット

### 1. 中央集約管理
- main.pyでの一元的な依存関係組み立て
- 設定変更時の影響範囲が明確

### 2. テスタビリティ向上
- Composition Rootモック化でテスト簡潔化
- 依存関係が明示的でテストケース作成が容易

### 3. 型安全性
- 完全な型アノテーション対応
- IDEでの自動補完とコンパイル時チェック

### 4. スケーラビリティ
- 新機能追加時の一貫したパターン
- レイヤー間責務の明確な分離

### 5. 保守性
- グローバル変数完全排除
- 依存関係フローの可視化

## 📋 チェックリスト

### 実装完了確認
- [ ] CompositionRootFactory.create()実装完了
- [ ] main.pyでのlifespan統合完了
- [ ] get_composition_root() dependencies実装
- [ ] API層でComposition Root経由の依存関係取得
- [ ] グローバル変数（_container, _agent）完全削除
- [ ] 全ツールクラスでlogger注入対応

### 動作確認
- [ ] 既存APIエンドポイント正常動作
- [ ] ログ出力が統一フォーマットで記録
- [ ] テストコードでComposition Rootモック化動作
- [ ] IDEでの型チェックパス
- [ ] エージェント初期化正常完了

### アーキテクチャ検証
- [ ] dependency-injector完全削除
- [ ] Pure Composition Pattern実装
- [ ] レイヤー責務の明確な分離
- [ ] 中央集約組み立ての実現

この統合により、GenieUsプロジェクトはComposition Rootパターンによる堅牢なDI管理を実現し、保守性・テスタビリティ・型安全性が大幅に向上します。