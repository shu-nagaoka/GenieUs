import json
import logging
from typing import Any

from src.application.interface.protocols.image_analyzer import ImageAnalyzerProtocol


class ImageAnalysisUseCase:
    """画像解析のビジネスロジック"""

    def __init__(self, image_analyzer: ImageAnalyzerProtocol, logger: logging.Logger) -> None:
        self.image_analyzer = image_analyzer
        self.logger = logger

    async def analyze_child_image(
        self,
        image_path: str,
        child_id: str,
        analysis_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """子どもの画像を分析してデータを抽出

        Args:
            image_path: 画像ファイルのパス
            child_id: 子どものID
            analysis_context: 分析のためのコンテキスト情報

        Returns:
            Dict[str, Any]: 分析結果

        """
        try:
            self.logger.info(f"画像分析開始: child_id={child_id}, image_path={image_path}")

            # ビジネスロジック: 子育て記録用プロンプトの構築
            prompt = self._build_childcare_analysis_prompt(child_id, analysis_context)

            # Infrastructure層の画像分析を実行（純粋な技術実装）
            raw_result = await self.image_analyzer.analyze_image_with_prompt(
                image_path=image_path,
                prompt=prompt,
            )

            # ビジネスロジック: AIレスポンスをビジネス概念に変換
            result = self._transform_to_childcare_analysis(raw_result, child_id)

            # ビジネスロジック: 結果の後処理・検証
            validated_result = self._validate_analysis_result(result)

            self.logger.info(f"画像分析完了: child_id={child_id}, confidence={validated_result.get('confidence', 0)}")

            return validated_result

        except Exception as e:
            self.logger.error(f"画像分析UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    def _build_childcare_analysis_prompt(self, child_id: str, analysis_context: dict[str, Any] | None = None) -> str:
        """子育て記録用画像分析プロンプトの構築（ビジネスロジック）"""
        analysis_type = analysis_context.get("analysis_type", "general") if analysis_context else "general"

        return f"""
        あなたは子育て記録の画像分析専門AIです。この画像から子供の育児記録を抽出してください。

        子供ID: {child_id}
        分析タイプ: {analysis_type}

        以下の観点で分析し、JSON形式で回答してください：
        {{
            "detected_items": ["検出された物品・食品リスト"],
            "estimated_data": {{
                "food_amount": "少量/適量/多め",
                "food_category": "離乳食/ミルク/おやつ/その他",
                "meal_progress": "完食/半分/少し/未摂取"
            }},
            "emotion_detected": "happy/neutral/sad/excited/tired/unknown",
            "activity_type": "eating/playing/sleeping/learning/outdoor",
            "developmental_indicators": ["観察された発達指標"],
            "safety_concerns": ["安全上の懸念事項"],
            "confidence": 0.0-1.0,
            "suggestions": ["親へのアドバイス"],
            "extracted_events": [
                {{
                    "type": "feeding/mood/activity/milestone",
                    "description": "イベントの詳細",
                    "confidence": 0.0-1.0
                }}
            ]
        }}

        特に注目する点：
        - 離乳食や食事の量・種類
        - 子供の表情や状態
        - 周囲の環境
        - 発達段階に関する手がかり
        - 安全性への配慮事項
        """.strip()

    def _parse_ai_response(self, raw_response: str) -> dict[str, Any]:
        """AIの生レスポンスをJSONパース（ビジネスロジック）"""
        try:
            # ```json```で囲まれている場合を考慮
            if "```json" in raw_response:
                json_start = raw_response.find("```json") + 7
                json_end = raw_response.find("```", json_start)
                raw_response = raw_response[json_start:json_end]
            elif "```" in raw_response:
                json_start = raw_response.find("```") + 3
                json_end = raw_response.find("```", json_start)
                raw_response = raw_response[json_start:json_end]

            return json.loads(raw_response.strip())

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"AI レスポンスのJSON解析に失敗: {e}")
            return {
                "detected_items": [],
                "confidence": 0.2,
                "suggestions": ["AI応答の解析中にエラーが発生しました"],
                "emotion_detected": "unknown",
                "activity_type": "unknown",
                "extracted_events": [],
            }

    def _transform_to_childcare_analysis(self, raw_result: dict[str, Any], child_id: str) -> dict[str, Any]:
        """AIレスポンスをビジネス概念（子育て記録）に変換"""
        if not raw_result.get("success", False):
            return self._create_error_response(raw_result.get("error", "AI分析が失敗しました"))

        # AIの生レスポンスをパース
        raw_response = raw_result.get("raw_response", "")
        parsed_data = self._parse_ai_response(raw_response)

        # ビジネスロジック: 子育て関連の解釈（パースされたデータをそのまま活用）
        childcare_result = {
            "child_id": child_id,  # ここでビジネス概念を付与
            "detected_items": parsed_data.get("detected_items", []),
            "confidence": parsed_data.get("confidence", 0),
            "suggestions": parsed_data.get("suggestions", []),
            "emotion_detected": parsed_data.get("emotion_detected", "unknown"),
            "activity_type": parsed_data.get("activity_type", "unknown"),
            "extracted_events": parsed_data.get("extracted_events", []),
            "safety_concerns": parsed_data.get("safety_concerns", []),
            "timestamp": self._get_current_timestamp(),
            "ai_model": raw_result.get("model_name", "unknown"),
        }

        return childcare_result

    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        from datetime import datetime

        return datetime.now().isoformat()

    def _validate_analysis_result(self, result: dict[str, Any]) -> dict[str, Any]:
        """分析結果の検証・正規化"""
        # 必須フィールドの確認
        required_fields = ["detected_items", "confidence", "suggestions"]
        for field in required_fields:
            if field not in result:
                result[field] = self._get_default_value(field)

        # 信頼度の正規化
        confidence = result.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            result["confidence"] = 0.3  # デフォルト値

        # 安全性チェック
        safety_concerns = result.get("safety_concerns", [])
        if safety_concerns:
            result["has_safety_concerns"] = True
            self.logger.warning(f"安全性懸念を検出: {safety_concerns}")
        else:
            result["has_safety_concerns"] = False

        return result

    def _get_default_value(self, field: str) -> Any:
        """フィールドのデフォルト値を取得"""
        defaults = {
            "detected_items": [],
            "confidence": 0.2,
            "suggestions": ["画像解析が部分的に完了しました"],
            "emotion_detected": "unknown",
            "activity_type": "unknown",
            "extracted_events": [],
        }
        return defaults.get(field, "")

    def _create_error_response(self, error_message: str) -> dict[str, Any]:
        """エラー時のレスポンス作成"""
        return {
            "success": False,
            "error": error_message,
            "detected_items": [],
            "confidence": 0.0,
            "suggestions": ["画像解析中にエラーが発生しました。後でもう一度お試しください。"],
            "emotion_detected": "unknown",
            "activity_type": "unknown",
            "extracted_events": [],
            "has_safety_concerns": False,
        }
