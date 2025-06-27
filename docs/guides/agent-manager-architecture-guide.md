# Agent Manager分割アーキテクチャガイド

**「モノリスから専門コンポーネントへ - 責務分離による保守性向上」**

GenieUsのAgent Managerは、単一の巨大クラスから機能別に分離された専門コンポーネントアーキテクチャに再設計されました。このドキュメントでは、その分割設計と各コンポーネントの責務を詳しく解説します。

## 🎯 分割の目的と背景

### 分割前の課題
```
【Agent Manager（モノリス）】
├── エージェント初期化
├── Runner管理
├── メッセージ処理
├── ルーティング実行
├── コンテキスト管理
├── フォールバック処理
├── フォローアップ質問生成
├── セッション管理
└── レスポンス処理
```

**課題:**
- 単一クラスに責務が集中（1000行超）
- テストが困難
- 機能追加時の影響範囲が不明確
- 個別機能の再利用ができない

### 分割後のアーキテクチャ
```
【Agent Manager V2（軽量統合インターフェース）】
├── AgentRegistry（エージェント管理）
├── MessageProcessor（メッセージ処理）
├── RoutingExecutor（ルーティング実行）
└── RoutingStrategy（ルーティング戦略）
```

## 🏗️ コンポーネント詳細解説

### 1. AgentRegistry - エージェント初期化とRunner管理

**ファイル:** `backend/src/agents/agent_registry.py`

**責務:**
- 18専門エージェントの初期化
- Sequential/Parallelパイプラインの構築
- Runner管理
- エージェント情報の提供

#### 主要機能

##### ① 18専門エージェントの統一初期化
```python
def _create_all_specialist_agents(self) -> None:
    """18専門エージェント一括作成"""
    # 全エージェントを統一的に作成
    for agent_id, prompt in AGENT_PROMPTS.items():
        try:
            self._create_single_agent(agent_id, prompt)
            self._created_agents.add(agent_id)
        except Exception as e:
            self._failed_agents.add(agent_id)
```

##### ② モデル選択とツール統合
```python
def _create_single_agent(self, agent_id: str, instruction: str) -> None:
    """単一エージェント作成"""
    # モデル選択（軽量モデル vs 標準モデル）
    model = (
        LIGHTWEIGHT_AGENT_CONFIG["model"] 
        if agent_id == "followup_question_generator" 
        else AGENT_CONFIG["model"]
    )
    
    # ツール設定（エージェント固有）
    tools = []
    if agent_id in TOOL_ENABLED_AGENTS:
        tool_names = TOOL_ENABLED_AGENTS[agent_id]
        tools = [self.tools[tool_name] for tool_name in tool_names if tool_name in self.tools]
```

##### ③ マルチエージェントパイプライン構築
```python
def _create_multi_agent_pipelines(self) -> None:
    """Sequential/Parallelパイプライン作成"""
    # Sequential Pipeline（順次実行）
    self._sequential_agent = SequentialAgent(
        name="Sequential18SpecialistPipeline",
        sub_agents=primary_agents[:3],
    )
    
    # Parallel Pipeline（並列実行）
    self._parallel_agent = ParallelAgent(
        name="Parallel18SpecialistPipeline",
        sub_agents=parallel_specialists[:5],
    )
```

**提供するインターフェース:**
- `get_agent(agent_type)` - 単一エージェント取得
- `get_all_agents()` - 全エージェント取得
- `get_runner(agent_type)` - Runner取得
- `get_agent_info()` - エージェント情報取得

### 2. MessageProcessor - メッセージ処理とコンテキスト管理

**ファイル:** `backend/src/agents/message_processor.py`

**責務:**
- 会話履歴と家族情報を含むコンテキスト管理
- メッセージ整形
- フォローアップ質問生成
- レスポンステキスト抽出

#### 主要機能

##### ① コンテキスト付きメッセージ作成
```python
def create_message_with_context(
    self,
    message: str,
    conversation_history: Optional[List[Dict]] = None,
    family_info: Optional[Dict] = None
) -> str:
    """会話履歴と家族情報を含めたメッセージを作成"""
    context_parts = []
    
    # 家族情報セクション
    if family_info:
        family_text = self._format_family_info(family_info)
        context_parts.append(family_text)
    
    # 会話履歴セクション
    if conversation_history:
        history_text = self._format_conversation_history(conversation_history)
        context_parts.append(history_text)
    
    # 現在のメッセージ
    current_message = f"【現在のメッセージ】\n親御さん: {message}\n"
    context_parts.append(current_message)
```

