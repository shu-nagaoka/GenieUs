# 新エージェント作成ガイド（V2分割アーキテクチャ対応）

**「ADKファースト × CompositionRoot統合 - 最新アーキテクチャ対応エージェント作成」**

GenieUs V2分割アーキテクチャとADKルーティング統合システムでの新エージェント作成完全ガイド

## 🏗️ 現在のエージェント管理システム

GenieUsでは**2つのエージェントシステム**が統合されています：

### 🎯 システム構成概要

```
【AgentManager V2 - 分割アーキテクチャ】
├── AgentRegistry（Agent管理）      ← Google ADK Agent使用
├── MessageProcessor（メッセージ処理）
├── RoutingExecutor（実行管理）
├── RoutingStrategy（戦略選択）
└── AdkRoutingCoordinator          ← Google ADK LlmAgent使用
```

### 📊 2つのエージェントシステム

#### 1. **ADKルーティングシステム**（推奨）
- **使用クラス**: `LlmAgent`（Google ADK）
- **ルーティング**: `transfer_to_agent()`による自動転送
- **管理**: `AdkRoutingCoordinator`
- **特徴**: ADK標準パターン、シンプル、高性能

#### 2. **従来型分割システム**
- **使用クラス**: `Agent`（Google ADK）
- **ルーティング**: `RoutingStrategy`による選択
- **管理**: `AgentRegistry` + `RoutingExecutor`
- **特徴**: 詳細制御、複雑なワークフロー対応

## 🚀 パターン1: ADKルーティングシステム（推奨）

### 📋 基本概念

ADK標準の`LlmAgent`と`transfer_to_agent()`を使用した最もシンプルで効果的な方法：

```python
# コーディネーターが適切な専門エージェントに自動転送
coordinator_agent = LlmAgent(
    name="コーディネーター",
    model="gemini-2.5-flash",
    instruction="適切な専門エージェントに転送してください",
    sub_agents=[specialist1, specialist2, ...]
)
```

### 🔧 実装手順

#### Step 1: 専門エージェント作成

```python
# backend/src/agents/adk_routing_coordinator.py 内で追加

def create_new_specialist_agent(self) -> LlmAgent:
    """新しい専門エージェントを作成"""
    
    # 専門エージェント用プロンプト
    specialist_instruction = """あなたは[専門領域]に特化した専門エージェントです。

## 専門領域
- [具体的な専門分野の説明]
- [対象年齢・状況]
- [提供するサービス内容]

## 重要指針
1. **年齢適応**: 子どもの月齢・年齢を必ず考慮
2. **安全最優先**: リスクを常に評価  
3. **実践的指導**: 具体的で実行可能なアドバイス
4. **緊急時対応**: 危険な状況は医療機関への相談を推奨

{FAMILY_RECOGNITION_INSTRUCTION}

温かく、専門的で信頼できるアドバイスを提供してください。
"""

    # ツールが必要な場合は追加
    tools = []
    if self._requires_tools():
        tools = [
            self.tools.get("image_analysis_tool"),
            self.tools.get("search_tool"),
            # 必要なツールを追加
        ]

    specialist_agent = LlmAgent(
        name="NewSpecialistAgent",  # エージェント名
        model="gemini-2.5-flash",   # ADK推奨モデル
        instruction=specialist_instruction,
        tools=tools if tools else None
    )
    
    return specialist_agent
```

#### Step 2: コーディネーターに専門エージェント追加

```python
# backend/src/agents/adk_routing_coordinator.py

class AdkRoutingCoordinator:
    def add_new_specialist(self) -> None:
        """新しい専門エージェントを動的追加"""
        
        # 新しい専門エージェント作成
        new_specialist = self.create_new_specialist_agent()
        
        # specialist_agentsに追加
        self.specialist_agents["new_specialist"] = new_specialist
        
        # コーディネーターエージェントを再作成（sub_agents更新）
        self.coordinator_agent = self._create_coordinator_agent()
        
        self.logger.info("✅ 新規専門エージェント追加完了: new_specialist")
```

#### Step 3: コーディネーター指示文更新

```python
# _create_coordinator_agent() 内の instruction に追加

def _create_coordinator_agent(self) -> LlmAgent:
    instruction = f"""あなたは子育て相談専門のルーティングコーディネーターです。

**重要**: 必ず適切な専門エージェントに transfer_to_agent() で転送してください。

利用可能な専門エージェント:
{self._build_specialist_descriptions()}

**転送例**:
- 新しい相談 → transfer_to_agent('NewSpecialistAgent')
- [既存の転送例...]

**動作確認**: 全ての応答は transfer_to_agent() 関数呼び出しである必要があります。
"""
    
    # sub_agentsリストに新しいエージェントが自動で含まれる
    sub_agents_list = list(self.specialist_agents.values())
    
    coordinator = LlmAgent(
        name="GenieUs子育てコーディネーター",
        model="gemini-2.5-flash",
        instruction=instruction,
        sub_agents=sub_agents_list
    )
    
    return coordinator
```

