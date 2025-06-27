# Google ADK制約とベストプラクティス

GenieUsプロジェクトにおけるGoogle AI Developer Kit (ADK)の技術制約、制限事項、ベストプラクティス集

## 🎯 概要

Google ADK v1.0.0が2024年に安定版リリースされ、本番環境でのエージェント構築・デプロイに対応しました。しかし、ADKには様々な制約と癖があり、これらを理解せずに開発すると予期しない問題に遭遇します。

## 📋 ADK基本制約

### 🔧 ツール制約

#### ツールレジストリの制限
```python
# ✅ 推奨パターン: 共有レジストリ使用
from google.adk.tools import ToolRegistry

# ツールは共有レジストリに登録し、任意のエージェントからアクセス可能
registry = ToolRegistry()
registry.register("growth_record", growth_record_tool)
registry.register("image_analysis", image_analysis_tool)
```

#### FunctionTool初期化制約
```python
# ❌ 動的ツール作成は不可
# ADKは初期化時に全ツールが確定している必要
agent = Agent(
    tools=[tool1, tool2, tool3],  # ここで全ツールが既に存在している必要
    model="gemini-2.5-flash"
)

# ✅ 正しいパターン: 事前にすべてのツールを準備
all_tools = composition_root.get_all_tools()  # 事前組み立て
agent_manager = AgentManager(tools=all_tools, logger=logger)
```

#### ツール数の実質的制限
- **確認された制限**: エージェント1つあたり多数のツールを持つとパフォーマンスが劣化
- **ベストプラクティス**: エージェント1つあたり3-5個のツールに制限
- **理由**: ツール呼び出しは予想以上にコンピュートを消費

### 🧠 エージェント制約

#### エージェントタイプ別制限

```python
# Sequential Agent制約
sequential_agent = SequentialAgent(
    activities=[activity1, activity2, activity3]  # 最大3つの個別アクティビティ推奨
)

# Parallel Agent制約 
parallel_agent = ParallelAgent(
    agents=[agent1, agent2, agent3],  # 並列実行時のリソース競合に注意
    max_concurrent=2  # 同時実行数制限推奨
)
```

#### メモリ・セッション管理制約

```python
# ローカル開発時: インメモリセッション
session = InMemorySession()

# 本番デプロイ時: クラウドベースマネージドセッション
# ⚠️ 注意: カスタムインメモリセッションは本番で同期されない可能性
```

### 📊 パフォーマンス制約

#### コンピュート消費の問題
```python
# ❌ 非効率的なパターン
def inefficient_workflow():
    # 1. 検索
    search_result = search_tool.execute("子育て情報")
    # 2. 別途要約
    summary = summarize_tool.execute(search_result)
    return summary

# ✅ 効率的なパターン  
def efficient_workflow():
    # 検索と要約を1ステップで実行
    result = search_and_summarize_tool.execute("子育て情報を検索して要約")
    return result
```

## 🏗️ アーキテクチャ制約

### 初期化タイミング制約

#### なぜComposition Rootが必要なのか

```python
# ❌ ADKでは不可能なパターン
# Lazy loadingは初期化タイミング制約で使用不可
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # ADKツール初期化時にLazy loadingが間に合わない
    tool1 = providers.Singleton(Tool1)  # 初期化遅延が問題
    tool2 = providers.Factory(Tool2)    # 実行時作成が不可
```

```python
# ✅ ADK対応パターン: Composition Root
class CompositionRoot:
    def __init__(self):
        # 初期化時に全依存関係を即座に組み立て
        self._build_infrastructure_layer()  # 1. インフラ層
        self._build_application_layer()     # 2. アプリケーション層  
        self._build_tool_layer()            # 3. ツール層（ADK要求）
        
    def get_all_tools(self) -> dict[str, FunctionTool]:
        # エージェント初期化時に全ツールが利用可能
        return self._tools._services
```

### 環境・設定制約

#### .env環境管理の制約