##### ② 家族情報の高精度フォーマット
```python
def _format_family_info(self, family_info: Dict) -> str:
    """家族情報のフォーマット"""
    # 子どもの年齢を正確に計算
    def _calculate_age(self, birth_date_str: str, today: date) -> str:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        
        years = today.year - birth_date.year
        months = today.month - birth_date.month
        days = today.day - birth_date.day
        
        # 誕生日がまだ来ていない場合の調整
        if months < 0 or (months == 0 and days < 0):
            years -= 1
            months += 12
        
        if years > 0:
            return f"{years}歳{months}ヶ月" if months > 0 else f"{years}歳"
        else:
            return f"{months}ヶ月" if months > 0 else f"{days}日"
```

##### ③ インテリジェントフォローアップ質問生成
```python
async def generate_followup_questions(
    self,
    original_message: str,
    specialist_response: str,
    followup_runner: Optional[Runner] = None,
    session_service = None
) -> str:
    """専門家回答に基づくフォローアップクエスチョン生成"""
    
    # LLMベース生成（優先）
    if followup_runner:
        followup_prompt = self._create_followup_prompt(original_message, specialist_response)
        # ... LLM実行 ...
    
    # ルールベースフォールバック
    else:
        return self._generate_dynamic_fallback_questions(original_message, specialist_response)
```

**提供するインターフェース:**
- `create_message_with_context()` - コンテキスト付きメッセージ作成
- `generate_followup_questions()` - フォローアップ質問生成
- `extract_response_text()` - レスポンステキスト抽出

### 3. RoutingExecutor - ルーティング実行とエージェント実行管理

**ファイル:** `backend/src/agents/routing_executor.py`

**責務:**
- ルーティング決定に基づくエージェント実行
- 専門家への自動ルーティング
- フォールバック処理
- レスポンス品質検証

#### 主要機能

##### ① 統合ルーティング実行
```python
async def execute_with_routing(
    self,
    message: str,
    user_id: str,
    session_id: str,
    runners: Dict[str, Runner],
    session_service,
    enhanced_message: str,
    conversation_history: Optional[List] = None,
    family_info: Optional[Dict] = None,
    agent_type: str = "auto"
) -> Tuple[str, Dict, List]:
    """ルーティングを含むエージェント実行"""
    
    # エージェント選択
    if agent_type == "auto":
        selected_agent_type = self._determine_agent_type(message)
    
    # ルーティング妥当性チェック
    if not self._validate_routing_decision(message, selected_agent_type):
        corrected_agent = self._auto_correct_routing(message, selected_agent_type)
        selected_agent_type = corrected_agent
    
    # エージェント実行
    response = await self._execute_agent(runner, user_id, session_id, content, selected_agent_type)
    
    return response, agent_info, routing_path
```

##### ② 専門家自動ルーティング
```python
async def _check_and_route_to_specialist(
    self,
    original_message: str,
    coordinator_response: str,
    user_id: str,
    session_id: str,
    runners: Dict[str, Runner],
    session_service,
    conversation_history: Optional[List] = None,
    family_info: Optional[Dict] = None
) -> Optional[Tuple[str, str]]:
    """コーディネーターのレスポンスから専門家紹介を検出し、自動ルーティング"""
    
    # 専門家への紹介キーワードを検出
    routing_keywords = [
        "専門家", "専門医", "栄養士", "睡眠専門", "発達専門",
        "健康管理", "行動専門", "遊び専門", "安全専門", "心理専門"
    ]
    
    keyword_match = any(keyword in coordinator_response.lower() for keyword in routing_keywords)
    
    if keyword_match:
        # 専門家ルーティング実行
        specialist_response = await self._perform_specialist_routing(
            original_message, user_id, session_id, runners, session_service, 
            conversation_history, family_info
        )
        return specialist_response, specialist_id
```

##### ③ 多段階フォールバック処理
```python
async def _route_to_specific_agent_with_fallback(
    self,
    agent_id: str,
    message: str,
    # ... その他パラメータ ...
    retry_count: int = 0,
    max_retries: int = 2,
) -> str:
    """フォールバック機能付き専門エージェント実行"""
    
    try:
        # 専門エージェント実行
        response = await self._execute_agent(runner, user_id, session_id, content, agent_id)
        
        # レスポンス品質検証
        if self._validate_agent_response(response, agent_id, message):
            return response
        else:
            # 品質不良時はリトライ
            if retry_count < max_retries:
                return await self._route_to_specific_agent_with_fallback(
                    agent_id, message, ..., retry_count + 1, max_retries
                )
    except Exception as e:
        # エラー時フォールバック
        return await self._execute_fallback_agent(message, user_id, session_id, runners, session_service)
```

**提供するインターフェース:**
- `execute_with_routing()` - 統合ルーティング実行
- レスポンス品質検証機能
- 多段階フォールバック機能

### 4. RoutingStrategy - ルーティング戦略

**ファイル:** `backend/src/agents/routing_strategy.py`

**責務:**
- エージェント選択戦略の定義
- キーワードベースルーティング
- 拡張可能な戦略パターン