#### Step 4: CompositionRootでの統合

```python
# backend/src/di_provider/composition_root.py

class CompositionRoot:
    def get_adk_routing_coordinator(self) -> AdkRoutingCoordinator:
        """ADKルーティングコーディネーター取得"""
        
        if not hasattr(self, '_adk_coordinator'):
            # 既存の専門エージェント取得
            specialist_agents = self._create_specialist_agents_for_adk()
            
            # ADKコーディネーター作成
            self._adk_coordinator = AdkRoutingCoordinator(
                specialist_agents=specialist_agents,
                logger=self.logger,
                tools=self.get_all_tools()
            )
            
            # 新しい専門エージェントを追加
            self._adk_coordinator.add_new_specialist()
        
        return self._adk_coordinator
```

### ✅ ADKルーティングシステムの利点

- **シンプル**: 最小限のコード変更
- **自動ルーティング**: LLMが適切な専門家を自動選択
- **ADK標準**: Googleベストプラクティス準拠
- **高性能**: transfer_to_agent()による効率的転送

## 🔧 パターン2: 従来型分割システム

より詳細な制御が必要な場合は、AgentRegistry経由での追加も可能です。

### 📋 実装手順

#### Step 1: constants.py更新

```python
# backend/src/agents/constants.py

# 新しいエージェントプロンプト
NEW_SPECIALIST_PROMPT = """新しい専門エージェントのプロンプト内容...

{FAMILY_RECOGNITION_INSTRUCTION}
"""

# プロンプトマッピングに追加
AGENT_PROMPTS = {
    # ... 既存エージェント
    "new_specialist": NEW_SPECIALIST_PROMPT,
}

# ツール使用エージェントの場合
TOOL_ENABLED_AGENTS = {
    # ... 既存エージェント
    "new_specialist": ["image_analysis", "search"],  # 必要なツールを指定
}

# 表示名追加
AGENT_DISPLAY_NAMES = {
    # ... 既存エージェント
    "new_specialist": "新規専門家",
}
```

#### Step 2: RoutingStrategy更新

```python
# backend/src/agents/routing_strategy.py

class KeywordRoutingStrategy(RoutingStrategy):
    def _get_agent_keywords(self) -> Dict[str, List[str]]:
        """エージェント別キーワードマッピング"""
        return {
            # ... 既存エージェント
            "new_specialist": ["新しいキーワード", "専門分野"],
        }
    
    def _determine_specialist_agent(self, message_lower: str) -> Tuple[str, Dict]:
        """専門エージェント決定（新エージェントも自動対応）"""
        # constants.pyのAGENT_PROMPTSから自動読み込み
        # 新しいエージェントが自動的に認識される
```

#### Step 3: 動作確認

```bash
# 開発サーバー起動
./scripts/start-dev.sh

# エージェント初期化確認
grep "new_specialist" backend/logs/app.log

# 期待されるログ:
# INFO - エージェント作成完了: new_specialist
# INFO - AgentRegistry初期化完了: XX個のエージェント
```

## 🎯 CompositionRoot DI統合パターン

### 📋 最新のDI統合方法

```python
# backend/src/main.py

def main():
    """メインエントリーポイント - Composition Root統合"""
    
    # Composition Root初期化
    composition_root = CompositionRootFactory.create()
    
    # FastAPIアプリケーションに注入
    app.composition_root = composition_root
    app.logger = composition_root.logger
    
    # AgentManager V2作成（分割アーキテクチャ）
    agent_manager = AgentManager(
        tools=composition_root.get_all_tools(),
        logger=composition_root.logger,
        settings=composition_root.settings,
        routing_strategy=composition_root.get_routing_strategy(),
        agent_registry=composition_root.get_agent_registry()  # 注入
    )
    
    # ADKルーティングコーディネーター統合
    adk_coordinator = composition_root.get_adk_routing_coordinator()
    
    # 統合システム初期化
    agent_manager.initialize_all_components()
    
    return agent_manager, adk_coordinator

# FastAPI Depends統合例
# backend/src/presentation/api/dependencies.py
def get_some_usecase(request: Request) -> SomeUseCase:
    """UseCaseをCompositionRoot経由で取得"""
    composition_root = request.app.composition_root
    return composition_root._usecases.get_required("some_usecase")

# ルートでの使用例
@router.post("/api/endpoint")
async def some_endpoint(
    usecase: SomeUseCase = Depends(get_some_usecase),
):
    """CompositionRoot統合のFastAPI Depends使用例"""
    return await usecase.execute()
```

### 🔧 DI統合の重要原則

