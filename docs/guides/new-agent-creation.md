# 新エージェント作成ガイド

GenieUsプロジェクトで新しいAIエージェントを作成する完全ガイド（Agent-Firstアーキテクチャ対応）

## 🎯 Agent中心設計の基本原則

GenieUsは**Agent-Firstアーキテクチャ**を採用。以下の原則に従って新エージェントを作成します：

```
✅ Agentが担当（推奨）
- 子育て判断・アドバイス生成
- 安全性評価・リスク判断
- 年齢発達評価
- 専門知識の提供

❌ Agent以外での実装禁止
- ChildcareAdviserProtocol
- SafetyAssessorProtocol
- 子育て相談UseCase
- ビジネス判断ロジック
```

## 📋 エージェント作成の基本フロー

新エージェントは以下の**4ステップ**で作成します：

```
1. マルチモーダルTool準備 → 2. Agent設計・実装
         ↓                      ↓
3. AgentManager統合 → 4. 動作確認・テスト
```

## 🔧 Step 1: マルチモーダルTool準備

### 1.1 必要なマルチモーダル機能の特定

新エージェントが使用する技術的機能を明確化：

```
例：栄養専門エージェント用Tool
✅ 実装すべき技術機能：
- 画像分析（食事写真の栄養成分分析）
- 音声分析（食事状況の音声記録）
- ファイル管理（栄養記録の保存）

❌ 実装禁止（Agent内で実装）：
- 栄養アドバイス生成
- 食事量評価判断
- 年齢別栄養指導
```

### 1.2 画像分析Tool実装

```python
# src/tools/image_analysis_tool.py
import logging
from typing import Dict, Any, Optional
from google.adk.tools import FunctionTool
from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase

def create_image_analysis_function(
    usecase: ImageAnalysisUseCase,
    logger: logging.Logger
) -> callable:
    """画像分析ツール関数を作成するファクトリー"""
    
    def image_analysis_function(
        image_path: str,
        analysis_prompt: str,
        user_id: str = "default_user",
        session_id: str = "default_session"
    ) -> Dict[str, Any]:
        """画像分析を実行するADK用ツール関数（技術機能のみ）"""
        try:
            logger.info(f"画像分析実行: path={image_path}, prompt_length={len(analysis_prompt)}")
            
            # 純粋な技術処理（ビジネス判断なし）
            analysis_result = usecase.analyze_image_with_prompt(
                image_path=image_path,
                prompt=analysis_prompt  # Agentから渡されるプロンプトをそのまま使用
            )
            
            return {
                "success": True,
                "analysis_result": analysis_result.raw_response,
                "metadata": {
                    "confidence": analysis_result.confidence,
                    "processing_time_ms": analysis_result.processing_time,
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"画像分析ツールエラー: {e}")
            return {
                "success": False,
                "analysis_result": "画像分析でエラーが発生しました",
                "metadata": {"error": str(e)}
            }
    
    return image_analysis_function

def create_image_analysis_tool(
    usecase: ImageAnalysisUseCase,
    logger: logging.Logger
) -> FunctionTool:
    """画像分析FunctionTool作成"""
    analysis_func = create_image_analysis_function(usecase, logger)
    return FunctionTool(func=analysis_func)
```

### 1.3 音声分析Tool実装

```python
# src/tools/voice_analysis_tool.py
import logging
from typing import Dict, Any
from google.adk.tools import FunctionTool
from src.application.usecases.voice_analysis_usecase import VoiceAnalysisUseCase

def create_voice_analysis_function(
    usecase: VoiceAnalysisUseCase,
    logger: logging.Logger
) -> callable:
    """音声分析ツール関数を作成するファクトリー"""
    
    def voice_analysis_function(
        voice_path: str,
        analysis_prompt: str,
        user_id: str = "default_user",
        session_id: str = "default_session"
    ) -> Dict[str, Any]:
        """音声分析を実行するADK用ツール関数（技術機能のみ）"""
        try:
            logger.info(f"音声分析実行: path={voice_path}, prompt_length={len(analysis_prompt)}")
            
            # 純粋な技術処理（ビジネス判断なし）
            analysis_result = usecase.analyze_voice_with_prompt(
                voice_path=voice_path,
                prompt=analysis_prompt  # Agentから渡されるプロンプトをそのまま使用
            )
            
            return {
                "success": True,
                "analysis_result": analysis_result.raw_response,
                "metadata": {
                    "duration_seconds": analysis_result.duration,
                    "confidence": analysis_result.confidence,
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"音声分析ツールエラー: {e}")
            return {
                "success": False,
                "analysis_result": "音声分析でエラーが発生しました",
                "metadata": {"error": str(e)}
            }
    
    return voice_analysis_function

def create_voice_analysis_tool(
    usecase: VoiceAnalysisUseCase,
    logger: logging.Logger
) -> FunctionTool:
    """音声分析FunctionTool作成"""
    analysis_func = create_voice_analysis_function(usecase, logger)
    return FunctionTool(func=analysis_func)
```

