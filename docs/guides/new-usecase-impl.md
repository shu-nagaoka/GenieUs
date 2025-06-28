# 新UseCase実装ガイド

GenieUs Clean Architecture + Composition Rootでの新UseCase実装完全ガイド

## 🎯 UseCase層の責務と設計原則

### **UseCase層の明確な責務**

```
Application Layer (UseCase) 責務:
✅ ビジネスロジック調整・オーケストレーション
✅ 外部システム呼び出しの組み合わせ
✅ AI用プロンプト構築（Infrastructure層では禁止）
✅ データ変換・検証
✅ エラーハンドリング・フォールバック

❌ Infrastructure層への責務の漏洩（禁止）
❌ Agent層の判断・アドバイス生成（Agent専用）
❌ Tool層のADK統合処理（Tool専用）
```

### **Agent-Firstアーキテクチャでのポジション**

```
Agent Layer ← 判断・アドバイス・ルーティング（AI-powered）
    ↓
Tool Layer ← Agent-Application間の薄いアダプター
    ↓
Application Layer (UseCase) ← ビジネスロジック調整（ここを実装）
    ↓
Infrastructure Layer ← 純粋技術実装（プロンプト構築禁止）
```

## 🚀 新UseCase実装手順

### Step 1: UseCase仕様定義

#### 1.1 ビジネス要件の特定
```python
"""
UseCase名: MultiModalContentAnalysisUseCase
ビジネス要件: 
- 画像・音声・テキストを統合分析
- 複数のAI技術を組み合わせ
- 結果の統合・検証・フォーマット

技術調整範囲:
✅ 複数Infrastructure層の呼び出し順序
✅ AI用プロンプト構築・最適化  
✅ 結果の統合・検証・変換
✅ エラー時のフォールバック戦略

除外事項（他層の責務）:
❌ Agent判断・アドバイス生成
❌ Infrastructure技術実装詳細
❌ Tool ADK統合処理
"""
```

#### 1.2 依存関係の特定
```python
# 必要なInfrastructure Protocol
- ImageAnalyzerProtocol: 画像分析技術
- VoiceAnalyzerProtocol: 音声分析技術  
- TextAnalyzerProtocol: テキスト分析技術（新規）

# 必要な設定・ユーティリティ
- Settings: AI関連設定
- Logger: 構造化ログ
```

### Step 2: Request/Response定義

```python
# backend/src/application/usecases/multimodal_content_analysis_usecase.py
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class ContentType(Enum):
    """コンテンツタイプ列挙"""
    IMAGE = "image"
    VOICE = "voice"  
    TEXT = "text"
    MIXED = "mixed"

@dataclass
class ContentItem:
    """分析対象コンテンツアイテム"""
    content_type: ContentType
    content_path: str
    metadata: Dict[str, Any] | None = None

@dataclass
class MultiModalAnalysisRequest:
    """マルチモーダル分析リクエスト"""
    content_items: List[ContentItem]
    analysis_purpose: str  # "comprehensive", "safety_check", "educational"
    custom_instructions: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None

@dataclass
class AnalysisResult:
    """個別分析結果"""
    content_type: ContentType
    success: bool
    analysis_data: Dict[str, Any]
    confidence_score: float
    processing_time_ms: int
    error: Optional[str] = None

@dataclass  
class MultiModalAnalysisResponse:
    """マルチモーダル分析レスポンス"""
    success: bool
    individual_results: List[AnalysisResult]
    integrated_insights: Dict[str, Any]
    summary: str
    confidence_overall: float
    metadata: Dict[str, Any]
    error: Optional[str] = None
```

### Step 3: UseCase本体実装

