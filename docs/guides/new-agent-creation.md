# 新エージェント作成ガイド

GenieUsプロジェクトで新しいAIエージェントを作成する完全ガイド

## 🎯 エージェント作成の基本フロー

新エージェントは以下の**6ステップ**で作成します：

```
1. ドメイン設計 → 2. ツール作成 → 3. エージェント実装 
     ↓                ↓                ↓
4. DI統合 → 5. API統合 → 6. テスト・検証
```

## 📋 Step 1: ドメイン設計

### 1.1 ドメイン定義
新しいエージェントの専門領域を明確化：

```
例：睡眠専門エージェント
- 対象年齢：0-6歳
- 専門領域：睡眠パターン、夜泣き、昼寝
- 連携エージェント：栄養、発達、安全性評価
```

### 1.2 ディレクトリ作成
```bash
mkdir -p src/agents/{domain}
mkdir -p src/tools/{domain}_tools
```

## 🔧 Step 2: カスタムツール作成

### 2.1 Protocol定義
まず、ドメイン固有のサービスプロトコルを定義：

```python
# src/application/interface/protocols/sleep_service.py
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SleepAnalysisResult:
    """睡眠分析結果のデータクラス"""
    sleep_pattern: str
    recommendations: list[str]
    urgency_level: str
    confidence: float
    metadata: Dict[str, Any]

class SleepAnalyzerProtocol(Protocol):
    """睡眠分析サービスのプロトコル"""
    
    def analyze_sleep_pattern(
        self, 
        query: str, 
        child_age_months: int,
        context: Optional[Dict[str, Any]] = None
    ) -> SleepAnalysisResult:
        """睡眠パターンを分析する"""
        ...
```

### 2.2 Infrastructure層実装

```python
# src/infrastructure/adapters/sleep_analyzer.py
import logging
from typing import Dict, Any, Optional
from src.application.interface.protocols.sleep_service import (
    SleepAnalyzerProtocol, 
    SleepAnalysisResult
)

class ExpertBasedSleepAnalyzer(SleepAnalyzerProtocol):
    """専門家ルールベースの睡眠分析アダプター"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def analyze_sleep_pattern(
        self, 
        query: str, 
        child_age_months: int,
        context: Optional[Dict[str, Any]] = None
    ) -> SleepAnalysisResult:
        """睡眠パターンの具体的な分析実装"""
        try:
            self.logger.info(f"睡眠分析開始: 月齢{child_age_months}, query長{len(query)}")
            
            # ドメイン固有のロジック実装
            pattern = self._classify_sleep_pattern(query, child_age_months)
            recommendations = self._generate_recommendations(pattern, child_age_months)
            urgency = self._assess_urgency(query, pattern)
            
            result = SleepAnalysisResult(
                sleep_pattern=pattern,
                recommendations=recommendations,
                urgency_level=urgency,
                confidence=0.85,
                metadata={
                    "child_age_months": child_age_months,
                    "analysis_timestamp": "now",
                    "pattern_confidence": 0.85
                }
            )
            
            self.logger.info(f"睡眠分析完了: pattern={pattern}, urgency={urgency}")
            return result
            
        except Exception as e:
            self.logger.error(f"睡眠分析エラー: {e}")
            return SleepAnalysisResult(
                sleep_pattern="分析不可",
                recommendations=["専門医への相談をお勧めします"],
                urgency_level="中",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _classify_sleep_pattern(self, query: str, age: int) -> str:
        """睡眠パターンの分類ロジック"""
        # 実装詳細
        pass
    
    def _generate_recommendations(self, pattern: str, age: int) -> list[str]:
        """推奨事項の生成ロジック"""
        # 実装詳細  
        pass
    
    def _assess_urgency(self, query: str, pattern: str) -> str:
        """緊急度評価ロジック"""
        # 実装詳細
        pass
```

### 2.3 UseCase層実装

