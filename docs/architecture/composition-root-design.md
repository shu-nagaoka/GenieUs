# Composition Root設計パターン

GenieUsプロジェクトのComposition Root Pattern - 中央集約型依存関係組み立て設計

## 🎯 Composition Rootとは

**Composition Root**は、アプリケーションの依存関係をたった1箇所（main.py）で組み立てる設計パターンです。

### 基本概念

```
main.py (唯一の組み立て場所)
    ↓
CompositionRoot (純粋な依存関係組み立て)
    ↓
FastAPI + AgentManager (実行時コンポーネント)
```

### 従来のDIContainerからの進化

```python
# ❌ 旧パターン: DIContainer（複雑・providers.Self問題）
class DIContainer(containers.DeclarativeContainer):
    config = providers.Singleton(get_settings)
    logger = providers.Singleton(setup_logger)
    # 100行以上の複雑な設定...

# ✅ 新パターン: CompositionRoot（シンプル・Pure組み立て）
class CompositionRoot:
    def __init__(self, settings: AppSettings, logger: logging.Logger):
        self.settings = settings
        self.logger = logger
        self._build_infrastructure_layer()
        self._build_application_layer()
        self._build_tool_layer()
```

## 🏗️ アーキテクチャ概要

### レイヤー構成と組み立て順序

```
1. Infrastructure Layer (外部システム連携)
   ↓ 依存関係注入
2. Application Layer (UseCase - ビジネスロジック)
   ↓ 依存関係注入
3. Tool Layer (ADK FunctionTool - Agent用アダプター)
   ↓ 統合
4. Agent Layer (AgentManager - AI判断・ルーティング)
```

### main.pyでの中央集約組み立て

```python
# src/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pure CompositionRoot Pattern"""
    
    # 🎯 1. CompositionRoot一元初期化（アプリケーション全体で1度だけ）
    composition_root = CompositionRootFactory.create()
    
    # 🎯 2. AgentManagerに必要なツールのみ注入
    all_tools = composition_root.get_all_tools()
    agent_manager = AgentManager(
        tools=all_tools, 
        logger=composition_root.logger, 
        settings=composition_root.settings
    )
    agent_manager.initialize_all_components()
    
    # 🎯 3. FastAPIアプリには必要なコンポーネントのみ注入
    app.agent_manager = agent_manager
    app.logger = composition_root.logger
    app.composition_root = composition_root
    
    yield
```

## 💉 CompositionRoot実装詳細

### CompositionRootFactory

```python
# src/di_provider/composition_root.py
class CompositionRootFactory:
    """CompositionRoot作成ファクトリー - Pure依存性組み立て"""

    @staticmethod
    def create(settings: AppSettings | None = None, logger: logging.Logger | None = None) -> "CompositionRoot":
        """CompositionRoot作成（本番・テスト統一）"""
        settings = settings or get_settings()
        logger = logger or setup_logger(name=settings.APP_NAME, env=settings.ENVIRONMENT)
        return CompositionRoot(settings=settings, logger=logger)
```

### CompositionRoot構造

```python
class CompositionRoot:
    """アプリケーション全体の依存関係組み立て（main.py中央集約）"""
    
    def __init__(self, settings: AppSettings, logger: logging.Logger):
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

### 層別組み立て実装

#### 1. Infrastructure層組み立て

```python
def _build_infrastructure_layer(self) -> None:
    """Infrastructure層組み立て"""
    
    # Repository Factory
    repository_factory = MemoryRepositoryFactory()
    self._infrastructure.register("repository_factory", repository_factory)
    
    # File Operator
    file_operator = GcsFileOperator(
        project_id=self.settings.GOOGLE_CLOUD_PROJECT, 
        logger=self.logger
    )
    self._infrastructure.register("file_operator", file_operator)
    
    # AI Analyzers
    image_analyzer = GeminiImageAnalyzer(logger=self.logger)
    voice_analyzer = GeminiVoiceAnalyzer(logger=self.logger)
    
    self._infrastructure.register("image_analyzer", image_analyzer)
    self._infrastructure.register("voice_analyzer", voice_analyzer)
    
    # Family Repository
    family_repository = FamilyRepository(logger=self.logger)
    self._infrastructure.register("family_repository", family_repository)
```

#### 2. Application層組み立て

```python
def _build_application_layer(self) -> None:
    """Application層組み立て（UseCase）"""
    
    # Infrastructure依存関係取得
    image_analyzer = self._infrastructure.get_required("image_analyzer")
    voice_analyzer = self._infrastructure.get_required("voice_analyzer")
    file_operator = self._infrastructure.get_required("file_operator")
    repository_factory = self._infrastructure.get_required("repository_factory")
    family_repository = self._infrastructure.get_required("family_repository")
    
    # UseCases組み立て
    image_analysis_usecase = ImageAnalysisUseCase(
        image_analyzer=image_analyzer, 
        logger=self.logger
    )
    
    voice_analysis_usecase = VoiceAnalysisUseCase(
        voice_analyzer=voice_analyzer, 
        logger=self.logger
    )
    
    # ... 他のUseCase組み立て
    
    # UseCase登録
    self._usecases.register("image_analysis", image_analysis_usecase)
    self._usecases.register("voice_analysis", voice_analysis_usecase)
    # ...
