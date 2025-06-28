# 新ツール開発ガイド

GenieUs Agent-Firstアーキテクチャでの新ツール開発完全ガイド

## 🎯 Agent-Firstアーキテクチャでのツール設計思想

### **重要原則**: Agentが中心、Toolは薄いアダプター

```
Agent（Gemini判断・アドバイス生成） ← 中心
    ↓
Tool（マルチモーダル技術の薄いアダプター） ← 補助
    ↓  
UseCase（純粋技術機能のみ） ← 補助
    ↓
Infrastructure（API呼び出しのみ） ← 補助
```

### **許可される機能範囲**
✅ **実装OK**: 純粋技術機能
- 画像分析技術 (`image_analysis_tool`)
- 音声分析技術 (`voice_analysis_tool`)
- ファイル操作技術 (`file_management_tool`)
- 記録管理技術 (`record_management_tool`)

❌ **実装禁止**: ビジネスロジック・判断・アドバイス生成
- 子育て相談ツール（Agent内で実装）
- 安全性評価ツール（Agent内で実装）
- 発達アドバイスツール（Agent内で実装）

## 🚀 新ツール開発手順

### Step 1: ツール仕様定義

#### 1.1 技術機能の特定
```python
# 例: 新しい画像認識ツール
"""
技術機能: 画像内のオブジェクト検出
入力: 画像パス + 検出プロンプト  
出力: 検出結果JSON
ビジネス概念: 含まない（child_id, advice等は禁止）
"""
```

#### 1.2 Protocol定義
```python
# backend/src/application/interface/protocols/new_analyzer.py
from typing import Protocol
from abc import abstractmethod

class NewAnalyzerProtocol(Protocol):
    """新分析技術のProtocol（ビジネス概念なし）"""
    
    @abstractmethod
    async def analyze_with_prompt(
        self, 
        data_path: str, 
        prompt: str
    ) -> dict:
        """汎用分析実行（プロンプトそのまま使用）"""
        pass
```

### Step 2: Infrastructure層実装

```python
# backend/src/infrastructure/adapters/new_analyzer.py
import logging
from typing import Dict, Any

from src.application.interface.protocols.new_analyzer import NewAnalyzerProtocol

class GeminiNewAnalyzer(NewAnalyzerProtocol):
    """新分析技術のInfrastructure実装（純粋技術のみ）"""
    
    def __init__(self, logger: logging.Logger):
        """コンストラクタ（DI注入）"""
        self.logger = logger
        # Gemini API初期化
        
    async def analyze_with_prompt(
        self, 
        data_path: str, 
        prompt: str
    ) -> Dict[str, Any]:
        """汎用分析実行（ビジネス概念なし）"""
        try:
            self.logger.info(f"新分析実行開始: {data_path}")
            
            # プロンプトをそのまま使用してAPI呼び出し
            response = await self._call_gemini_api(data_path, prompt)
            
            # 純粋な技術結果を返す
            return {
                "success": True,
                "raw_response": response.text,
                "metadata": {
                    "model": "gemini-2.5-flash",
                    "timestamp": "2024-12-XX"
                }
            }
            
        except Exception as e:
            self.logger.error(f"新分析エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": None
            }
    
    async def _call_gemini_api(self, data_path: str, prompt: str) -> Any:
        """内部：Gemini API呼び出し"""
        # 実装
        pass
```

### Step 3: UseCase層実装