### 1.4 記録管理Tool実装

```python
# src/tools/record_management_tool.py
import logging
from typing import Dict, Any, List
from google.adk.tools import FunctionTool
from src.application.usecases.record_management_usecase import RecordManagementUseCase

def create_record_management_function(
    usecase: RecordManagementUseCase,
    logger: logging.Logger
) -> callable:
    """記録管理ツール関数を作成するファクトリー"""
    
    def record_management_function(
        operation: str,  # "save", "retrieve", "update", "delete"
        record_data: Dict[str, Any],
        user_id: str = "default_user",
        session_id: str = "default_session"
    ) -> Dict[str, Any]:
        """記録管理を実行するADK用ツール関数（技術機能のみ）"""
        try:
            logger.info(f"記録管理実行: operation={operation}, user={user_id}")
            
            # 純粋な技術処理（ビジネス判断なし）
            if operation == "save":
                result = usecase.save_record(record_data, user_id)
            elif operation == "retrieve":
                result = usecase.retrieve_records(record_data.get("criteria", {}), user_id)
            elif operation == "update":
                result = usecase.update_record(record_data.get("record_id"), record_data, user_id)
            elif operation == "delete":
                result = usecase.delete_record(record_data.get("record_id"), user_id)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            return {
                "success": True,
                "operation": operation,
                "result": result.to_dict(),
                "metadata": {
                    "records_affected": result.records_affected,
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"記録管理ツールエラー: {e}")
            return {
                "success": False,
                "operation": operation,
                "result": {},
                "metadata": {"error": str(e)}
            }
    
    return record_management_function

def create_record_management_tool(
    usecase: RecordManagementUseCase,
    logger: logging.Logger
) -> FunctionTool:
    """記録管理FunctionTool作成"""
    management_func = create_record_management_function(usecase, logger)
    return FunctionTool(func=management_func)
```

## 🤖 Step 2: Agent設計・実装

### 2.1 Agent専用プロンプト設計