```python
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from src.application.interface.protocols.image_analyzer import ImageAnalyzerProtocol
from src.application.interface.protocols.voice_analyzer import VoiceAnalyzerProtocol
from src.application.interface.protocols.text_analyzer import TextAnalyzerProtocol
from src.config.settings import AppSettings

class MultiModalContentAnalysisUseCase:
    """マルチモーダルコンテンツ分析UseCase
    
    責務:
    - 複数のInfrastructure層技術の組み合わせ
    - AI用プロンプト構築・最適化
    - 分析結果の統合・検証
    - エラーハンドリング・フォールバック
    """
    
    def __init__(
        self,
        image_analyzer: ImageAnalyzerProtocol,
        voice_analyzer: VoiceAnalyzerProtocol,
        text_analyzer: TextAnalyzerProtocol,
        settings: AppSettings,
        logger: logging.Logger
    ):
        """コンストラクタ（DI注入）"""
        self.image_analyzer = image_analyzer
        self.voice_analyzer = voice_analyzer
        self.text_analyzer = text_analyzer
        self.settings = settings
        self.logger = logger
    
    async def execute(
        self, 
        request: MultiModalAnalysisRequest
    ) -> MultiModalAnalysisResponse:
        """マルチモーダル分析実行（メインエントリーポイント）"""
        
        start_time = datetime.now()
        self.logger.info(
            "マルチモーダル分析開始",
            extra={
                "content_count": len(request.content_items),
                "analysis_purpose": request.analysis_purpose
            }
        )
        
        try:
            # Step 1: 並列で個別分析実行
            individual_results = await self._execute_parallel_analysis(
                request.content_items, 
                request.analysis_purpose,
                request.custom_instructions
            )
            
            # Step 2: 結果統合・検証
            integrated_insights = await self._integrate_analysis_results(
                individual_results,
                request.analysis_purpose
            )
            
            # Step 3: サマリー生成
            summary = await self._generate_integrated_summary(
                integrated_insights,
                individual_results
            )
            
            # Step 4: 全体信頼度計算
            overall_confidence = self._calculate_overall_confidence(
                individual_results
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "マルチモーダル分析完了",
                extra={
                    "success": True,
                    "processing_time_ms": processing_time,
                    "overall_confidence": overall_confidence
                }
            )
            
            return MultiModalAnalysisResponse(
                success=True,
                individual_results=individual_results,
                integrated_insights=integrated_insights,
                summary=summary,
                confidence_overall=overall_confidence,
                metadata={
                    "processing_time_ms": processing_time,
                    "analysis_purpose": request.analysis_purpose,
                    "content_types": [item.content_type.value for item in request.content_items]
                }
            )
            
        except Exception as e:
            self.logger.error(
                "マルチモーダル分析エラー",
                extra={
                    "error": str(e),
                    "analysis_purpose": request.analysis_purpose
                }
            )
            
            # フォールバック応答
            return self._create_fallback_response(str(e))
    
    async def _execute_parallel_analysis(
        self,
        content_items: List[ContentItem],
        analysis_purpose: str,
        custom_instructions: Optional[str]
    ) -> List[AnalysisResult]:
        """並列個別分析実行（ビジネスロジック）"""
        
        tasks = []
        for item in content_items:
            task = self._analyze_single_content(
                item, 
                analysis_purpose, 
                custom_instructions
            )
            tasks.append(task)
        
        # 並列実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 例外処理
        analysis_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"コンテンツ{i}分析エラー: {result}")
                analysis_results.append(
                    self._create_error_result(content_items[i].content_type, str(result))
                )
            else:
                analysis_results.append(result)
        
        return analysis_results
    
    async def _analyze_single_content(
        self,
        content_item: ContentItem,
        analysis_purpose: str,
        custom_instructions: Optional[str]
    ) -> AnalysisResult:
        """単一コンテンツ分析（Infrastructure層呼び出し）"""
        
        start_time = datetime.now()
        
        try:
            # UseCase層でプロンプト構築（ビジネス要件に基づく）
            prompt = self._build_analysis_prompt(
                content_item.content_type,
                analysis_purpose,
                custom_instructions
            )
            
            # 適切なInfrastructure層を選択・呼び出し
            if content_item.content_type == ContentType.IMAGE:
                result = await self.image_analyzer.analyze_image_with_prompt(
                    content_item.content_path, 
                    prompt
                )
            elif content_item.content_type == ContentType.VOICE:
                result = await self.voice_analyzer.analyze_voice_with_prompt(
                    content_item.content_path, 
                    prompt
                )
            elif content_item.content_type == ContentType.TEXT:
                result = await self.text_analyzer.analyze_text_with_prompt(
                    content_item.content_path, 
                    prompt
                )
            else:
                raise ValueError(f"未対応のコンテンツタイプ: {content_item.content_type}")
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return AnalysisResult(
                content_type=content_item.content_type,
                success=result.get("success", False),
                analysis_data=result.get("raw_response", {}),
                confidence_score=self._extract_confidence(result),
                processing_time_ms=int(processing_time),
                error=result.get("error")
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            return AnalysisResult(
                content_type=content_item.content_type,
                success=False,
                analysis_data={},
                confidence_score=0.0,
                processing_time_ms=int(processing_time),
                error=str(e)
            )
    
    def _build_analysis_prompt(
        self,
        content_type: ContentType,
        analysis_purpose: str,
        custom_instructions: Optional[str]
    ) -> str:
        """分析用プロンプト構築（UseCase層の重要責務）"""
        
        # ベースプロンプト（分析目的別）
        base_prompts = {
            "comprehensive": {
                ContentType.IMAGE: "この画像を詳細に分析し、以下の観点で情報を抽出してください：\n- 主要なオブジェクト・人物\n- 環境・場所\n- 色彩・構図\n- テキスト・文字情報",
                ContentType.VOICE: "この音声を詳細に分析し、以下の観点で情報を抽出してください：\n- 話者の特徴\n- 感情・トーン\n- 内容・キーワード\n- 環境音・背景",
                ContentType.TEXT: "このテキストを詳細に分析し、以下の観点で情報を抽出してください：\n- 主要なトピック\n- 感情・トーン\n- キーワード・エンティティ\n- 文章構造"
            },
            "safety_check": {
                ContentType.IMAGE: "この画像の安全性を評価してください。不適切な内容、危険な要素がないかチェックしてください。",
                ContentType.VOICE: "この音声の内容の安全性を評価してください。不適切な発言、危険な内容がないかチェックしてください。",
                ContentType.TEXT: "このテキストの安全性を評価してください。不適切な表現、危険な内容がないかチェックしてください。"
            },
            "educational": {
                ContentType.IMAGE: "この画像を教育的観点で分析してください。学習価値、教材としての適性を評価してください。",
                ContentType.VOICE: "この音声を教育的観点で分析してください。学習価値、教材としての適性を評価してください。",
                ContentType.TEXT: "このテキストを教育的観点で分析してください。学習価値、教材としての適性を評価してください。"
            }
        }
        
        # ベースプロンプト取得
        prompt = base_prompts.get(analysis_purpose, {}).get(
            content_type, 
            f"この{content_type.value}を分析してください。"
        )
        
        # カスタム指示追加
        if custom_instructions:
            prompt += f"\n\n追加指示:\n{custom_instructions}"
        
        # 出力フォーマット指定
        prompt += "\n\nJSON形式で結果を返してください。"
        
        return prompt
    
    async def _integrate_analysis_results(
        self,
        individual_results: List[AnalysisResult],
        analysis_purpose: str
    ) -> Dict[str, Any]:
        """分析結果統合（ビジネスロジック）"""
        
        # 成功した結果のみを抽出
        successful_results = [r for r in individual_results if r.success]
        
        if not successful_results:
            return {"integration_status": "no_successful_results"}
        
        # 結果タイプ別グループ化
        results_by_type = {}
        for result in successful_results:
            content_type = result.content_type.value
            if content_type not in results_by_type:
                results_by_type[content_type] = []
            results_by_type[content_type].append(result.analysis_data)
        
        # クロスモーダル統合ロジック
        integrated = {
            "content_types_analyzed": list(results_by_type.keys()),
            "integration_method": analysis_purpose,
            "cross_modal_insights": self._extract_cross_modal_insights(results_by_type),
            "consistency_check": self._check_result_consistency(results_by_type),
            "quality_metrics": self._calculate_quality_metrics(successful_results)
        }
        
        return integrated
    
    def _extract_cross_modal_insights(
        self, 
        results_by_type: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """クロスモーダル洞察抽出（高度なビジネスロジック）"""
        
        insights = {}
        
        # 画像+音声の組み合わせ
        if "image" in results_by_type and "voice" in results_by_type:
            insights["visual_audio_correlation"] = "detected"
            # 具体的な相関分析ロジック
        
        # 画像+テキストの組み合わせ  
        if "image" in results_by_type and "text" in results_by_type:
            insights["visual_text_correlation"] = "detected"
            # 具体的な相関分析ロジック
        
        # 全ての組み合わせ
        if len(results_by_type) >= 3:
            insights["multimodal_coherence"] = "high"
            # 多次元整合性分析ロジック
        
        return insights
    
    async def _generate_integrated_summary(
        self,
        integrated_insights: Dict[str, Any],
        individual_results: List[AnalysisResult]
    ) -> str:
        """統合サマリー生成（UseCase層でのプロンプト構築）"""
        
        # サマリー用プロンプト構築
        prompt = self._build_summary_prompt(integrated_insights, individual_results)
        
        # テキスト分析器を使用してサマリー生成
        try:
            result = await self.text_analyzer.analyze_text_with_prompt("", prompt)
            return result.get("raw_response", "サマリー生成に失敗しました")
        except Exception as e:
            self.logger.error(f"サマリー生成エラー: {e}")
            return "統合分析を実行しましたが、サマリー生成中にエラーが発生しました。"
    
    def _build_summary_prompt(
        self,
        integrated_insights: Dict[str, Any],
        individual_results: List[AnalysisResult]
    ) -> str:
        """サマリー生成用プロンプト構築"""
        
        prompt = "以下のマルチモーダル分析結果を統合して、簡潔で分かりやすいサマリーを生成してください：\n\n"
        
        # 個別結果の要約
        for i, result in enumerate(individual_results):
            if result.success:
                prompt += f"{i+1}. {result.content_type.value}分析結果:\n"
                prompt += f"   信頼度: {result.confidence_score}\n"
                prompt += f"   主要な発見: {str(result.analysis_data)[:200]}...\n\n"
        
        # 統合洞察
        prompt += f"統合洞察:\n{integrated_insights}\n\n"
        
        prompt += "上記を踏まえ、全体的な分析結果を3-5文で要約してください。"
        
        return prompt
    
    def _calculate_overall_confidence(
        self, 
        individual_results: List[AnalysisResult]
    ) -> float:
        """全体信頼度計算"""
        
        successful_results = [r for r in individual_results if r.success]
        
        if not successful_results:
            return 0.0
        
        # 重み付き平均（処理時間も考慮）
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for result in successful_results:
            # 処理時間が短いほど重み大（品質指標）
            time_weight = max(0.1, 1.0 / (result.processing_time_ms / 1000 + 1))
            weighted_confidence = result.confidence_score * time_weight
            
            total_weighted_confidence += weighted_confidence
            total_weight += time_weight
        
        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _check_result_consistency(
        self, 
        results_by_type: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """結果整合性チェック（ビジネスロジック）"""
        return {
            "consistency_score": 0.85,  # 実際の整合性分析ロジック
            "inconsistencies": [],
            "validation_status": "passed"
        }
    
    def _calculate_quality_metrics(
        self, 
        successful_results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """品質メトリクス計算"""
        return {
            "avg_confidence": sum(r.confidence_score for r in successful_results) / len(successful_results),
            "avg_processing_time": sum(r.processing_time_ms for r in successful_results) / len(successful_results),
            "success_rate": len(successful_results) / len(successful_results) if successful_results else 0
        }
    
    def _extract_confidence(self, result: Dict[str, Any]) -> float:
        """信頼度抽出（結果パース）"""
        # Infrastructure層の結果から信頼度を抽出
        metadata = result.get("metadata", {})
        return metadata.get("confidence", 0.8)  # デフォルト値
    
    def _create_error_result(
        self, 
        content_type: ContentType, 
        error: str
    ) -> AnalysisResult:
        """エラー結果作成"""
        return AnalysisResult(
            content_type=content_type,
            success=False,
            analysis_data={},
            confidence_score=0.0,
            processing_time_ms=0,
            error=error
        )
    
    def _create_fallback_response(self, error: str) -> MultiModalAnalysisResponse:
        """フォールバック応答作成"""
        return MultiModalAnalysisResponse(
            success=False,
            individual_results=[],
            integrated_insights={"fallback": True},
            summary="分析中にエラーが発生しました。しばらく待ってから再試行してください。",
            confidence_overall=0.0,
            metadata={"error_recovery": True},
            error=error
        )
```