#### 主要機能

##### ① 戦略パターンインターフェース
```python
class RoutingStrategy(ABC):
    """ルーティング戦略の抽象基底クラス"""
    
    @abstractmethod
    def determine_agent(
        self, 
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        family_info: Optional[Dict] = None
    ) -> Tuple[str, Dict]:
        """エージェントを決定する"""
        pass
```

##### ② キーワードベース戦略実装
```python
class KeywordRoutingStrategy(RoutingStrategy):
    """既存のキーワードベースルーティング戦略"""
    
    def determine_agent(self, message: str, ...) -> Tuple[str, Dict]:
        """キーワードマッチングによるエージェント決定"""
        message_lower = message.lower()
        
        # ステップ1: 強制ルーティングキーワードチェック
        force_routed_agent = self._check_force_routing(message_lower)
        if force_routed_agent:
            return force_routed_agent, {"confidence": 1.0, "reasoning": "緊急キーワード"}
        
        # ステップ2: 並列・順次分析キーワードチェック
        if self._is_parallel_analysis_requested(message_lower):
            return "parallel", {"confidence": 0.9, "reasoning": "並列分析キーワード"}
        
        # ステップ3: 専門エージェント決定論的ルーティング
        specialist_agent, routing_info = self._determine_specialist_agent(message_lower)
        if specialist_agent and specialist_agent != "coordinator":
            return specialist_agent, routing_info
        
        # ステップ4: デフォルト（コーディネーター）
        return "coordinator", {"confidence": 0.3, "reasoning": "デフォルト"}
```

**提供するインターフェース:**
- `determine_agent()` - エージェント決定
- `get_strategy_name()` - 戦略名取得
- 拡張可能な戦略パターン

### 5. Agent Manager V2 - 軽量統合インターフェース

**ファイル:** `backend/src/agents/agent_manager.py`

**責務:**
- 3つのコンポーネントの統合
- 既存APIとの互換性維持
- 単一インターフェースの提供

#### 主要機能

##### ① コンポーネント統合
```python
class AgentManager:
    """軽量化されたAgentManager - 統合インターフェース"""

    def __init__(self, tools: dict, logger: logging.Logger, settings, routing_strategy: Optional[RoutingStrategy] = None):
        # コンポーネント初期化
        self._registry = AgentRegistry(tools, logger)
        self._message_processor = MessageProcessor(logger)
        self._routing_executor = RoutingExecutor(logger, routing_strategy, self._message_processor)
        
        # 互換性のためのエイリアス
        self._agents = self._registry._agents
        self._runners = self._registry._runners
        self._session_service = self._registry._session_service
```

##### ② 統合ワークフロー
```python
async def route_query_async(self, message: str, user_id: str = "default_user", ...) -> str:
    """マルチエージェント対応クエリ実行（非同期）"""
    try:
        # 1. メッセージ整形（MessageProcessor）
        enhanced_message = self._message_processor.create_message_with_context(
            message, conversation_history, family_info
        )
        
        # 2. ルーティング実行（RoutingExecutor）
        response, agent_info, routing_path = await self._routing_executor.execute_with_routing(
            message=message,
            enhanced_message=enhanced_message,
            runners=self._registry.get_all_runners(),
            session_service=self._registry.get_session_service(),
            # ... その他パラメータ ...
        )
        
        # 3. フォローアップ質問生成（MessageProcessor）
        if agent_info.get("agent_id") not in ["sequential", "parallel"]:
            followup_questions = await self._message_processor.generate_followup_questions(
                original_message=message,
                specialist_response=response,
                followup_runner=self._registry.get_runner("followup_question_generator"),
                session_service=self._registry.get_session_service()
            )
            
            if followup_questions:
                return f"{response}\n\n{followup_questions}"
        
        return response
    except Exception as e:
        return f"システムエラーが発生しました: {str(e)}"
```

## 🔄 Enhanced Routing - 高度ルーティングシステム

### LLMベース意図理解
**ファイル:** `backend/src/agents/enhanced_routing.py`

```python
class EnhancedRoutingSystem:
    """LLMベース意図理解を統合したルーティングシステム"""
    
    async def analyze_intent(self, message: str, llm_client) -> Dict[str, any]:
        """LLMを使用してメッセージの意図を詳細分析"""
        return {
            "intent_type": str,         # 相談、質問、緊急対応、情報検索など
            "urgency_level": int,       # 1-5 (5が最高緊急度)
            "emotion_tone": str,        # 不安、心配、喜び、困惑など
            "key_entities": List[str],  # 年齢、症状、行動など抽出されたエンティティ
            "suggested_agents": List[str], # LLMが推奨するエージェント
            "confidence": float,        # 判定の確信度
            "reasoning": str           # 判定理由
        }
```