```python
# src/agents/nutrition_agent.py
import logging
from typing import List
from google.adk import Agent
from google.adk.tools import FunctionTool

def create_nutrition_specialist_agent(
    image_analysis_tool: FunctionTool,
    voice_analysis_tool: FunctionTool,
    record_management_tool: FunctionTool,
    logger: logging.Logger
) -> Agent:
    """栄養専門エージェント作成"""
    logger.info("栄養専門エージェント作成開始")
    
    try:
        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="NutritionSpecialist",
            instruction=create_nutrition_instruction(),
            tools=[image_analysis_tool, voice_analysis_tool, record_management_tool],
        )
        
        logger.info("栄養専門エージェント作成完了")
        return agent
        
    except Exception as e:
        logger.error(f"栄養エージェント作成エラー: {e}")
        raise

def create_nutrition_instruction() -> str:
    """栄養専門エージェント用指示文（Agent中心設計）"""
    return """
    あなたは乳幼児の栄養に特化した専門エージェントです。
    
    ## 専門領域
    - 0-6歳の栄養指導・食事評価
    - 離乳食の進め方・アレルギー対応
    - 成長段階に応じた栄養バランス評価
    
    ## 利用可能なツール
    1. **image_analysis_tool**: 食事写真を分析して栄養成分を評価
    2. **voice_analysis_tool**: 食事状況の音声記録を分析
    3. **record_management_tool**: 栄養記録の保存・取得・更新
    
    ## ツール使用方針
    ### 画像分析時のプロンプト構築
    ```
    image_analysis_tool(
        image_path="user_provided_path",
        analysis_prompt="この食事写真を分析して、以下の情報を提供してください：
        1. 食材の種類と量の推定
        2. 栄養成分（カロリー、タンパク質、炭水化物、脂質、ビタミン、ミネラル）
        3. 年齢別適切な分量との比較
        4. 食材の調理方法と安全性
        5. アレルギーリスクの評価
        
        回答は具体的な数値と根拠を含めて詳細に記載してください。",
        user_id=user_id,
        session_id=session_id
    )
    ```
    
    ### 音声分析時のプロンプト構築
    ```
    voice_analysis_tool(
        voice_path="user_provided_path", 
        analysis_prompt="この音声記録を分析して、以下の情報を抽出してください：
        1. 食事中の子どもの様子（喜び、拒否、満足度）
        2. 食べるペースと咀嚼音の特徴
        3. 親との食事時のやり取り
        4. 食事への興味・関心度
        5. 気になる行動や反応
        
        子どもの月齢・年齢を考慮した評価を含めてください。",
        user_id=user_id,
        session_id=session_id
    )
    ```
    
    ### 記録管理の活用
    ```
    # 記録保存
    record_management_tool(
        operation="save",
        record_data={
            "type": "nutrition_analysis",
            "date": "2024-01-01",
            "meal_type": "breakfast",
            "analysis_result": "画像・音声分析結果",
            "recommendations": ["具体的な改善提案"],
            "follow_up_date": "2024-01-08"
        },
        user_id=user_id
    )
    
    # 過去の記録取得
    record_management_tool(
        operation="retrieve",
        record_data={
            "criteria": {
                "type": "nutrition_analysis",
                "date_range": "last_30_days"
            }
        },
        user_id=user_id
    )
    ```
    
    ## 応答方針
    1. **年齢適応**: 子どもの月齢・年齢を必ず考慮した指導
    2. **安全最優先**: アレルギーや誤嚥リスクを常に評価
    3. **実践的指導**: 具体的で実行可能なアドバイス
    4. **成長追跡**: 過去の記録と比較した成長評価
    5. **緊急時対応**: 危険な状況は医療機関への相談を推奨
    
    ## 判断・評価の実行
    あなたは画像・音声・記録データを総合的に分析し、以下を自動実行してください：
    - 栄養バランスの評価判断
    - 年齢適正性の安全性評価  
    - 改善提案の優先順位付け
    - フォローアップの必要性判断
    
    常に温かく、専門的で信頼できるアドバイスを提供してください。
    """
```

### 2.2 Agent中心のマルチモーダル処理

```python
# Agentが自動でマルチモーダル処理を統合する例

def create_comprehensive_nutrition_instruction() -> str:
    """包括的な栄養分析Agent指示文"""
    return """
    ## マルチモーダル統合評価手順
    
    ユーザーから食事に関する相談を受けた場合：
    
    1. **画像がある場合**
       - image_analysis_toolで食事内容を詳細分析
       - 栄養成分・分量・安全性を評価
       
    2. **音声がある場合**  
       - voice_analysis_toolで食事状況を分析
       - 子どもの反応・食べ方を評価
       
    3. **過去の記録確認**
       - record_management_toolで履歴を取得
       - 成長パターン・改善傾向を評価
       
    4. **統合判断の実行**
       - 全ての情報を総合して専門判断
       - 年齢・発達段階に応じたアドバイス生成
       - 安全性リスクの評価・警告
       
    5. **記録保存**
       - 分析結果と推奨事項を記録
       - フォローアップスケジュールを設定
       
    各ステップで具体的で実行可能なアドバイスを提供し、
    必要に応じて医療機関への相談を推奨してください。
    """
```

## 💉 Step 3: AgentManager統合

### 3.1 AgentManager更新