```python
# backend/src/application/usecases/new_analysis_usecase.py
import logging
from typing import Dict, Any
from dataclasses import dataclass

from src.application.interface.protocols.new_analyzer import NewAnalyzerProtocol

@dataclass
class NewAnalysisRequest:
    """新分析リクエスト（技術パラメータのみ）"""
    data_path: str
    analysis_type: str  # "object_detection", "text_extraction"等
    custom_prompt: str | None = None

@dataclass  
class NewAnalysisResponse:
    """新分析レスポンス（技術結果のみ）"""
    success: bool
    analysis_result: Dict[str, Any]
    metadata: Dict[str, Any]
    error: str | None = None

class NewAnalysisUseCase:
    """新分析UseCase（技術調整のみ、ビジネスロジックなし）"""
    
    def __init__(
        self,
        new_analyzer: NewAnalyzerProtocol,
        logger: logging.Logger
    ):
        self.new_analyzer = new_analyzer
        self.logger = logger
    
    async def execute(self, request: NewAnalysisRequest) -> NewAnalysisResponse:
        """新分析実行（技術的プロンプト構築のみ）"""
        try:
            self.logger.info(f"新分析UseCase実行: {request.analysis_type}")
            
            # 技術的プロンプト構築（ビジネス概念なし）
            prompt = self._build_technical_prompt(
                request.analysis_type, 
                request.custom_prompt
            )
            
            # Infrastructure層呼び出し
            result = await self.new_analyzer.analyze_with_prompt(
                request.data_path, 
                prompt
            )
            
            return NewAnalysisResponse(
                success=result["success"],
                analysis_result=result.get("raw_response", {}),
                metadata=result.get("metadata", {}),
                error=result.get("error")
            )
            
        except Exception as e:
            self.logger.error(f"新分析UseCase実行エラー: {e}")
            return NewAnalysisResponse(
                success=False,
                analysis_result={},
                metadata={},
                error=str(e)
            )
    
    def _build_technical_prompt(
        self, 
        analysis_type: str, 
        custom_prompt: str | None
    ) -> str:
        """技術的プロンプト構築（ビジネス概念なし）"""
        
        base_prompts = {
            "object_detection": "この画像に含まれるオブジェクトを検出してください。",
            "text_extraction": "この画像から文字を抽出してください。",
            "color_analysis": "この画像の色彩を分析してください。"
        }
        
        prompt = base_prompts.get(analysis_type, "この画像を分析してください。")
        
        if custom_prompt:
            prompt = f"{prompt}\n\n追加指示: {custom_prompt}"
            
        return prompt
```

### Step 4: Tool層実装

```python
# backend/src/tools/new_analysis_tool.py
import logging
from typing import Dict, Any

from google.adk.tools import FunctionTool
from src.application.usecases.new_analysis_usecase import (
    NewAnalysisUseCase, 
    NewAnalysisRequest
)

def create_new_analysis_tool(
    usecase: NewAnalysisUseCase,
    logger: logging.Logger
) -> FunctionTool:
    """新分析ツール作成（薄いアダプター）"""
    
    def new_analysis_function(
        data_path: str,
        analysis_type: str = "object_detection",
        custom_prompt: str | None = None
    ) -> Dict[str, Any]:
        """ADK用新分析ツール関数（薄いアダプター）"""
        
        try:
            logger.info(f"新分析ツール実行: {analysis_type}")
            
            # UseCaseリクエスト作成
            request = NewAnalysisRequest(
                data_path=data_path,
                analysis_type=analysis_type,
                custom_prompt=custom_prompt
            )
            
            # UseCase実行
            response = await usecase.execute(request)
            
            # ADK形式でレスポンス返却
            return {
                "success": response.success,
                "analysis_result": response.analysis_result,
                "metadata": response.metadata,
                "error": response.error
            }
            
        except Exception as e:
            logger.error(f"新分析ツールエラー: {e}")
            return {
                "success": False,
                "analysis_result": {},
                "error": str(e)
            }
    
    return FunctionTool(
        func=new_analysis_function,
        name="new_analysis_tool",
        description="新しい分析技術を実行するツール"
    )
```

### Step 5: Composition Root統合

```python
# backend/src/di_provider/composition_root.py

class CompositionRoot:
    def _build_infrastructure_layer(self):
        """Infrastructure Layer構築"""
        # 既存の分析器
        image_analyzer = GeminiImageAnalyzer(logger=self.logger)
        voice_analyzer = GeminiVoiceAnalyzer(logger=self.logger)
        
        # 新しい分析器追加
        new_analyzer = GeminiNewAnalyzer(logger=self.logger)
        
        self._infrastructure.register("image_analyzer", image_analyzer)
        self._infrastructure.register("voice_analyzer", voice_analyzer)
        self._infrastructure.register("new_analyzer", new_analyzer)
    
    def _build_application_layer(self):
        """Application Layer構築"""
        # 既存のUseCase
        image_analysis_usecase = ImageAnalysisUseCase(
            image_analyzer=self._infrastructure.get("image_analyzer"),
            logger=self.logger
        )
        
        # 新しいUseCase追加
        new_analysis_usecase = NewAnalysisUseCase(
            new_analyzer=self._infrastructure.get("new_analyzer"),
            logger=self.logger
        )
        
        self._usecases.register("image_analysis", image_analysis_usecase)
        self._usecases.register("new_analysis", new_analysis_usecase)
    
    def _build_tool_layer(self):
        """Tool Layer構築"""
        # 既存のツール
        image_analysis_tool = create_image_analysis_tool(
            usecase=self._usecases.get("image_analysis"),
            logger=self.logger
        )
        
        # 新しいツール追加
        new_analysis_tool = create_new_analysis_tool(
            usecase=self._usecases.get("new_analysis"),
            logger=self.logger
        )
        
        self._tools.register("image_analysis", image_analysis_tool)
        self._tools.register("new_analysis", new_analysis_tool)
```

