# GieieUs Backend - Agent-First Architecture Design Guidelines

## 概要
Google ADK（Agent Development Kit）を活用した子育て支援AIシステムのバックエンドアーキテクチャ設計指針。
**Agent中心の完全統合アーキテクチャ（2024年12月更新）**を採用。

## 🚨 重要な変更（2024年12月）

**完全なAgent-Firstアーキテクチャに移行**：
- 子育て相談・発達相談・安全性評価・年齢検出はすべて**Gemini-poweredなAgent内で実装**
- Tool/UseCase/Infrastructureは**マルチモーダル技術機能（画像・音声・ファイル・記録）のみ**
- 重複するビジネスロジック実装を完全に排除

## 設計思想

### 1. Agent-First Architecture
- **Agentがビジネスフローの中心**: 従来のWeb API中心からAgentによる判断・ルーティング中心へ
- **LLM-driven Routing**: 複雑な判断はCoordinator Agentが担当、シンプルなルールはApplication層で処理
- **状態管理はADKネイティブ**: `ToolContext.state`、`SessionService`を活用した堅牢な状態管理

### 2. Hybrid Clean Architecture
ADKの利点を活かしつつ、従来のクリーンアーキテクチャの原則を適用：

```
Agent Layer (判断・ルーティング)
    ↓
Tool Layer (アダプター)
    ↓  
Application Layer (ビジネスロジック調整)
    ↓
Domain Layer (ビジネスルール)
    ↓
Infrastructure Layer (外部システム)
```

### 3. 標準化された中間層
- **Pydanticベースの統一レスポンス**: 型安全性とエラーハンドリングの一貫性
- **Tool層の薄いアダプター**: Agent-Application間の変換に特化
- **再利用可能なApplication層**: REST API化も容易

## ディレクトリ構造

### 現在の構成
```
src/
├── agents/                 # エージェント定義
│   ├── childcare/
│   │   ├── __init__.py
│   │   ├── childcare.py       # 子育てエージェント実装
│   │   └── router_agent.py    # マルチエージェントルーティング
│   └── simple_childcare.py    # シンプルエージェント
├── application/            # アプリケーション層
│   ├── config/
│   │   └── constants.py       # アプリケーション定数
│   ├── interface/
│   │   └── protocols/         # インターフェース定義
│   │       ├── agent_gateway.py
│   │       ├── child_carer.py
│   │       └── file_operator.py
│   └── usecases/
│       └── childcare_consultation_usecase.py
├── infrastructure/         # インフラ層
│   ├── adapters/               # 外部システムアダプター
│   │   ├── child_service/
│   │   │   ├── age_detector.py
│   │   │   ├── childcare_adviser.py
│   │   │   └── safety_assessor.py
│   │   ├── google_cloud/
│   │   │   ├── adk_gateway.py    # ADK接続実装
│   │   │   └── file_operator.py
│   │   └── persistence/
│   │       └── __init__.py
│   └── config/
│       └── constants.py
├── presentation/           # プレゼンテーション層
│   ├── api/                   # REST API
│   │   ├── middleware/
│   │   │   └── auth_middleware.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── chat.py        # チャットエンドポイント
│   │       ├── chat_simple.py # テスト用エンドポイント
│   │       └── health.py
│   └── mcp/                   # MCP統合（今後の拡張用）
├── tools/                  # Agent-Application間アダプター
├── config/                 # グローバル設定
│   ├── constants.py
│   └── settings.py            # 環境変数管理
├── share/                  # 共通ユーティリティ
│   ├── exception.py
│   └── logger.py
├── di_provider/            # 依存性注入
│   ├── container.py
│   └── factory.py
└── main.py                 # アプリケーションエントリーポイント
```

### 今後の推奨構成への移行
```
src/
├── agents/                 # そのまま維持
├── tools/                  # Agent向けツール定義を充実
│   ├── childcare/
│   └── calendar/
├── application/            # 現状の構成を維持・拡張
│   ├── interface/          # protocolsからドメイン層へ移行検討
│   └── usecases/           # ビジネスロジック集約
├── domain/                 # 新規作成推奨
│   ├── entities/
│   ├── value_objects/
│   └── repositories/       # interfaceから移行
├── infrastructure/         # adapters構造を維持
│   └── adapters/
├── presentation/           # 現状維持
├── config/                 # 現状維持
├── share/                  # 現状維持
└── di_provider/            # 現状維持
```

## アーキテクチャ原則

### 1. Agent層の責務
- **ルーティング判断**: どの専門エージェントに処理を委譲するか
- **文脈理解**: ユーザーの意図を解釈し適切な処理フローを決定
- **状態管理**: ADKの`SessionService`を活用した会話状態の維持