```python
# src/agents/agent_manager.py に追加
from src.agents.nutrition_agent import create_nutrition_specialist_agent

class AgentManager:
    """エージェント一元管理クラス"""
    
    def __init__(self, container: DIContainer):
        self.container = container
        self.logger = container.logger()
        self._agents: Dict[str, Agent] = {}
    
    def initialize_all_agents(self) -> None:
        """全エージェント初期化"""
        self.logger.info("全エージェント初期化開始")
        
        try:
            # 既存エージェント
            self._initialize_childcare_agent()
            
            # 新規追加
            self._initialize_nutrition_agent()
            
            # 将来予定
            # self._initialize_sleep_agent()
            # self._initialize_development_agent()
            
            self.logger.info(f"全エージェント初期化完了: {len(self._agents)}個のエージェント")
            
        except Exception as e:
            self.logger.error(f"エージェント初期化エラー: {e}")
            raise
    
    def _initialize_nutrition_agent(self) -> None:
        """栄養専門エージェント初期化"""
        try:
            # マルチモーダルツールを取得
            image_tool = self.container.image_analysis_tool()
            voice_tool = self.container.voice_analysis_tool()
            record_tool = self.container.record_management_tool()
            
            # エージェント作成（マルチモーダル対応）
            agent = create_nutrition_specialist_agent(
                image_analysis_tool=image_tool,
                voice_analysis_tool=voice_tool,
                record_management_tool=record_tool,
                logger=self.logger
            )
            
            self._agents["nutrition"] = agent
            self.logger.info("栄養専門エージェント初期化完了")
            
        except Exception as e:
            self.logger.error(f"栄養エージェント初期化エラー: {e}")
            raise
    
    def get_agent(self, agent_type: str) -> Agent:
        """指定されたタイプのエージェントを取得"""
        if agent_type not in self._agents:
            available = list(self._agents.keys())
            raise ValueError(f"エージェント '{agent_type}' が見つかりません. 利用可能: {available}")
        
        return self._agents[agent_type]
    
    def route_multimodal_query(
        self, 
        message: str, 
        image_path: str = None, 
        voice_path: str = None,
        user_context: Dict[str, Any] = None
    ) -> str:
        """マルチモーダル対応のクエリルーティング"""
        try:
            # 簡単なルーティングロジック（実際はより高度に）
            if "栄養" in message or "食事" in message or image_path or voice_path:
                agent = self.get_agent("nutrition")
            else:
                agent = self.get_agent("childcare")  # デフォルト
            
            # Agentがマルチモーダル処理を自動実行
            response = agent.run(message)
            return response
            
        except Exception as e:
            self.logger.error(f"マルチモーダルクエリルーティングエラー: {e}")
            return "申し訳ございません。処理中にエラーが発生しました。"
```

### 3.2 Composition Root統合

新エージェントの統合は**Composition Root**で行います。DIContainerは使用しません。

```python
# src/di_provider/composition_root.py に追加
class CompositionRoot:
    """アプリケーション全体の依存関係組み立て（main.py中央集約）"""
    
    def _build_tool_layer(self) -> None:
        """Tool層組み立て（ADK FunctionTool）"""
        
        # 既存ツール
        image_usecase = self._usecases.get_required("image_analysis")
        image_tool = self._create_image_analysis_tool(image_usecase)
        self._tools.register("image_analysis", image_tool)
        
        voice_usecase = self._usecases.get_required("voice_analysis")
        voice_tool = self._create_voice_analysis_tool(voice_usecase)
        self._tools.register("voice_analysis", voice_tool)
        
        # 新規追加: 栄養専門用ツール（必要に応じて）
        # nutrition_usecase = self._usecases.get_required("nutrition_analysis")
        # nutrition_tool = self._create_nutrition_analysis_tool(nutrition_usecase)
        # self._tools.register("nutrition_analysis", nutrition_tool)
        
        # 記録管理ツール
        record_usecase = self._usecases.get_required("record_management")
        record_tool = self._create_record_management_tool(record_usecase)
        self._tools.register("record_management", record_tool)
        
        self.logger.info("Tool層組み立て完了")
    
    # 新ツール作成メソッド追加例
    def _create_nutrition_analysis_tool(self, usecase: NutritionAnalysisUseCase) -> FunctionTool:
        """栄養分析ツール作成"""
        from src.tools.nutrition_analysis_tool import create_nutrition_analysis_tool
        return create_nutrition_analysis_tool(nutrition_analysis_usecase=usecase, logger=self.logger)
```