### Step 4: Composition Root統合

```python
# backend/src/di_provider/composition_root.py

class CompositionRoot:
    def _build_application_layer(self):
        """Application Layer構築"""
        
        # 既存のUseCase
        image_analysis_usecase = ImageAnalysisUseCase(
            image_analyzer=self._infrastructure.get("image_analyzer"),
            logger=self.logger
        )
        
        # 新しいUseCase追加
        multimodal_analysis_usecase = MultiModalContentAnalysisUseCase(
            image_analyzer=self._infrastructure.get("image_analyzer"),
            voice_analyzer=self._infrastructure.get("voice_analyzer"),
            text_analyzer=self._infrastructure.get("text_analyzer"),
            settings=self.settings,
            logger=self.logger
        )
        
        # 登録
        self._usecases.register("image_analysis", image_analysis_usecase)
        self._usecases.register("multimodal_analysis", multimodal_analysis_usecase)
```

### Step 5: API統合（オプション）

```python
# backend/src/presentation/api/routes/multimodal_analysis.py
from fastapi import APIRouter, Depends, HTTPException, Request
from src.application.usecases.multimodal_content_analysis_usecase import (
    MultiModalContentAnalysisUseCase,
    MultiModalAnalysisRequest
)

router = APIRouter(tags=["multimodal"])

@router.post("/multimodal/analyze")
async def analyze_multimodal_content(
    request: MultiModalAnalysisRequest,
    usecase: MultiModalContentAnalysisUseCase = Depends(get_multimodal_analysis_usecase),
) -> dict:
    """マルチモーダルコンテンツ分析API"""
    
    try:
        response = await usecase.execute(request)
        return {
            "success": response.success,
            "summary": response.summary,
            "confidence": response.confidence_overall,
            "results": response.individual_results,
            "insights": response.integrated_insights,
            "metadata": response.metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🧪 テスト実装

```python
# tests/test_multimodal_content_analysis_usecase.py
import pytest
from unittest.mock import Mock, AsyncMock

