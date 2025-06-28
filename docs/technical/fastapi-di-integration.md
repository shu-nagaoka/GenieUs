# FastAPI DI 統合ガイド

GenieUs プロジェクトにおける FastAPI Depends と Composition Root 統合実装ガイド

## 🎯 概要

**✅ 現在の実装**: GenieUs は**Composition Root + FastAPI Request 経由**パターンを採用しています。dependency-injector ライブラリは使用せず、Pure Composition Root パターンで依存関係を管理します。

## 🏗️ アーキテクチャ概要

### 現行パターン（Composition Root + Request 経由）

```
FastAPI Application
    ↓
CompositionRootFactory.create()  ← main.pyで中央集約組み立て
    ↓
app.composition_root = composition_root  ← FastAPIアプリに注入
    ↓
request.app.composition_root  ← エンドポイントでCompositionRoot取得
    ↓
Depends(get_xxx_usecase)  ← 依存関数でUseCase取得
    ↓
ビジネスロジック実行
```

### アーキテクチャの特徴

| 項目               | GenieUs 実装パターン                | 利点                   |
| ------------------ | ----------------------------------- | ---------------------- |
| **DI ライブラリ**  | Pure Composition Root               | 外部依存なし、軽量     |
| **初期化場所**     | `main.py`で中央集約                 | 依存関係が明確         |
| **依存関係取得**   | `request.app.composition_root`      | FastAPI ネイティブ統合 |
| **テスタビリティ** | CompositionRoot モック化容易        | 高いテスト容易性       |
| **型安全性**       | TypeScript 風型安全 ServiceRegistry | コンパイル時チェック   |

## 📝 実装手順

### 1. Composition Root 設計

```python
# src/di_provider/composition_root.py
import logging
from typing import Any

from google.adk.tools import FunctionTool
from src.config.settings import AppSettings, get_settings
from src.share.logger import setup_logger
from src.share.service_registry import ServiceRegistry

class CompositionRootFactory:
    """CompositionRoot作成ファクトリー - Pure依存性組み立て"""

    @staticmethod
    def create(
        settings: AppSettings | None = None,
        logger: logging.Logger | None = None
    ) -> "CompositionRoot":
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

        # Service registries - 型安全な管理
        self._usecases = ServiceRegistry[Any]()
        self._tools = ServiceRegistry[FunctionTool]()
        self._infrastructure = ServiceRegistry[Any]()

        # Build dependency tree
        self._build_infrastructure_layer()
        self._build_application_layer()
        self._build_tool_layer()

    def get_all_tools(self) -> dict[str, FunctionTool]:
        """全ツールを取得"""
        return self._tools.get_all()
```

### 2. main.py での Composition Root 統合

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.di_provider.composition_root import CompositionRootFactory
from src.agents.agent_manager import AgentManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    try:
        # ⭐ 重要: Composition Root作成（中央集約組み立て）
        composition_root = CompositionRootFactory.create()

        # ⭐ 重要: FastAPIアプリケーションにCompositionRootを注入
        app.composition_root = composition_root
        app.logger = composition_root.logger

        # エージェント初期化
        agent_manager = AgentManager(
            tools=composition_root.get_all_tools(),
            logger=composition_root.logger,
            settings=composition_root.settings
        )
        agent_manager.initialize_all_components()

        composition_root.logger.info("✅ アプリケーション初期化完了")
        yield

    except Exception as e:
        print(f"❌ アプリケーション初期化失敗: {e}")
        raise
    finally:
        composition_root.logger.info("🛑 アプリケーション終了")

# FastAPIアプリケーション作成
app = FastAPI(
    title="GenieUs API",
    lifespan=lifespan
)

# ルート登録
from src.presentation.api.routes import (
    auth, chat_support, family, growth_records, meal_plans,
    memories, schedules, streaming_chat, effort_reports
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat_support.router, prefix="/api/v1")
app.include_router(family.router, prefix="/api/v1")
# ... 他のルート追加
```

### 3. FastAPI Dependencies 実装

```python
# src/presentation/api/dependencies.py
import logging
from typing import Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.application.usecases.chat_support_usecase import ChatSupportUseCase
# ... 他のUseCaseインポート

# セキュリティ設定
security = HTTPBearer()

# ⭐ 重要: CompositionRoot経由でのDI注入パターン

def get_family_management_usecase(request: Request) -> FamilyManagementUseCase:
    """家族管理UseCaseを取得（CompositionRoot経由）"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("family_management")

def get_chat_support_usecase(request: Request) -> ChatSupportUseCase:
    """チャットサポートUseCaseを取得（CompositionRoot経由）"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("chat_support")

def get_logger(request: Request) -> logging.Logger:
    """ロガーを取得（DI注入パターン）"""
    return request.app.composition_root.logger

# 認証関連
def get_user_id_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str | None:
    """オプショナルユーザーID取得"""
    if not credentials:
        return None
    # JWTトークン検証ロジック
    return extract_user_id_from_token(credentials.credentials)