### 3.3 AgentManager統合（Composition Root統合版）

```python
# src/agents/agent_manager.py に追加
class AgentManager:
    """Agent中心のコンポーネント管理（CompositionRoot統合）"""
    
    def __init__(self, tools: dict[str, FunctionTool], logger: logging.Logger, settings: AppSettings):
        """CompositionRootから必要なコンポーネントのみ注入"""
        self.tools = tools
        self.logger = logger  
        self.settings = settings
        self._agents: dict[str, Agent] = {}
    
    def initialize_all_components(self) -> None:
        """全エージェント初期化（CompositionRoot統合）"""
        self.logger.info("AgentManager初期化開始（CompositionRoot統合）")
        
        try:
            # 既存エージェント
            self._initialize_childcare_agent()
            
            # 新規追加: 栄養専門エージェント
            self._initialize_nutrition_agent()
            
            # 将来予定
            # self._initialize_sleep_agent()
            # self._initialize_development_agent()
            
            self.logger.info(f"AgentManager初期化完了: {len(self._agents)}個のエージェント")
            
        except Exception as e:
            self.logger.error(f"AgentManager初期化エラー: {e}")
            raise
    
    def _initialize_nutrition_agent(self) -> None:
        """栄養専門エージェント初期化（CompositionRoot統合）"""
        try:
            # CompositionRootから注入されたツールを使用
            image_tool = self.tools.get("image_analysis")
            voice_tool = self.tools.get("voice_analysis")
            record_tool = self.tools.get("record_management")
            # nutrition_tool = self.tools.get("nutrition_analysis")  # 専用ツールがあれば
            
            # エージェント作成（マルチモーダル対応）
            agent = create_nutrition_specialist_agent(
                image_analysis_tool=image_tool,
                voice_analysis_tool=voice_tool,
                record_management_tool=record_tool,
                logger=self.logger
            )
            
            self._agents["nutrition"] = agent
            self.logger.info("栄養専門エージェント初期化完了（CompositionRoot統合）")
            
        except Exception as e:
            self.logger.error(f"栄養エージェント初期化エラー: {e}")
            raise
```

### 3.4 main.py統合（Composition Root中央集約）

```python
# src/main.py での統合（推奨パターン）
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pure CompositionRoot Pattern"""
    
    # 🎯 1. CompositionRoot一元初期化（アプリケーション全体で1度だけ）
    composition_root = CompositionRootFactory.create()
    logger = composition_root.logger
    logger.info("✅ CompositionRoot初期化完了")
    
    # 🎯 2. AgentManagerに必要なツールのみ注入
    all_tools = composition_root.get_all_tools()
    agent_manager = AgentManager(
        tools=all_tools, 
        logger=logger, 
        settings=composition_root.settings
    )
    agent_manager.initialize_all_components()  # 栄養エージェントも自動初期化
    logger.info("✅ AgentManager初期化完了（Pure Composition Root）")
    
    # 🎯 3. FastAPIアプリには必要なコンポーネントのみ注入
    app.agent_manager = agent_manager
    app.logger = logger
    app.composition_root = composition_root  # UseCase直接アクセス用
    logger.info("✅ FastAPIアプリ関連付け完了（Pure CompositionRoot）")
    
    yield

# アプリケーション作成
app = FastAPI(lifespan=lifespan)

# ルーター登録（依存関係は自動注入）
app.include_router(multiagent_chat_router, prefix="/api/v1", tags=["multiagent"])
app.include_router(family_router, prefix="/api/v1", tags=["family"])
```

## ✅ Step 4: 動作確認・テスト

### 4.1 統合テスト作成