```bash
# ADK プロジェクト構造要求
backend/src/agents/
├── .env                 # ADK固有環境変数
├── init_agents.py      # エージェント初期化制約
├── agent_config.json   # エージェント設定ファイル
└── tools/              # ツール格納制約
```

#### プロセス・ポート制約

```yaml
# ポート分離ルール（GenieUs固有）
開発者ローカル環境:
  フロントエンド: 3000
  バックエンド: 8000

AI開発支援テスト環境:
  フロントエンド: 3001  # 競合回避
  バックエンド: 8001    # 競合回避
```

## 🔍 マルチエージェント制約

### ルーティング制約

```python
# ADK推奨パターン: LLM駆動ルーティング
class RoutingStrategy:
    def route_to_agent(self, message: str) -> str:
        # エージェントの理解と利用可能エージェントの能力に基づいて動的ルーティング
        if "睡眠" in message or "夜泣き" in message:
            return "sleep_specialist_agent"
        elif "栄養" in message or "離乳食" in message:
            return "nutrition_specialist_agent"
        else:
            return "general_childcare_agent"
```

### エージェント間通信制約

```python
# ✅ 構造化ワークフロー（予測可能）
sequential_workflow = SequentialAgent([
    data_retrieval_agent,    # 1. データ取得
    analysis_agent,          # 2. 分析
    reporting_agent          # 3. レポート作成
])

# ✅ 動的LLM駆動ルーティング（適応的）
class DynamicRouter:
    def delegate(self, query: str, available_agents: list):
        # LLMが状況に応じて最適なエージェントを選択
        return llm_driven_delegation(query, available_agents)
```

## 🛡️ セキュリティ・制限制約

### ユーザーID制約
```python
# ユーザーIDは128文字制限
MAX_USER_ID_LENGTH = 128

def validate_user_id(user_id: str) -> bool:
    return len(user_id) <= MAX_USER_ID_LENGTH
```

### Pre-GA制約
```python
# ⚠️ Pre-GA機能の制約
"""
ADKは「Pre-GA Offerings Terms」の対象
- 機能は「現状のまま」提供
- 限定的サポート
- 予期しない変更の可能性
"""
```

## 🎛️ ツール統合制約

### Google Search統合の制約

```python
# ❌ Google Search使用時のツール制約
# Google Search APIを使用するとツール数が制限される場合がある
search_agent = Agent(
    tools=[google_search_tool],  # 他のツールが利用不可になる可能性
    model="gemini-2.5-flash"
)

# ✅ 代替パターン: 専用検索エージェント
search_specialist = Agent(
    tools=[google_search_tool],
    model="gemini-2.5-flash"  
)

general_agent = Agent(
    tools=[other_tools],  # Google Search以外のツール
    model="gemini-2.5-flash"
)
```

### MCP (Model Context Protocol) 制約

```python
# ADKはMCP対応だが制約あり
from google.adk.mcp import MCPTool

# MCP経由でのツール統合
mcp_tool = MCPTool(
    server_url="localhost:8080",
    capabilities=["read", "write"],  # 権限制約
    rate_limit=100  # レート制限適用
)
```

## 📈 パフォーマンス最適化

### トークン使用量管理

```python
# ✅ トークン予算設定
class TokenBudgetManager:
    def __init__(self):
        self.per_agent_limit = 10000    # エージェント毎制限
        self.per_user_limit = 50000     # ユーザー毎制限
        
    def check_budget(self, agent_id: str, user_id: str) -> bool:
        # 使用量監視とブロック機能
        return self.get_usage(agent_id, user_id) < self.get_limit(agent_id, user_id)
```

### ツール呼び出し最適化

```python
# ✅ ベストプラクティス: ツールの統合
def create_efficient_tools():
    # 複数ステップを1つのツールにまとめる
    search_and_analyze_tool = CombinedTool([
        search_component,
        analysis_component,
        summary_component
    ])
    
    return [search_and_analyze_tool]  # 個別ツールより効率的
```