```python
# src/agents/childcare/router_agent.py
coordinator_agent = Agent(
    name="ChildcareCoordinator",
    instruction="相談内容を分析して適切な専門家にルーティング",
    sub_agents=[sleep_agent, feeding_agent, development_agent]
)
```

### 2. Tool層の責務（薄いアダプター）
- **引数変換**: Agent用パラメータ → Application層用リクエスト
- **戻り値変換**: Application層レスポンス → Agent用自然言語
- **状態連携**: `tool_context.state`による情報共有

```python
# src/tools/calendar_tools.py
from google.adk.tools import FunctionTool
from src.application.usecases.calendar_usecase import CalendarApplicationService
from src.application.dto.calendar_dto import CreateAppointmentRequest

def schedule_appointment_tool(date: str, title: str, tool_context: ToolContext) -> str:
    """Agent用Tool定義 - 薄いアダプターとして機能"""
    # Application層呼び出し（通常のAPI実装）
    app_service = CalendarApplicationService()
    request = CreateAppointmentRequest(date=date, title=title)
    response = app_service.create_appointment(request)
    
    # Agent用レスポンス変換
    if response.status == "success":
        tool_context.state["temp:last_appointment"] = response.data
        return f"予定「{title}」を{date}に作成しました"
    else:
        return f"エラー: {response.message}"

# FunctionTool定義（Agent向け）
appointment_tool = FunctionTool(
    schedule_appointment_tool,
    description="予定を作成します"
)
```

### 3. Application層の責務
- **ビジネスロジック調整**: 複数ドメインの連携処理
- **トランザクション境界**: データ整合性の保証
- **標準化レスポンス**: 統一的なエラーハンドリング
- **Agent非依存**: 通常のAPIサービスとして実装

```python
# src/application/usecases/calendar_usecase.py
class CalendarApplicationService:
    """通常のAPIサービスとして実装 - Agent固有の処理は含まない"""
    
    def __init__(self, calendar_repository, notification_service):
        self.calendar_repository = calendar_repository
        self.notification_service = notification_service
    
    def create_appointment(self, request: CreateAppointmentRequest) -> StandardResponse:
        try:
            # 通常のビジネスロジック
            appointment = Appointment.create(request.date, request.title)
            self.calendar_repository.save(appointment)
            self.notification_service.send_reminder(appointment)
            return StandardResponse(status="success", data=appointment.to_dict())
        except ConflictError as e:
            return StandardResponse(status="error", message=str(e))
```

### 4. 標準化レスポンス形式
```python
class StandardResponse(BaseModel):
    status: Literal["success", "error"]
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    
class CreateAppointmentRequest(BaseModel):
    date: str
    title: str
    user_id: Optional[str] = None
```

## 環境変数管理

### 集約化原則
- **単一の.envファイル**: ルートレベルの`.env.dev`のみ
- **設定クラス経由**: `AppSettings`でPydanticベースの型安全な設定管理
- **ハードコード禁止**: コード内での`os.environ`直接設定を避ける

```python
class AppSettings(BaseSettings):
    # Google Cloud設定
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_GENAI_USE_VERTEXAI: str = "True"
    
    class Config:
        env_file = ".env.dev"
```

## ADKベストプラクティス

### 1. 状態管理
```python
# Tool間でのデータ共有
def tool_1(tool_context: ToolContext):
    tool_context.state["temp:processing_step"] = "verified"
    
def tool_2(tool_context: ToolContext):
    step = tool_context.state.get("temp:processing_step")
    # 確実に前のToolの状態を参照可能
```

### 2. ルーティングパターン
- **Sequential**: 段階的処理（緊急度判定 → 専門家ルーティング）
- **Parallel**: 並列処理（複数視点での情報収集）
- **LLM-driven**: 動的判断によるルーティング

```python
# 総合パイプライン
comprehensive_pipeline = SequentialAgent(
    name="ChildcareConsultationPipeline",
    sub_agents=[triage_agent, coordinator_agent]
)

# 並列情報収集
multi_perspective_agent = ParallelAgent(
    name="MultiPerspectiveConsultation", 
    sub_agents=[sleep_agent, feeding_agent, development_agent]
)
```

### 3. **重要: ADKツール制限の理解**

ADKには以下のツール制限があります：

#### 制限される構成 ❌
```python
# 単一Agent + sub_agents + tools = エラー
agent = Agent(
    name="CoordinatorAgent",
    sub_agents=[sleep_agent, feeding_agent],  # sub_agentsあり
    tools=[google_search]  # toolsあり → エラー: Multiple tools制限
)
```