```python
# src/application/usecases/sleep_consultation_usecase.py
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from src.application.interface.protocols.sleep_service import SleepAnalyzerProtocol

@dataclass
class SleepConsultationRequest:
    """睡眠相談リクエスト"""
    message: str
    user_id: str
    session_id: str
    child_age_months: int
    context: Optional[Dict[str, Any]] = None

@dataclass  
class SleepConsultationResponse:
    """睡眠相談レスポンス"""
    advice: str
    pattern_analysis: str
    recommendations: list[str]
    urgency_level: str
    session_id: str
    timestamp: datetime
    success: bool

class SleepConsultationUseCase:
    """睡眠相談ビジネスロジック"""
    
    def __init__(
        self,
        sleep_analyzer: SleepAnalyzerProtocol,
        logger: logging.Logger
    ):
        self.sleep_analyzer = sleep_analyzer
        self.logger = logger
    
    def consult(self, request: SleepConsultationRequest) -> SleepConsultationResponse:
        """睡眠相談のビジネスロジック実行"""
        try:
            self.logger.info(f"睡眠相談開始: user={request.user_id}")
            
            # 睡眠分析実行
            analysis = self.sleep_analyzer.analyze_sleep_pattern(
                request.message,
                request.child_age_months,
                request.context
            )
            
            # アドバイス生成
            advice = self._generate_advice(analysis, request.child_age_months)
            
            return SleepConsultationResponse(
                advice=advice,
                pattern_analysis=analysis.sleep_pattern,
                recommendations=analysis.recommendations,
                urgency_level=analysis.urgency_level,
                session_id=request.session_id,
                timestamp=datetime.now(),
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"睡眠相談実行エラー: {e}")
            return SleepConsultationResponse(
                advice="申し訳ございません。睡眠に関する分析でエラーが発生しました。",
                pattern_analysis="分析不可",
                recommendations=[],
                urgency_level="低",
                session_id=request.session_id,
                timestamp=datetime.now(),
                success=False
            )
    
    def _generate_advice(self, analysis, age_months: int) -> str:
        """年齢に応じたアドバイス生成"""
        # 実装詳細
        pass
```

### 2.4 Tool層実装

```python
# src/tools/sleep_consultation_tool.py
import logging
from typing import Any, Dict, Optional
from google.adk.tools import FunctionTool

from src.application.usecases.sleep_consultation_usecase import (
    SleepConsultationRequest,
    SleepConsultationResponse,
    SleepConsultationUseCase
)

def create_sleep_consultation_function(
    usecase: SleepConsultationUseCase,
    logger: logging.Logger  # 🚨 必須: ロガーDI注入
) -> callable:
    """睡眠相談ツール関数を作成するファクトリー"""
    
    def sleep_consultation_function(
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session", 
        child_age_months: int = 12,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """睡眠相談を実行するADK用ツール関数"""
        try:
            # リクエスト構築
            request = SleepConsultationRequest(
                message=message,
                user_id=user_id,
                session_id=session_id,
                child_age_months=child_age_months,
                context=additional_context or {}
            )
            
            # ビジネスロジック実行
            response: SleepConsultationResponse = usecase.consult(request)
            
            # Agent向けレスポンス変換
            if response.success:
                agent_response = f\"\"\"
                【{child_age_months}ヶ月のお子さまの睡眠アドバイス】
                
                {response.advice}
                
                睡眠パターン分析: {response.pattern_analysis}
                緊急度: {response.urgency_level}
                
                推奨事項:
                {chr(10).join(f"• {rec}" for rec in response.recommendations)}
                \"\"\".strip()
                
                return {
                    "success": True,
                    "response": agent_response,
                    "metadata": {
                        "pattern": response.pattern_analysis,
                        "urgency": response.urgency_level,
                        "session_id": response.session_id,
                        "timestamp": response.timestamp.isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "response": response.advice,
                    "metadata": {"error": "sleep_analysis_failed"}
                }
                
        except Exception as e:
            logger.error(f"睡眠相談ツールエラー: {e}")  # ✅ 注入されたロガー使用
            return {
                "success": False,
                "response": "睡眠に関するご相談で問題が発生しました。お子さまの安全に関わる場合は医療機関にご相談ください。",
                "metadata": {"error": str(e)}
            }
    
    return sleep_consultation_function

def create_sleep_consultation_tool(
    usecase: SleepConsultationUseCase,
    logger: logging.Logger  # 🚨 必須: ロガーDI注入
) -> FunctionTool:
    """睡眠相談FunctionTool作成（ロガーDI統合版）"""
    consultation_func = create_sleep_consultation_function(usecase, logger)
    return FunctionTool(func=consultation_func)
```

## 🤖 Step 3: エージェント実装

```python
# src/agents/sleep_agent.py
import logging
from google.adk import Agent
from google.adk.tools import FunctionTool

def create_sleep_specialist_agent(
    sleep_tool: FunctionTool, 
    logger: logging.Logger  # 🚨 必須: ログDI注入
) -> Agent:
    """睡眠専門エージェント作成（ロガーDI統合版）"""
    logger.info("睡眠専門エージェント作成開始")
    
    try:
        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="SleepSpecialist",
            instruction=create_sleep_instruction(),
            tools=[sleep_tool],
        )
        
        logger.info("睡眠専門エージェント作成完了")
        return agent
        
    except Exception as e:
        logger.error(f"睡眠エージェント作成エラー: {e}")
        raise

def create_sleep_instruction() -> str:
    """睡眠専門エージェント用指示文"""
    return \"\"\"
    あなたは子どもの睡眠に特化した専門家です。
    
    専門領域:
    - 新生児〜6歳の睡眠パターン
    - 夜泣き、昼寝、睡眠リズムの調整
    - 年齢別睡眠の悩み解決
    
    対応方針:
    1. 子どもの月齢・年齢を考慮したアドバイス
    2. 安全性を最優先とした提案
    3. 親の負担軽減も配慮
    4. 緊急性がある場合は医療機関への相談を推奨
    
    常に優しく、実践的なアドバイスを提供してください。
    \"\"\"
```