## 🧪 開発・デバッグ制約

### ローカル開発制約

```python
# ADK Web UI起動制約
"""
backend/src/agents/$ adk web
- ポート8000がデフォルト
- FastAPIと競合する可能性
- ディレクトリ構造依存
"""

# ✅ 競合回避パターン
def start_adk_with_port_separation():
    # ADK Web UI: ポート8001
    # FastAPI: ポート8000  
    # フロントエンド: ポート3000
    subprocess.run(["adk", "web", "--port", "8001"])
```

### エラーハンドリング制約

```python
# ADK特有のエラーハンドリング
try:
    result = agent.execute(query)
except ADKToolExecutionError as e:
    # ツール実行エラー: 段階的フォールバック必要
    logger.error(f"ツール実行失敗: {e}")
    return fallback_response(query)
except ADKSessionExpiredError as e:
    # セッション期限切れ: 新規セッション作成
    logger.warning(f"セッション期限切れ: {e}")
    return restart_session_and_retry(query)
```

## 📋 開発チェックリスト

### 設計段階
- [ ] エージェント1つあたりのツール数を3-5個に制限
- [ ] 複数ステップのワークフローを1つのツールに統合できないか検討
- [ ] ツール呼び出し頻度を最小化する設計
- [ ] メモリ・セッション管理戦略の決定

### 実装段階  
- [ ] Composition Rootパターンでの事前ツール組み立て
- [ ] ADK初期化タイミング制約への対応
- [ ] 段階的エラーハンドリングの実装
- [ ] トークン使用量監視の実装

### テスト段階
- [ ] ローカル（インメモリ）とクラウド（マネージド）セッション両方でテスト
- [ ] ツール実行失敗時のフォールバック動作確認
- [ ] パフォーマンス負荷テスト（ツール呼び出し頻度）
- [ ] ポート競合回避の確認

### 本番デプロイ段階
- [ ] Pre-GA制約の承認とリスク評価
- [ ] トークン予算とコスト監視の設定
- [ ] セッション同期の確認（カスタムセッション使用時）
- [ ] スケーリング制約の確認

## 🚨 よくある問題と解決策

### 問題1: ツール初期化タイミングエラー
```python
# ❌ 問題コード
def setup_agent():
    agent = Agent(model="gemini-2.5-flash")
    agent.add_tool(create_tool())  # 実行時追加は不可

# ✅ 解決策
def setup_agent():
    tools = [create_tool1(), create_tool2()]  # 事前作成
    agent = Agent(tools=tools, model="gemini-2.5-flash")
```

### 問題2: Google Search + 他ツール競合
```python
# ❌ 問題パターン
agent = Agent(
    tools=[google_search_tool, image_analysis_tool, record_tool],  # 競合
    model="gemini-2.5-flash"
)

# ✅ 解決策: エージェント分離
search_agent = Agent(tools=[google_search_tool], model="gemini-2.5-flash")
general_agent = Agent(tools=[image_analysis_tool, record_tool], model="gemini-2.5-flash")
```

### 問題3: セッション同期エラー
```python
# ✅ 解決策: セッション戦略の統一
class SessionManager:
    def get_session(self, environment: str):
        if environment == "local":
            return InMemorySession()
        else:
            return CloudManagedSession()  # 本番では統一
```

## 🔗 関連ドキュメント

- [アーキテクチャ概要](../architecture/overview.md) - ADK統合設計
- [Composition Root設計](../architecture/composition-root-design.md) - ADK制約対応パターン
- [新エージェント作成ガイド](../guides/new-agent-creation.md) - ADK制約下での実装手順
- [エラーハンドリング戦略](./error-handling.md) - ADK特有のエラー対応

---

**💡 重要**: ADKは高性能なマルチエージェントシステムを構築できる優れたフレームワークですが、これらの制約を理解せずに使用すると、パフォーマンス問題やアーキテクチャの複雑化を招きます。制約を受け入れ、それに合わせた設計を行うことが成功の鍵です。