```python
# tests/test_nutrition_agent_integration.py
import pytest
from src.di_provider.factory import get_container
from src.agents.agent_manager import AgentManager

class TestNutritionAgentIntegration:
    """栄養エージェント統合テスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.container = get_container()
        self.agent_manager = AgentManager(self.container)
        self.agent_manager.initialize_all_agents()
    
    def test_nutrition_agent_creation(self):
        """栄養エージェント作成テスト"""
        agent = self.agent_manager.get_agent("nutrition")
        
        assert agent.name == "NutritionSpecialist"
        assert len(agent.tools) == 3  # image, voice, record
    
    def test_multimodal_nutrition_consultation(self):
        """マルチモーダル栄養相談テスト"""
        response = self.agent_manager.route_multimodal_query(
            message="1歳の子どもの離乳食について相談したいです",
            image_path="/path/to/meal_photo.jpg",
            voice_path="/path/to/eating_sound.wav"
        )
        
        assert "栄養" in response
        assert "離乳食" in response
        assert len(response) > 100  # 詳細な回答
    
    def test_agent_tool_integration(self):
        """エージェント・ツール統合テスト"""
        # 個別ツールテスト
        image_tool = self.container.image_analysis_tool()
        voice_tool = self.container.voice_analysis_tool()
        record_tool = self.container.record_management_tool()
        
        # ツール動作確認
        assert image_tool is not None
        assert voice_tool is not None
        assert record_tool is not None
        
        # Agent経由でのツール使用確認
        agent = self.agent_manager.get_agent("nutrition")
        # 実際のAgent.run()テストは環境に依存するためモック使用推奨
```

### 4.2 APIエンドポイント統合テスト

```python
# tests/test_nutrition_api_integration.py
import pytest
from fastapi.testclient import TestClient
from src.main import create_app

class TestNutritionAPIIntegration:
    """栄養API統合テスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        app = create_app()
        self.client = TestClient(app)
    
    def test_multimodal_nutrition_endpoint(self):
        """マルチモーダル栄養エンドポイントテスト"""
        response = self.client.post(
            "/api/v1/multiagent/chat",
            json={
                "message": "離乳食の量が適切か相談したいです",
                "user_id": "test_user",
                "session_id": "test_session",
                "message_type": "image",
                "has_image": True,
                "image_path": "base64_encoded_image_data",
                "multimodal_context": {
                    "type": "image",
                    "image_description": "離乳食の写真"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "栄養" in data["response"]
        assert data["agent_info"]["specialist"] == "nutrition"
```

## 📋 チェックリスト

新エージェント作成完了前の確認事項：

### ✅ Agent中心設計チェック
- [ ] **マルチモーダルツール実装完了**（画像・音声・記録管理）
- [ ] **Agent指示文にツール使用方針記載**（プロンプト構築含む）
- [ ] **Agent内でビジネス判断実装**（Protocol/UseCase禁止）
- [ ] **AgentManager統合完了**（個別初期化禁止）

### ✅ 実装品質チェック
- [ ] **型アノテーション完備**
- [ ] **エラーハンドリング実装**
- [ ] **ロガーDI注入実装**（個別初期化禁止）
- [ ] **FastAPI Depends統合**（グローバル変数禁止）
- [ ] **import文がファイル先頭配置**

### ✅ 禁止事項回避チェック
- [ ] **ChildcareAdviserProtocol等を実装していない**
- [ ] **SafetyAssessorProtocol等を実装していない**
- [ ] **consultation_usecase等を実装していない**
- [ ] **ビジネス概念をInfrastructure層で扱っていない**
- [ ] **DIContainer・setup_routes関数を使用していない**
- [ ] **Composition Rootパターンを使用している**

### ✅ 動作確認チェック
- [ ] **統合テスト通過**
- [ ] **マルチモーダル対応確認**
- [ ] **エージェントルーティング動作確認**
- [ ] **エラーケース動作確認**

## 🔗 関連ドキュメント

- [コーディング規約](../development/coding-standards.md) - 必須の実装規約
- [アーキテクチャ概要](../architecture/overview.md) - Agent中心設計理解
- [Composition Root設計](../architecture/composition-root-design.md) - 中央集約型依存関係組み立て
- [新ツール開発ガイド](./new-tool-development.md) - マルチモーダルツール開発
- [ADKベストプラクティス](../technical/adk-best-practices.md) - ADK制約・パターン

---

**💡 重要**: Agent-Firstアーキテクチャでは、Agentが中心となってマルチモーダル処理・ビジネス判断・専門知識提供を統合的に実行します。Tool/UseCase/Infrastructureは純粋な技術機能（画像・音声・ファイル・記録）のみに特化し、依存関係の組み立てはComposition Rootパターンで中央集約してください。