### Step 6: Agent統合

```python
# backend/src/agents/adk_routing_coordinator.py

class AdkRoutingCoordinator:
    def create_specialist_agent_with_new_tool(self) -> LlmAgent:
        """新ツール対応の専門エージェント作成"""
        
        instruction = """あなたは画像・データ分析の専門エージェントです。

## 利用可能なツール
1. **image_analysis_tool**: 基本的な画像分析
2. **new_analysis_tool**: 新しい高度な分析技術
   - object_detection: オブジェクト検出
   - text_extraction: 文字認識
   - color_analysis: 色彩分析

## 使用例
ユーザーが「この写真の中の文字を読んでください」と言った場合：
- new_analysis_tool(data_path="画像パス", analysis_type="text_extraction")

{FAMILY_RECOGNITION_INSTRUCTION}

適切なツールを選んで技術的な分析を実行し、結果を分かりやすく説明してください。
"""

        tools = [
            self.tools.get("image_analysis_tool"),
            self.tools.get("new_analysis_tool"),  # 新ツール追加
        ]

        return LlmAgent(
            name="DataAnalysisSpecialist",
            model="gemini-2.5-flash",
            instruction=instruction,
            tools=[tool for tool in tools if tool is not None]
        )
```

## 🧪 テスト実装

### Unit Test例

```python
# tests/test_new_analysis_usecase.py
import pytest
from unittest.mock import Mock, AsyncMock

from src.application.usecases.new_analysis_usecase import (
    NewAnalysisUseCase, 
    NewAnalysisRequest
)

class TestNewAnalysisUseCase:
    def setup_method(self):
        self.mock_analyzer = Mock()
        self.mock_logger = Mock()
        self.usecase = NewAnalysisUseCase(
            new_analyzer=self.mock_analyzer,
            logger=self.mock_logger
        )
    
    @pytest.mark.asyncio
    async def test_successful_analysis(self):
        """正常な分析処理のテスト"""
        # Arrange
        self.mock_analyzer.analyze_with_prompt = AsyncMock(
            return_value={
                "success": True,
                "raw_response": {"detected": ["object1", "object2"]},
                "metadata": {"model": "gemini-2.5-flash"}
            }
        )
        
        request = NewAnalysisRequest(
            data_path="/test/image.jpg",
            analysis_type="object_detection"
        )
        
        # Act
        response = await self.usecase.execute(request)
        
        # Assert
        assert response.success is True
        assert response.analysis_result == {"detected": ["object1", "object2"]}
        self.mock_analyzer.analyze_with_prompt.assert_called_once()
```

## 📋 チェックリスト

### ✅ 設計チェック
- [ ] **技術機能のみに特化**（ビジネス概念なし）
- [ ] **Protocol定義済み**（Infrastructure抽象化）
- [ ] **レイヤー責務明確**（Infrastructure→UseCase→Tool→Agent）
- [ ] **Agent-First設計準拠**（Toolは薄いアダプター）

### ✅ 実装チェック  
- [ ] **型アノテーション完備**
- [ ] **エラーハンドリング実装**
- [ ] **ロガーDI注入**（個別初期化禁止）
- [ ] **import文先頭配置**

### ✅ 統合チェック
- [ ] **CompositionRoot登録完了**
- [ ] **Agent統合完了**
- [ ] **動作テスト通過**
- [ ] **API整合性確認**

### ✅ 禁止事項回避チェック
- [ ] **ビジネスロジック含まない**（child_id, advice等の概念なし）
- [ ] **プロンプト構築はUseCase層のみ**（Infrastructure層では禁止）
- [ ] **グローバル変数不使用**
- [ ] **個別ロガー初期化なし**

## 🎯 まとめ

### **Agent-Firstツール開発の原則**

1. **Agent中心**: ツールは技術機能のみ、判断・アドバイスはAgent
2. **薄いアダプター**: ToolはUseCaseへの橋渡しのみ
3. **技術特化**: ビジネス概念（child_id, advice等）は一切含まない
4. **Protocol抽象化**: Infrastructure層の実装詳細を隠蔽
5. **DI統合**: 全コンポーネントのComposition Root統合

### **開発フロー**
```
技術仕様定義 → Protocol作成 → Infrastructure実装 → UseCase実装 → Tool実装 → Agent統合 → テスト
```

このガイドに従うことで、GenieUsのAgent-Firstアーキテクチャに適合した、保守しやすく拡張しやすい新ツールを開発できます。

---

**💡 重要**: 新ツール開発時は必ず[コーディング規約](../development/coding-standards.md)と[アーキテクチャ概要](../architecture/overview.md)を参照してください。