from src.application.usecases.multimodal_content_analysis_usecase import (
    MultiModalContentAnalysisUseCase,
    MultiModalAnalysisRequest,
    ContentItem,
    ContentType
)

class TestMultiModalContentAnalysisUseCase:
    def setup_method(self):
        self.mock_image_analyzer = Mock()
        self.mock_voice_analyzer = Mock()
        self.mock_text_analyzer = Mock()
        self.mock_settings = Mock()
        self.mock_logger = Mock()
        
        self.usecase = MultiModalContentAnalysisUseCase(
            image_analyzer=self.mock_image_analyzer,
            voice_analyzer=self.mock_voice_analyzer,
            text_analyzer=self.mock_text_analyzer,
            settings=self.mock_settings,
            logger=self.mock_logger
        )
    
    @pytest.mark.asyncio
    async def test_successful_multimodal_analysis(self):
        """正常なマルチモーダル分析のテスト"""
        # Arrange
        self.mock_image_analyzer.analyze_image_with_prompt = AsyncMock(
            return_value={
                "success": True,
                "raw_response": {"objects": ["cat", "chair"]},
                "metadata": {"confidence": 0.9}
            }
        )
        
        self.mock_voice_analyzer.analyze_voice_with_prompt = AsyncMock(
            return_value={
                "success": True,
                "raw_response": {"transcript": "Hello world"},
                "metadata": {"confidence": 0.8}
            }
        )
        
        self.mock_text_analyzer.analyze_text_with_prompt = AsyncMock(
            return_value={
                "success": True,
                "raw_response": "分析結果の統合サマリー",
                "metadata": {"confidence": 0.95}
            }
        )
        
        request = MultiModalAnalysisRequest(
            content_items=[
                ContentItem(ContentType.IMAGE, "/test/image.jpg"),
                ContentItem(ContentType.VOICE, "/test/audio.wav")
            ],
            analysis_purpose="comprehensive"
        )
        
        # Act
        response = await self.usecase.execute(request)
        
        # Assert
        assert response.success is True
        assert len(response.individual_results) == 2
        assert response.confidence_overall > 0.0
        assert "統合" in response.summary or "分析" in response.summary