def get_user_id_required(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """必須ユーザーID取得"""
    user_id = get_user_id_optional(credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="認証が必要です")
    return user_id
```

### 4. ルート実装での使用例

```python
# src/presentation/api/routes/family.py
from fastapi import APIRouter, Depends, HTTPException
from src.application.usecases.family_management_usecase import FamilyManagementUseCase
from src.presentation.api.dependencies import (
    get_family_management_usecase,
    get_user_id_optional
)

router = APIRouter(tags=["family"])

@router.post("/family/register")
async def register_family_info(
    request: FamilyRegistrationRequest,
    # ⭐ 重要: Depends経由でのDI注入
    user_id: str = Depends(get_user_id_optional),
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> dict[str, Any]:
    """家族情報を登録"""
    try:
        # ⭐ UseCaseはDI注入済み、直接使用可能
        result = await family_usecase.register_family_info(
            user_id=user_id,
            family_data=request.dict()
        )
        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="内部サーバーエラー")

@router.get("/family/{family_id}")
async def get_family_info(
    family_id: str,
    user_id: str = Depends(get_user_id_required),
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
) -> dict[str, Any]:
    """家族情報を取得"""
    try:
        family_info = await family_usecase.get_family_info(
            family_id=family_id,
            requesting_user_id=user_id
        )
        return {"success": True, "data": family_info}

    except PermissionError:
        raise HTTPException(status_code=403, detail="アクセス権限がありません")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## ⚡ DI 統合の重要原則

### ✅ 推奨パターン

1. **CompositionRoot 中央集約**

   ```python
   # main.pyで一元的に組み立て
   composition_root = CompositionRootFactory.create()
   app.composition_root = composition_root
   ```

2. **Request 経由の DI 注入**

   ```python
   def get_usecase(request: Request) -> SomeUseCase:
       return request.app.composition_root._usecases.get_required("some_usecase")
   ```

3. **型安全な ServiceRegistry**

   ```python
   self._usecases = ServiceRegistry[Any]()  # 型安全な管理
   ```

4. **宣言的依存関係**
   ```python
   async def endpoint(
       usecase: SomeUseCase = Depends(get_usecase),  # 宣言的
   ):
   ```

### ❌ 避けるべきパターン

1. **グローバル変数の使用**

   ```python
   # ❌ 避ける
   _container = None  # グローバル状態
   ```

2. **setup_routes 関数**

   ```python
   # ❌ 非推奨パターン
   def setup_routes(container, agent):
   ```

3. **個別ロガー初期化**

   ```python
   # ❌ 避ける
   logger = setup_logger(__name__)  # 個別初期化
   ```

4. **dependency-injector ライブラリ**
   ```python
   # ❌ 使用しない
   @inject
   def endpoint(usecase = Depends(Provide[Container.usecase])):
   ```

## 🧪 テスト統合

### テスト用 CompositionRoot

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from src.di_provider.composition_root import CompositionRoot

@pytest.fixture
def mock_composition_root():
    """テスト用CompositionRoot"""
    mock_root = Mock(spec=CompositionRoot)

    # モックUseCase作成
    mock_usecase = Mock()
    mock_root._usecases.get_required.return_value = mock_usecase

    return mock_root

@pytest.fixture
def test_app(mock_composition_root):
    """テスト用FastAPIアプリ"""
    from src.main import app

    # テスト用CompositionRootを注入
    app.composition_root = mock_composition_root
    app.logger = Mock()

    return app
```

### エンドポイントテスト

```python
# tests/test_family_routes.py
import pytest
from fastapi.testclient import TestClient

def test_register_family_info(test_app, mock_composition_root):
    """家族情報登録APIテスト"""
    client = TestClient(test_app)

    # モックUseCase設定
    mock_usecase = mock_composition_root._usecases.get_required.return_value
    mock_usecase.register_family_info.return_value = {"family_id": "test_id"}

    # APIテスト実行
    response = client.post(
        "/api/v1/family/register",
        json={"name": "田中家", "children": []}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_usecase.register_family_info.assert_called_once()
```

## 📊 パフォーマンス最適化

### 1. ServiceRegistry 最適化

```python
# 型安全かつ高速なServiceRegistry
class ServiceRegistry[T]:
    def __init__(self) -> None:
        self._services: dict[str, T] = {}

    def register(self, name: str, service: T) -> None:
        self._services[name] = service

    def get_required(self, name: str) -> T:
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found")
        return self._services[name]
```

### 2. 遅延初期化

```python
class CompositionRoot:
    def get_usecase_lazy(self, name: str):
        """遅延初期化でパフォーマンス向上"""
        if not hasattr(self, f"_{name}_usecase"):
            usecase = self._create_usecase(name)
            setattr(self, f"_{name}_usecase", usecase)
        return getattr(self, f"_{name}_usecase")
```

## 🎯 まとめ

GenieUs の FastAPI DI 統合は、以下の特徴を持つ実用的なアーキテクチャです：

### **核心価値**

1. **Pure Composition Root**: 外部ライブラリ依存なし
2. **FastAPI ネイティブ統合**: Request 経由の自然な注入
3. **型安全**: TypeScript 風 ServiceRegistry
4. **テスト容易性**: CompositionRoot モック化
5. **中央集約**: main.py での依存関係組み立て

### **実装パターン**

```
CompositionRoot作成 → FastAPIアプリ注入 → Request経由取得 → Depends統合
```

この統合アーキテクチャにより、GenieUs は保守しやすく、テストしやすく、拡張しやすい DI 統合を実現しています。

---

**最終更新**: 2025-06-28  
**対応バージョン**: Composition Root + FastAPI Request 経由統合
