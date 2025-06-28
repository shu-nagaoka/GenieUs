# DI統合マイグレーションガイド

GenieUsプロジェクトの既存コードをComposition Root + FastAPI Depends統合に移行するための実践ガイド

## 🎯 マイグレーション概要

### 移行前の問題

- **混在するロガー初期化**: 各ファイルで`setup_logger(__name__)`を個別呼び出し
- **グローバル変数依存**: `_container`、`_childcare_agent`によるAPI設計
- **テスト困難**: グローバル状態とハードコーディングされた依存関係

### 移行後の改善（現在の実装）

- **統一ロガー管理**: CompositionRootからの一元的な注入
- **FastAPI Depends統合**: `request.app.composition_root`による宣言的DI
- **テスタビリティ向上**: CompositionRootモック化による簡単なテスト

## 📋 マイグレーション手順

### Phase 1: Composition Root準備

#### 1.1 CompositionRootの設計

```python
# src/di_provider/composition_root.py
import logging
from typing import Any

from google.adk.tools import FunctionTool
from src.config.settings import AppSettings, get_settings
from src.share.logger import setup_logger
from src.share.service_registry import ServiceRegistry

class CompositionRootFactory:
    """CompositionRoot作成ファクトリー"""

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
    """アプリケーション全体の依存関係組み立て"""

    def __init__(self, settings: AppSettings, logger: logging.Logger) -> None:
        # Core components
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

    def _build_infrastructure_layer(self) -> None:
        """インフラストラクチャ層組み立て"""
        # データベース接続
        from src.infrastructure.database.sqlite_manager import SQLiteManager
        db_manager = SQLiteManager(
            db_path=self.settings.DATABASE_PATH,
            logger=self.logger
        )
        self._infrastructure.register("db_manager", db_manager)

        # リポジトリ層
        from src.infrastructure.adapters.persistence.user_repository import UserRepository
        user_repo = UserRepository(
            db_manager=db_manager,
            logger=self.logger
        )
        self._infrastructure.register("user_repository", user_repo)

    def _build_application_layer(self) -> None:
        """アプリケーション層組み立て"""
        # UseCase層
        from src.application.usecases.user_management_usecase import UserManagementUseCase
        user_usecase = UserManagementUseCase(
            user_repository=self._infrastructure.get_required("user_repository"),
            logger=self.logger
        )
        self._usecases.register("user_management", user_usecase)

    def _build_tool_layer(self) -> None:
        """ツール層組み立て"""
        # FunctionTool層
        from src.tools.search_history_tool import SearchHistoryTool
        search_tool = SearchHistoryTool(
            search_usecase=self._usecases.get_required("search_history"),
            logger=self.logger
        )
        self._tools.register("search_history", search_tool)
```

#### 1.2 ServiceRegistry実装

```python
# src/share/service_registry.py
from typing import TypeVar, Generic, Dict

T = TypeVar('T')

class ServiceRegistry(Generic[T]):
    """型安全なサービスレジストリ"""

    def __init__(self) -> None:
        self._services: Dict[str, T] = {}

    def register(self, name: str, service: T) -> None:
        """サービス登録"""
        self._services[name] = service

    def get_required(self, name: str) -> T:
        """必須サービス取得"""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found")
        return self._services[name]

    def get_optional(self, name: str) -> T | None:
        """オプショナルサービス取得"""
        return self._services.get(name)

    def get_all(self) -> Dict[str, T]:
        """全サービス取得"""
        return self._services.copy()
```

### Phase 2: main.py統合

#### 2.1 FastAPIアプリケーション統合

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.di_provider.composition_root import CompositionRootFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    try:
        # ⭐ 重要: Composition Root作成
        composition_root = CompositionRootFactory.create()
        
        # ⭐ 重要: FastAPIアプリに注入
        app.composition_root = composition_root
        app.logger = composition_root.logger
        
        composition_root.logger.info("✅ アプリケーション初期化完了")
        yield
        
    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        raise
    finally:
        app.logger.info("🛑 アプリケーション終了")

# FastAPIアプリケーション作成
app = FastAPI(
    title="GenieUs API",
    lifespan=lifespan
)
```

### Phase 3: Dependencies実装

#### 3.1 依存関数の作成

```python
# src/presentation/api/dependencies.py
import logging
from fastapi import Request
from src.application.usecases.user_management_usecase import UserManagementUseCase