```

## 📋 チェックリスト

### ✅ 設計チェック
- [ ] **レイヤー責務明確**（ビジネスロジック調整のみ）
- [ ] **Infrastructure層への適切な委譲**
- [ ] **Protocol使用による抽象化**
- [ ] **Agent層との責務分離**（判断・アドバイス生成はAgent専用）

### ✅ 実装チェック
- [ ] **Request/Response型定義済み**
- [ ] **非同期処理対応**（async/await）
- [ ] **並列処理活用**（asyncio.gather）
- [ ] **エラーハンドリング・フォールバック実装**
- [ ] **プロンプト構築実装**（UseCase層の重要責務）

### ✅ 品質チェック
- [ ] **型アノテーション完備**
- [ ] **構造化ログ実装**
- [ ] **DI注入済み**（個別初期化禁止）
- [ ] **import文先頭配置**
- [ ] **テストケース実装**

### ✅ 統合チェック
- [ ] **Composition Root登録完了**
- [ ] **API統合完了**（必要に応じて）
- [ ] **動作テスト通過**

## 🎯 まとめ

### **UseCase実装の重要原則**

1. **ビジネスロジック調整**: 複数Infrastructure層の組み合わせ・オーケストレーション
2. **プロンプト構築責務**: AI用プロンプトはUseCase層で構築（Infrastructure層では禁止）
3. **エラーハンドリング**: 段階的フォールバック・復旧戦略
4. **並列処理活用**: 複数の外部システム呼び出しの効率化
5. **結果統合・検証**: 複数の結果を統合し、ビジネス価値を創出

### **Agent-Firstアーキテクチャでの位置づけ**
- **Agent**: 判断・アドバイス・ルーティング（AI-powered）
- **UseCase**: ビジネスロジック調整・技術統合（この層を実装）
- **Infrastructure**: 純粋技術実装（プロンプト構築禁止）

この設計により、保守しやすく、テストしやすく、拡張しやすいUseCase実装が可能になります。

---

**💡 重要**: UseCase実装時は[UseCase設計ルール](../technical/usecase-design-rules.md)と[アーキテクチャ概要](../architecture/overview.md)を必ず参照してください。