```

#### 3. Tool層組み立て

```python
def _build_tool_layer(self) -> None:
    """Tool層組み立て（ADK FunctionTool）"""
    
    # 画像分析ツール
    image_usecase = self._usecases.get_required("image_analysis")
    image_tool = self._create_image_analysis_tool(image_usecase)
    self._tools.register("image_analysis", image_tool)
    
    # 音声分析ツール
    voice_usecase = self._usecases.get_required("voice_analysis")
    voice_tool = self._create_voice_analysis_tool(voice_usecase)
    self._tools.register("voice_analysis", voice_tool)
    
    # ... 他のツール組み立て

def _create_image_analysis_tool(self, usecase: ImageAnalysisUseCase) -> FunctionTool:
    """画像分析ツール作成"""
    from src.tools.image_analysis_tool import create_image_analysis_tool
    return create_image_analysis_tool(image_analysis_usecase=usecase, logger=self.logger)
```

## 🔄 DIContainerからの移行

### 移行の理由

```
❌ DIContainer問題点:
- providers.Self()の循環参照問題
- 複雑すぎる設定ファイル（100行以上）
- 型安全性の不足
- テスト時のモック注入困難

✅ CompositionRoot利点:
- 純粋なPython組み立て（循環参照なし）
- シンプルで理解しやすい
- 完全な型安全性
- テスト時の柔軟なモック注入
```

### 移行手順

```python
# STEP 1: CompositionRootFactory作成
composition_root = CompositionRootFactory.create()

# STEP 2: AgentManagerでツール統合
all_tools = composition_root.get_all_tools()
agent_manager = AgentManager(tools=all_tools, logger=composition_root.logger)

# STEP 3: FastAPIへ必要最小限のコンポーネント注入
app.agent_manager = agent_manager
app.composition_root = composition_root  # UseCase直接アクセス用
```

### 旧DIContainerパターン除去

```python
# ❌ 削除されたパターン
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

# DIContainer定義
class DIContainer(containers.DeclarativeContainer):
    # 複雑な設定...

# グローバル変数
_container = None
_agent = None

# setup_routes関数
def setup_routes(container, agent):
    global _container, _agent
    _container = container
    _agent = agent

# FastAPI Depends
@inject
async def endpoint(
    tool = Depends(Provide[DIContainer.some_tool])
):
    pass
```

## 🤖 AgentManager統合

### CompositionRoot + AgentManager連携

```python
# src/agents/agent_manager.py
class AgentManager:
    """Agent中心のコンポーネント管理（CompositionRoot統合）"""
    
    def __init__(self, tools: dict[str, FunctionTool], logger: logging.Logger, settings: AppSettings):
        """CompositionRootから必要なコンポーネントのみ注入"""
        self.tools = tools
        self.logger = logger
        self.settings = settings
        self._agents: dict[str, Agent] = {}
    
    def initialize_all_components(self) -> None:
        """全エージェント初期化（CompositionRootパターン）"""
        self.logger.info("AgentManager初期化開始（CompositionRoot統合）")
        
        try:
            # 基本子育てエージェント
            self._initialize_childcare_agent()
            
            # 将来の専門エージェント
            # self._initialize_nutrition_agent()
            # self._initialize_sleep_agent()
            
            self.logger.info(f"AgentManager初期化完了: {len(self._agents)}個のエージェント")
            
        except Exception as e:
            self.logger.error(f"AgentManager初期化エラー: {e}")
            raise
    
    def _initialize_childcare_agent(self) -> None:
        """基本子育てエージェント初期化"""
        from src.agents.di_based_childcare_agent import get_childcare_agent
        
        # CompositionRootから注入されたツールを使用
        image_tool = self.tools.get("image_analysis")
        voice_tool = self.tools.get("voice_analysis") 
        file_tool = self.tools.get("file_management")
        record_tool = self.tools.get("record_management")
        
        agent = get_childcare_agent(
            agent_type="simple",
            image_analysis_tool=image_tool,
            voice_analysis_tool=voice_tool,
            file_management_tool=file_tool,
            record_management_tool=record_tool,
            logger=self.logger
        )
        
        self._agents["childcare"] = agent
        self.logger.info("子育てエージェント初期化完了（CompositionRoot統合）")