def get_user_management_usecase(request: Request) -> UserManagementUseCase:
    """ユーザー管理UseCaseを取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("user_management")

def get_logger(request: Request) -> logging.Logger:
    """ロガーを取得"""
    return request.app.composition_root.logger
```

### Phase 4: 既存コードのマイグレーション

#### 4.1 ロガー初期化削除

```python
# ❌ 移行前
import logging
from src.share.logger import setup_logger

logger = setup_logger(__name__)  # 個別初期化

class SomeUseCase:
    def __init__(self):
        self.logger = logger  # グローバルロガー使用

# ✅ 移行後
import logging

class SomeUseCase:
    def __init__(self, logger: logging.Logger):  # DI注入
        self.logger = logger
```

#### 4.2 グローバル変数の削除

```python
# ❌ 移行前
_container = None
_childcare_agent = None

def setup_routes(container, agent):
    global _container, _childcare_agent
    _container = container
    _childcare_agent = agent

@router.post("/api/childcare/chat")
async def childcare_chat(request: ChildcareChatRequest):
    tool = _container.childcare_consultation_tool()  # グローバル変数使用

# ✅ 移行後
from fastapi import Depends
from src.presentation.api.dependencies import get_childcare_tool

@router.post("/api/childcare/chat")
async def childcare_chat(
    request: ChildcareChatRequest,
    tool: ChildcareConsultationTool = Depends(get_childcare_tool),  # DI注入
):
    result = await tool.execute(request.message)
```

#### 4.3 ルート関数の更新

```python
# ❌ 移行前
@router.post("/api/users")
async def create_user(request: CreateUserRequest):
    usecase = _container.user_management_usecase()  # グローバル変数
    result = await usecase.create_user(request.user_data)

# ✅ 移行後
@router.post("/api/users")
async def create_user(
    request: CreateUserRequest,
    usecase: UserManagementUseCase = Depends(get_user_management_usecase),  # DI注入
    logger: logging.Logger = Depends(get_logger),  # ロガーDI注入
):
    logger.info(f"ユーザー作成開始: {request.user_data.get('email')}")
    result = await usecase.create_user(request.user_data)
    logger.info(f"ユーザー作成完了: {result.user_id}")
```

### Phase 5: テストコードの更新

#### 5.1 テスト用CompositionRoot

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from src.di_provider.composition_root import CompositionRoot

@pytest.fixture
def mock_composition_root():
    """テスト用CompositionRoot"""
    mock_root = Mock(spec=CompositionRoot)
    
    # モックサービス設定
    mock_usecase = Mock()
    mock_root._usecases.get_required.return_value = mock_usecase
    
    mock_logger = Mock()
    mock_root.logger = mock_logger
    
    return mock_root

@pytest.fixture
def test_app(mock_composition_root):
    """テスト用FastAPIアプリ"""
    from src.main import app
    
    # テスト用CompositionRootを注入
    app.composition_root = mock_composition_root
    app.logger = mock_composition_root.logger
    
    return app
```

#### 5.2 エンドポイントテスト

```python
# tests/test_user_routes.py
import pytest
from fastapi.testclient import TestClient

def test_create_user(test_app, mock_composition_root):
    """ユーザー作成APIテスト"""
    client = TestClient(test_app)
    
    # モックUseCase設定
    mock_usecase = mock_composition_root._usecases.get_required.return_value
    mock_usecase.create_user.return_value = {"user_id": "test_id"}
    
    # APIテスト実行
    response = client.post(
        "/api/users",
        json={"email": "test@example.com", "name": "Test User"}
    )
    
    assert response.status_code == 200
    assert response.json()["user_id"] == "test_id"
    mock_usecase.create_user.assert_called_once()
```

## 📋 マイグレーションチェックリスト

### ✅ Phase 1: 基盤準備
- [ ] CompositionRootFactory実装
- [ ] CompositionRoot実装  
- [ ] ServiceRegistry実装
- [ ] 依存関係組み立てロジック実装

### ✅ Phase 2: FastAPI統合
- [ ] main.py lifespan実装
- [ ] app.composition_root注入
- [ ] app.logger注入

### ✅ Phase 3: Dependencies実装
- [ ] get_xxx_usecase関数実装
- [ ] get_logger関数実装
- [ ] 認証関連依存関数実装

### ✅ Phase 4: 既存コード移行
- [ ] 個別ロガー初期化削除
- [ ] グローバル変数削除
- [ ] setup_routes関数削除
- [ ] 全ルート関数のDepends追加

### ✅ Phase 5: テスト更新
- [ ] テスト用CompositionRoot実装
- [ ] 既存テストのモック更新
- [ ] 新しいDI統合テスト追加

## ⚡ 移行のコツ

### 1. 段階的移行

```python
# 1段階目: 依存関数のみ作成（既存コードは残す）
def get_user_usecase(request: Request) -> UserManagementUseCase:
    # 新しい実装

# 2段階目: 一部ルートで使用開始
@router.post("/api/users/new")  # 新エンドポイント
async def create_user_new(usecase = Depends(get_user_usecase)):

# 3段階目: 既存ルートを順次移行
@router.post("/api/users")  # 既存エンドポイント更新
async def create_user(usecase = Depends(get_user_usecase)):
```

### 2. テスト駆動移行

```python
# まずテストから移行
def test_create_user_with_di():
    # 新しいDI統合でテスト作成
    pass

# テストが通ったら実装を移行
@router.post("/api/users")
async def create_user(usecase = Depends(get_user_usecase)):
    # DI統合実装
```

### 3. ロギングの段階的移行

```python
# 1段階目: 並行実行（検証）
class SomeUseCase:
    def __init__(self, logger: logging.Logger):
        self.di_logger = logger  # DI注入ロガー
        self.old_logger = setup_logger(__name__)  # 既存ロガー
        
    def some_method(self):
        self.di_logger.info("DI注入ロガー")
        self.old_logger.info("既存ロガー")  # 比較用

# 2段階目: DI注入のみ使用
class SomeUseCase:
    def __init__(self, logger: logging.Logger):
        self.logger = logger  # DI注入のみ
```

## 🎯 まとめ

GenieUsのDI統合マイグレーションは、以下の特徴を持つ実用的なアプローチです：

### **移行の核心価値**
1. **Pure Composition Root**: 外部ライブラリ依存なし
2. **段階的移行**: 既存機能を壊さない安全な移行
3. **テスト容易性**: CompositionRootモック化
4. **型安全**: ServiceRegistryによる型安全な管理
5. **FastAPIネイティブ**: Request経由の自然な統合

### **移行パターン**
```
グローバル変数 → CompositionRoot作成 → FastAPI統合 → Depends移行 → テスト更新
```

この段階的アプローチにより、GenieUsは安全かつ効率的にDI統合への移行を完了しています。

---

**最終更新**: 2025-06-28  
**対応バージョン**: Composition Root + FastAPI Request経由統合