#### 許可される構成 ✅
```python
# ParallelAgent/SequentialAgentの各sub_agentがツールを持つ = OK
sleep_agent = Agent(name="SleepAgent", tools=[google_search])
feeding_agent = Agent(name="FeedingAgent", tools=[google_search])

parallel_agent = ParallelAgent(
    name="SearchableAgents",
    sub_agents=[sleep_agent, feeding_agent]  # 各sub_agentがツールを持つのはOK
)

# 単一Agent + toolsのみ = OK
simple_agent = Agent(
    name="SimpleAgent", 
    tools=[google_search, custom_tool]  # sub_agentsなしならツールOK
)

# 単一Agent + sub_agentsのみ = OK
coordinator_agent = Agent(
    name="Coordinator",
    sub_agents=[agent1, agent2]  # toolsなしならsub_agentsOK
)
```

#### エラーメッセージ
```
400 INVALID_ARGUMENT: Multiple tools are supported only when they are all search tools.
```

このエラーは`google.genai`ライブラリの制限で、ADKが内部で使用しているため適用されます。

### 4. エラーハンドリング
- **段階的フォールバック**: ADK処理失敗時の適切な代替処理
- **構造化ログ**: `extra`パラメータによる詳細な文脈情報
- **ユーザーフレンドリー**: エラー時も適切な子育て支援メッセージ

## 実装時の注意点

### やること
- ADKネイティブクラス（Agent、SequentialAgent、ParallelAgent）の活用
- Tool層での薄いアダプター実装
- Application層でのビジネスロジック集約（Agent非依存）
- Protocol/Infrastructure層での通常のAPI実装
- Pydanticによる型安全性の確保
- 構造化ログによる適切な監視

### やらないこと
- 各ディレクトリでの.envファイル分散
- Tool層での複雑なビジネスロジック実装
- Agent層でのデータアクセス直接実装
- **Protocol/Infrastructure層でのAgent固有の実装**
- ハードコードされた環境変数設定
- 非構造化エラーメッセージ
- **関数内でのimport文記述** - 例外ケース以外はファイル先頭に配置する

### 重要な設計指針
**Protocol/Infrastructure層はAgent非依存の通常のAPI実装を行い、Agent向けの変換はTool層で実装する**

## DIコンテナ設計パターン（上級者向け）

### 完全デコレーター形式の採用
**推奨**: 全てのプロバイダーを`@providers.Singleton`または`@providers.Factory`で統一

```python
# ✅ 推奨: 完全デコレーター形式
class DIContainer(containers.DeclarativeContainer):
    @providers.Singleton
    def config(self) -> AppSettings:
        """アプリケーション設定"""
        return get_settings()

    @providers.Singleton
    def logger(self) -> logging.Logger:
        """構造化ログ"""
        from src.share.logger import setup_logger
        config = self.config()
        return setup_logger(name=config.APP_NAME, env=config.ENVIRONMENT)

    @providers.Singleton
    def agent_factory(self):
        """エージェントファクトリー"""
        from src.agents.config.agent_factory import AgentFactory
        return AgentFactory(self.tool_registry(), self.logger())
```

**避けるべき**: 混在形式
```python
# ❌ 非推奨: 混在形式（可読性低下）
config = providers.Singleton(get_settings)
agent_factory = providers.Singleton(
    lambda tool_registry, logger: AgentFactory(tool_registry, logger),
    tool_registry=tool_registry,
    logger=logger,
)
```

### 設定ベースエージェント管理パターン

#### 3層アーキテクチャ
```
AgentManager (統一管理)
    ↓
AgentFactory (設定ベース作成)  ← AgentConfigPresets使用
    ↓
ToolRegistry (ツール一元管理)  ← None安全な取得
```

#### 実装例
```python
# AgentManagerでの使用
agent_configs = {
    "childcare": AgentConfigPresets.standard_childcare(),
    "development": AgentConfigPresets.standard_development(),
    "multimodal": AgentConfigPresets.standard_multimodal(),
}

for agent_key, config in agent_configs.items():
    agent = self.agent_factory.create_agent(config)
    self._agents[agent_key] = agent
```

#### パターンの利点
- **設定による制御**: コードを変更せずにツール構成を変更
- **型安全性**: プリセット設定による一貫性保証
- **テスタビリティ**: 各層が独立してテスト可能
- **拡張性**: 新しいエージェントタイプの容易な追加

### ツールレジストリ安全管理パターン