## 💉 Step 4: DI統合

### 4.1 DIコンテナ更新

```python
# src/di_provider/container.py に追加
from src.infrastructure.adapters.sleep_analyzer import ExpertBasedSleepAnalyzer
from src.application.usecases.sleep_consultation_usecase import SleepConsultationUseCase
from src.tools.sleep_consultation_tool import create_sleep_consultation_tool

class DIContainer(containers.DeclarativeContainer):
    # 既存のprovider...
    
    # ========== INFRASTRUCTURE LAYER - Sleep Domain ==========
    sleep_analyzer: providers.Provider[SleepAnalyzerProtocol] = providers.Singleton(
        ExpertBasedSleepAnalyzer,
        logger=logger,
    )
    
    # ========== APPLICATION LAYER - Sleep Domain ==========
    sleep_consultation_usecase: providers.Provider[SleepConsultationUseCase] = providers.Factory(
        SleepConsultationUseCase,
        sleep_analyzer=sleep_analyzer,
        logger=logger,
    )
    
    # ========== TOOLS LAYER - Sleep Domain ==========
    sleep_consultation_tool = providers.Factory(
        create_sleep_consultation_tool,
        usecase=sleep_consultation_usecase,
        logger=logger,  # 🚨 必須: ロガーDI注入
    )
```

### 4.2 エージェント統合

```python
# ❌ 非推奨: 個別エージェント初期化は AgentManager に移行
# ✅ 推奨: src/agents/agent_manager.py で一元管理

class AgentManager:
    def _initialize_sleep_agent(self) -> None:
        \"\"\"睡眠エージェント初期化（AgentManagerパターン）\"\"\"
        try:
            sleep_tool = self.container.sleep_consultation_tool()
            agent = create_sleep_specialist_agent(sleep_tool, self.logger)
            self._agents["sleep"] = agent
            self.logger.info("睡眠エージェント初期化完了")
        except Exception as e:
            self.logger.error(f"睡眠エージェント初期化エラー: {e}")
            raise
    
    def initialize_all_agents(self) -> None:
        \"\"\"全エージェントを初期化\"\"\"
        self.logger.info("全エージェント初期化開始")
        
        try:
            # 各エージェントを順次初期化
            self._initialize_childcare_agent()
            self._initialize_sleep_agent()  # 睡眠エージェント追加
            # 将来: self._initialize_nutrition_agent()
            
            self.logger.info(f"全エージェント初期化完了: {len(self._agents)}個")
        except Exception as e:
            self.logger.error(f"エージェント初期化エラー: {e}")
            raise
```

## 🌐 Step 5: API統合

### 5.1 APIエンドポイント追加

```python
# src/presentation/api/routes/sleep.py
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from dependency_injector.wiring import inject, Provide

from src.di_provider.container import DIContainer

router = APIRouter()

class SleepConsultationMessage(BaseModel):
    message: str = Field(..., description="睡眠に関する相談内容")
    user_id: str = Field(default="anonymous", description="ユーザーID")
    session_id: str = Field(default="default", description="セッションID")
    child_age_months: int = Field(default=12, description="子どもの月齢")

class SleepConsultationResponse(BaseModel):
    response: str = Field(..., description="睡眠専門家からの応答")
    status: str = Field(default="success", description="処理状況")
    session_id: str = Field(..., description="セッションID")
    agent_info: dict = Field(default_factory=dict, description="エージェント情報")

@router.post("/sleep/consultation", response_model=SleepConsultationResponse)
@inject  # 🚨 必須: DI注入有効化
async def sleep_consultation_endpoint(
    consultation: SleepConsultationMessage,
    # ✅ FastAPI Depends + DI統合パターン
    tool = Depends(Provide[DIContainer.sleep_consultation_tool]),
    logger = Depends(Provide[DIContainer.logger]),
):
    \"\"\"睡眠専門相談エンドポイント（DI完全統合版）\"\"\"
    try:
        logger.info(f"睡眠相談リクエスト受信: user={consultation.user_id}")
        
        # 注入されたツールを使用（グローバル変数不要）
        tool_result = tool.func(
            message=consultation.message,
            user_id=consultation.user_id,
            session_id=consultation.session_id,
            child_age_months=consultation.child_age_months
        )
        
        if tool_result.get("success", False):
            response_text = tool_result["response"]
            agent_info = {
                "specialist": "sleep",
                "metadata": tool_result.get("metadata", {})
            }
        else:
            response_text = tool_result.get("response", "睡眠相談でエラーが発生しました。")
            agent_info = {"error": tool_result.get("metadata", {})}
        
        return SleepConsultationResponse(
            response=response_text,
            session_id=consultation.session_id,
            agent_info=agent_info
        )
        
    except Exception as e:
        logger.error(f"睡眠相談エンドポイントエラー: {e}")
        return SleepConsultationResponse(
            response="睡眠相談でシステムエラーが発生しました。",
            status="error",
            session_id=consultation.session_id,
            agent_info={"error": str(e)}
        )

# ❌ 非推奨: setup_routes関数は使用禁止
# ✅ 推奨: main.pyでcontainer.wire()により自動統合

# main.py での統合例:
# container.wire(modules=["src.presentation.api.routes.sleep"])
# app.include_router(sleep_router, prefix="/api/v1", tags=["sleep"])
```