```

## 🌐 API統合パターン

### FastAPI Endpoint実装

```python
# src/presentation/api/routes/multiagent_chat.py
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/multiagent/chat")
async def multiagent_chat_endpoint(request: Request, chat_request: ChatRequest):
    """マルチエージェントチャット（CompositionRoot統合）"""
    
    # CompositionRootから注入されたコンポーネント使用
    agent_manager = request.app.agent_manager
    logger = request.app.logger
    
    try:
        logger.info(f"マルチエージェントチャット開始: user={chat_request.user_id}")
        
        # AgentManagerでルーティング・実行
        response = agent_manager.route_and_execute(
            message=chat_request.message,
            user_id=chat_request.user_id,
            session_id=chat_request.session_id,
            conversation_history=chat_request.conversation_history,
            multimodal_context=chat_request.multimodal_context
        )
        
        return ChatResponse(response=response, ...)
        
    except Exception as e:
        logger.error(f"マルチエージェントチャットエラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 家族管理UseCase直接アクセス

```python
# src/presentation/api/routes/family.py
@router.post("/family")
async def create_family_endpoint(request: Request, family_request: FamilyRequest):
    """家族作成（CompositionRoot統合）"""
    
    # CompositionRootから直接UseCase取得
    composition_root = request.app.composition_root
    family_usecase = composition_root._usecases.get_required("family_management")
    logger = request.app.logger
    
    try:
        result = family_usecase.create_family(family_request)
        return FamilyResponse(result=result, ...)
        
    except Exception as e:
        logger.error(f"家族作成エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## ✅ テスト統合

### テスト用CompositionRoot

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from src.di_provider.composition_root import CompositionRootFactory

@pytest.fixture
def test_composition_root():
    """テスト用CompositionRoot作成"""
    # モックロガーでテスト環境構築
    mock_logger = Mock()
    return CompositionRootFactory.create(logger=mock_logger)

@pytest.fixture
def test_agent_manager(test_composition_root):
    """テスト用AgentManager作成"""
    from src.agents.agent_manager import AgentManager
    
    tools = test_composition_root.get_all_tools()
    return AgentManager(
        tools=tools,
        logger=test_composition_root.logger,
        settings=test_composition_root.settings
    )
```

### 統合テスト例

```python
# tests/test_composition_root_integration.py
def test_composition_root_integration(test_composition_root):
    """CompositionRoot統合テスト"""
    
    # 全ツール取得確認
    tools = test_composition_root.get_all_tools()
    
    assert "image_analysis" in tools
    assert "voice_analysis" in tools
    assert "file_management" in tools
    assert "record_management" in tools
    
    # ツール実行確認
    image_tool = tools["image_analysis"]
    result = image_tool.func(
        image_path="/test/path.jpg",
        analysis_prompt="テスト分析プロンプト"
    )
    
    assert result["success"] is True

def test_agent_manager_composition_root_integration(test_agent_manager):
    """AgentManager + CompositionRoot統合テスト"""
    
    # エージェント初期化確認
    test_agent_manager.initialize_all_components()
    
    # エージェント取得確認
    childcare_agent = test_agent_manager.get_agent("childcare")
    assert childcare_agent is not None
    assert len(childcare_agent.tools) > 0
    
    # マルチモーダルルーティング確認
    response = test_agent_manager.route_and_execute(
        message="子育ての相談です",
        user_id="test_user",
        session_id="test_session"
    )
    
    assert len(response) > 0
```

## 📋 移行チェックリスト

### ✅ CompositionRoot実装確認
- [ ] **CompositionRootFactory実装済み**
- [ ] **層別組み立て実装済み**（Infrastructure→Application→Tool）
- [ ] **ServiceRegistry型安全性確保済み**
- [ ] **main.pyでの中央集約組み立て実装済み**

### ✅ DIContainer除去確認
- [ ] **DIContainer定義削除済み**
- [ ] **providers設定削除済み**
- [ ] **@inject + Depends(Provide[])削除済み**
- [ ] **グローバル変数削除済み**（_container, _agent等）
- [ ] **setup_routes関数削除済み**

### ✅ AgentManager統合確認
- [ ] **CompositionRootからツール注入実装済み**
- [ ] **AgentManager初期化統合済み**
- [ ] **FastAPIアプリ関連付け実装済み**
- [ ] **API Endpoint統合済み**

### ✅ テスト統合確認
- [ ] **テスト用CompositionRoot実装済み**
- [ ] **統合テスト実装済み**
- [ ] **モック注入機能確認済み**

## 🔗 関連ドキュメント

- [アーキテクチャ概要](./overview.md) - 全体設計理解
- [新エージェント作成ガイド](../guides/new-agent-creation.md) - CompositionRoot統合手順
- [コーディング規約](../development/coding-standards.md) - 実装規約
- [ADKベストプラクティス](../technical/adk-best-practices.md) - ADK制約・パターン

---

**💡 重要**: CompositionRootパターンは、アプリケーションの依存関係をmain.py 1箇所で純粋に組み立てることで、複雑性を大幅に削減し、テスタビリティと保守性を向上させます。DIContainerの問題を根本解決する核心パターンです。