### ハイブリッドスコアリング
```python
def calculate_hybrid_score(
    self, 
    agent_id: str,
    keyword_score: float,
    llm_confidence: float,
    is_suggested_by_llm: bool,
    urgency_match: bool
) -> float:
    """ハイブリッドスコアの計算"""
    
    # 基本スコア = キーワードスコア
    score = keyword_score
    
    # LLMが推奨した場合のボーナス
    if is_suggested_by_llm:
        score += 20 * llm_confidence  # 最大+20点
    
    # 緊急度マッチボーナス
    if urgency_match:
        score += 10
    
    return score
```

## 📊 分割による改善効果

### 1. 保守性の向上
**Before:**
- 1つのファイル（1000行超）
- 全機能が密結合
- 一部の修正が全体に影響

**After:**
- 機能別に分離された4つのコンポーネント
- 明確な責務分離
- 個別機能の独立した修正・テスト

### 2. テスタビリティの向上
```python
# 個別コンポーネントのユニットテスト
def test_message_processor():
    processor = MessageProcessor(logger)
    result = processor.create_message_with_context("テストメッセージ", [], {})
    assert "テストメッセージ" in result

def test_routing_strategy():
    strategy = KeywordRoutingStrategy(logger, agent_keywords, force_routing, priority)
    agent_id, info = strategy.determine_agent("熱が38度です")
    assert agent_id == "health_specialist"
```

### 3. 拡張性の向上
```python
# 新しいルーティング戦略の追加
class MLRoutingStrategy(RoutingStrategy):
    def determine_agent(self, message: str, ...) -> Tuple[str, Dict]:
        # 機械学習ベースのエージェント選択
        return self.ml_model.predict(message)

# 新しいメッセージプロセッサーの追加
class AdvancedMessageProcessor(MessageProcessor):
    def create_message_with_context(self, ...) -> str:
        # より高度なコンテキスト処理
        return self.advanced_context_processing(...)
```

### 4. パフォーマンスの向上
- **エージェント初期化**: AgentRegistryで最適化
- **メッセージ処理**: MessageProcessorで専門化
- **ルーティング実行**: RoutingExecutorで高速化
- **戦略選択**: RoutingStrategyで効率化

## 🔧 設定とカスタマイズ

### コンポーネント設定
```python
# Composition Root（main.py）での組み立て
def create_agent_manager(tools, logger, settings):
    # ルーティング戦略の選択
    routing_strategy = KeywordRoutingStrategy(
        logger=logger,
        agent_keywords=AGENT_KEYWORDS,
        force_routing_keywords=FORCE_ROUTING_KEYWORDS,
        agent_priority=AGENT_PRIORITY
    )
    
    # Agent Manager V2の作成
    agent_manager = AgentManager(
        tools=tools,
        logger=logger,
        settings=settings,
        routing_strategy=routing_strategy
    )
    
    return agent_manager
```

### 動的戦略切り替え
```python
# 環境変数による戦略切り替え
routing_strategy_name = os.getenv("ROUTING_STRATEGY", "keyword")

if routing_strategy_name == "keyword":
    strategy = KeywordRoutingStrategy(...)
elif routing_strategy_name == "llm":
    strategy = LLMRoutingStrategy(...)
elif routing_strategy_name == "hybrid":
    strategy = HybridRoutingStrategy(...)
```

## 🎯 今後の発展

### 1. プラグイン化
- 各コンポーネントのプラグインインターフェース
- サードパーティルーティング戦略の追加
- カスタムメッセージプロセッサーの実装

### 2. マイクロサービス化
- 各コンポーネントの独立サービス化
- API経由でのコンポーネント間通信
- スケーラブルなアーキテクチャ

### 3. AI統合強化
- LLMベースルーティングの本格実装
- エージェント間協調の最適化
- 意図理解精度の向上

## 📋 まとめ

GenieUsのAgent Manager分割アーキテクチャは以下の特徴を持っています：

### **分割の核心価値**
1. **責務分離** - 各コンポーネントが明確な責務を持つ
2. **保守性向上** - 個別機能の独立した開発・修正
3. **テスト容易性** - コンポーネントレベルでのユニットテスト
4. **拡張性** - 新機能の追加が容易
5. **再利用性** - コンポーネントの他プロジェクトでの利用

### **4つの専門コンポーネント**
- **AgentRegistry** - エージェント初期化・管理の専門家
- **MessageProcessor** - メッセージ・コンテキスト処理の専門家  
- **RoutingExecutor** - ルーティング実行・フォールバックの専門家
- **RoutingStrategy** - ルーティング戦略の専門家

### **統合インターフェース**
- **Agent Manager V2** - 軽量な統合レイヤー
- 既存APIとの完全互換性
- プラグイン方式による機能拡張

この分割アーキテクチャにより、GenieUsはより保守しやすく、拡張しやすく、テストしやすいシステムになりました。