#### None安全なツール取得
```python
def _safe_tool_getter(self, tool_factory, tool_name):
    """ツール取得の安全なラッパー"""
    def get_tool():
        try:
            tool = tool_factory()
            return tool if tool is not None else None
        except Exception as e:
            self.logger.error(f"ツール取得エラー {tool_name}: {e}")
            return None
    return get_tool

def get_tools(self, tool_names: List[str]) -> List[FunctionTool]:
    """Noneセーフなツール取得"""
    tools = []
    for name in tool_names:
        if name in self._tools:
            tool = self._tools[name]()
            if tool is not None:  # Noneチェック
                tools.append(tool)
    return tools
```

#### 設計思想
- **部分的なツール失敗でもシステム継続**
- **存在しないツールは静かに無視**
- **エラー時のグレースフルデグラデーション**

## Import文の配置規約（Claude Codeへの重要な指示）

### 基本原則
**すべてのimport文はファイルの先頭に配置する**

```python
# ✅ 正しい例 - ファイル先頭にすべてのimportを配置
from typing import Dict, Any, Optional
from dataclasses import dataclass
from google.adk.tools import FunctionTool
from google.adk.core import ToolContext
from src.application.interface.protocols.child_carer import ChildCarerProtocol
from src.share.logger import setup_logger

def create_childcare_tool(context: ToolContext) -> FunctionTool:
    """ADK用の子育て相談ツール"""
    # 実装
    pass
```

### 例外パターン（限定的使用）
以下の**特定のケースのみ**関数内importを許可：

#### 1. 循環インポート回避（DIコンテナで必須）
```python
# ✅ DIコンテナでの循環インポート回避
@providers.Singleton
def agent_manager(self):
    # 関数内importで循環インポートを回避
    from src.agents.agent_manager import AgentManager
    return AgentManager(self)
```

#### 2. 重いモジュールの遅延読み込み
```python
# ✅ 重いライブラリの遅延読み込み
@providers.Singleton
def ml_model(self):
    import tensorflow as tf  # 実際に使用されるまで読み込まない
    return tf.keras.models.load_model("model.h5")
```

#### 3. オプショナル依存関係
```python
# ✅ オプショナル依存の処理
def create_cache(self):
    try:
        import redis  # redisが無くても他は動く
        return redis.Redis()
    except ImportError:
        from .mock_cache import MockCache
        return MockCache()
```

#### 4. 条件分岐による動的インポート
```python
# ✅ 環境による動的インポート
def create_database(self):
    config = self.config()
    if config.DB_TYPE == "postgres":
        from .adapters.postgres import PostgresDB
        return PostgresDB()
    else:
        from .adapters.sqlite import SQLiteDB
        return SQLiteDB()
```

### 禁止パターン
```python
# ❌ 通常のケースでの関数内import
def normal_function():
    import json  # これは先頭に書くべき
    return json.loads(data)

# ❌ パフォーマンス重要な関数での毎回import
def process_data(data):
    import pandas as pd  # 毎回importは遅い
    return pd.DataFrame(data)
```

### 判断基準
| ケース | 先頭import | 関数内import | 理由 |
|--------|------------|--------------|------|
| 標準ライブラリ | ✅ | ❌ | 高速・安全 |
| 普通の依存関係 | ✅ | ❌ | 明確性・性能 |
| 循環インポート | ❌ | ✅ | **エラー回避** |
| 重いライブラリ | △ | ✅ | 起動時間短縮 |
| オプショナル依存 | ❌ | ✅ | エラー耐性 |
| 条件分岐インポート | ❌ | ✅ | 柔軟性 |

### 理由
1. **依存関係の明確化**: ファイルを開いた瞬間にすべての依存関係が把握できる
2. **パフォーマンス向上**: 関数呼び出しのたびにimportが実行されることを防ぐ
3. **コードの可読性**: import部分とロジック部分が明確に分離される
4. **ADK開発での重要性**: エージェントやツールの依存関係が明確になる
5. **静的解析の支援**: Ruffやmypyがより効果的に動作する
6. **循環依存の解決**: DIコンテナパターンでは関数内importが必須テクニック

## 今後の拡張性

### 1. マイクロサービス化
- Application層は独立したサービスとしてAPI化可能
- Tool層のアダプターのみ変更で対応

### 2. 多言語対応
- Agent層での言語判定
- Application層は言語非依存
- Infrastructure層でのローカライゼーション

### 3. マルチモーダル対応
- Agent層での入力形式判定（テキスト・音声・画像）
- Tool層での形式変換
- Application層は入力形式非依存

この設計により、ADKの利点を最大限活用しつつ、保守性・テスタビリティ・再利用性を確保した拡張可能なシステムを構築する。