### 5.2 main.py統合（推奨パターン）

```python
# src/main.py での統合（推奨パターン）
def create_app() -> FastAPI:
    \"\"\"FastAPIアプリケーションファクトリー\"\"\"
    container = DIContainer()
    
    # ⭐ AgentManager による一元管理
    agent_manager = AgentManager(container)
    agent_manager.initialize_all_agents()  # 睡眠エージェントも自動初期化
    
    app = FastAPI()
    app.container = container
    app.agent_manager = agent_manager
    
    # ⭐ FastAPI Depends統合（グローバル変数・setup_routes不要）
    container.wire(modules=[
        "src.presentation.api.routes.chat",
        "src.presentation.api.routes.sleep",  # 睡眠ルート追加
    ])
    
    # ルーター登録（依存関係は自動注入）
    app.include_router(sleep_router, prefix="/api/v1", tags=["sleep"])
    
    return app
```

## ✅ Step 6: テスト・検証

### 6.1 統合テスト作成

```python
# test_sleep_agent_integration.py
import pytest
from src.di_provider.factory import get_container
from src.agents.di_based_childcare_agent import get_childcare_agent

def test_sleep_agent_integration():
    \"\"\"睡眠エージェント統合テスト\"\"\"
    # DIコンテナ初期化
    container = get_container()
    
    # ツール・エージェント作成
    sleep_tool = container.sleep_consultation_tool()
    sleep_agent = get_childcare_agent("sleep", None, sleep_tool=sleep_tool)
    
    # 基本動作確認
    assert sleep_agent.name == "SleepSpecialist"
    assert len(sleep_agent.tools) == 1
    
    # ツール実行テスト
    result = sleep_tool.func(
        message="3ヶ月の赤ちゃんが夜泣きします",
        child_age_months=3
    )
    
    assert result["success"] is True
    assert "睡眠" in result["response"]
    assert "metadata" in result
```

### 6.2 API動作確認

```bash
# エンドポイントテスト
curl -X POST "http://localhost:8000/api/v1/sleep/consultation" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "1歳の子どもが夜中に何度も起きます",
    "child_age_months": 12,
    "user_id": "test_user"
  }'
```

## 📋 チェックリスト

新エージェント作成完了前の確認事項：

### ✅ 実装チェック
- [ ] Protocol定義完了
- [ ] Infrastructure層実装完了
- [ ] UseCase層実装完了  
- [ ] Tool層実装完了
- [ ] Agent実装完了
- [ ] DI統合完了
- [ ] API統合完了

### ✅ 品質チェック
- [ ] 型アノテーション完備
- [ ] エラーハンドリング実装
- [ ] **ロガーDI注入実装**（個別初期化禁止）
- [ ] **AgentManager統合**（個別エージェント初期化禁止）
- [ ] **FastAPI Depends統合**（グローバル変数・setup_routes禁止）
- [ ] テストケース作成
- [ ] import文がファイル先頭配置

### ✅ 動作確認
- [ ] 統合テスト通過
- [ ] APIエンドポイント動作確認
- [ ] エラーケース動作確認
- [ ] パフォーマンス確認

## 🔗 関連ドキュメント

- [新ツール開発ガイド](./new-tool-development.md) - ツール開発詳細
- [コーディング規約](../development/coding-standards.md) - 必須の実装規約
- [ADKベストプラクティス](../technical/adk-best-practices.md) - ADK制約・パターン
- [アーキテクチャ概要](../architecture/overview.md) - 全体設計理解

---

**💡 重要**: 新エージェント作成は段階的に進めることを推奨。まずはシンプルな実装から始めて、動作確認後に機能拡張することで、安定性を確保できます。