1. **ロガーDI注入**: `setup_logger()`個別呼び出し禁止
2. **Composition Root統合**: 中央集約型依存関係組み立て
3. **FastAPI Depends統合**: `request.app.composition_root`経由での依存注入
4. **グローバル変数禁止**: すべてCompositionRoot経由

## 📊 使い分けガイド

### 🎯 ADKルーティングシステムを選ぶ場合

- ✅ **シンプルな専門エージェント**
- ✅ **標準的な子育て相談対応**
- ✅ **迅速な実装が必要**
- ✅ **ADK標準パターンを使いたい**

### 🔧 従来型分割システムを選ぶ場合

- ✅ **複雑なワークフローが必要**
- ✅ **詳細なルーティング制御が必要**
- ✅ **Sequential/Parallelパイプライン使用**
- ✅ **カスタムルーティング戦略実装**

## 🔍 実装例: 睡眠専門エージェント拡張

### ADKルーティング版

```python
# 睡眠専門エージェントに新機能追加
def create_advanced_sleep_specialist(self) -> LlmAgent:
    """高度な睡眠分析機能を持つ専門エージェント"""
    
    instruction = """あなたは睡眠とお昼寝の専門エージェントです。

## 高度な専門機能
- 睡眠パターン分析
- 個別睡眠計画作成
- 環境最適化アドバイス
- 成長段階別睡眠指導

## 利用可能なツール
1. **voice_analysis_tool**: 泣き声パターン分析
2. **record_management_tool**: 睡眠記録分析
3. **search_tool**: 最新睡眠研究情報

{FAMILY_RECOGNITION_INSTRUCTION}

科学的根拠に基づく、個別化された睡眠改善アドバイスを提供してください。
"""

    tools = [
        self.tools.get("voice_analysis_tool"),
        self.tools.get("record_management_tool"),
        self.tools.get("search_tool"),
    ]

    return LlmAgent(
        name="AdvancedSleepSpecialist",
        model="gemini-2.5-flash",
        instruction=instruction,
        tools=[tool for tool in tools if tool is not None]
    )
```

## 📋 チェックリスト

### ✅ ADKルーティングシステム実装チェック

- [ ] **専門エージェント作成完了**（LlmAgent使用）
- [ ] **AdkRoutingCoordinatorに追加完了**
- [ ] **コーディネーター指示文更新完了**
- [ ] **CompositionRoot統合完了**
- [ ] **transfer_to_agent()動作確認**

### ✅ 従来型分割システム実装チェック

- [ ] **constants.py更新完了**（プロンプト、ツール、表示名）
- [ ] **RoutingStrategy対応確認**
- [ ] **AgentRegistry自動認識確認**
- [ ] **動作テスト通過**

### ✅ 品質・規約チェック

- [ ] **型アノテーション完備**
- [ ] **エラーハンドリング実装**
- [ ] **ロガーDI注入実装**（個別初期化禁止）
- [ ] **import文がファイル先頭配置**
- [ ] **Composition Rootパターン使用**

### ✅ 禁止事項回避チェック

- [ ] **個別エージェントファイル作成していない**
- [ ] **setup_logger()個別呼び出ししていない**
- [ ] **グローバル変数を使用していない**
- [ ] **setup_routes関数を使用していない**

## 🔗 関連ドキュメント

- **[AgentManager分割アーキテクチャガイド](agent-manager-architecture-guide.md)** - V2分割システム詳細
- **[コーディング規約](../development/coding-standards.md)** - 実装規約・DI統合
- **[アーキテクチャ概要](../architecture/overview.md)** - ADKファースト設計思想
- **[Composition Root設計](../architecture/composition-root-design.md)** - DI統合パターン
- **[ADKベストプラクティス](../technical/adk-best-practices.md)** - ADK制約・推奨パターン

## 🎯 まとめ

### **V2分割アーキテクチャ**の特徴

1. **2つのエージェントシステム統合**
   - ADKルーティング（推奨）: LlmAgent + transfer_to_agent()
   - 従来型分割: Agent + RoutingStrategy

2. **CompositionRoot DI統合**
   - 中央集約型依存関係組み立て
   - ロガー・ツール・設定のDI注入
   - グローバル変数完全排除

3. **責務明確化**
   - AgentRegistry: エージェント管理
   - MessageProcessor: メッセージ処理
   - RoutingExecutor: 実行管理
   - RoutingStrategy: 戦略選択

### **推奨開発フロー**

```
1. ADKルーティングで実装 → 2. 動作確認 → 3. 必要に応じて従来型拡張
```

この最新アーキテクチャにより、GenieUsはより保守しやすく、拡張しやすく、テストしやすいエージェントシステムを実現しています。

---

**最終更新**: 2025-06-28  
**対応バージョン**: V2分割アーキテクチャ + ADKルーティング統合