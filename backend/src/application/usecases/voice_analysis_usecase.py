"""音声分析UseCase"""

import logging
from typing import Any

from src.application.interface.protocols.voice_analyzer import VoiceAnalyzerProtocol


class VoiceAnalysisUseCase:
    """音声分析のビジネスロジック"""

    def __init__(self, voice_analyzer: VoiceAnalyzerProtocol, logger: logging.Logger) -> None:
        self.voice_analyzer = voice_analyzer
        self.logger = logger

    async def analyze_child_voice(
        self,
        voice_text: str,
        child_id: str,
        analysis_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """子どもの音声テキストを分析してデータを抽出

        Args:
            voice_text: 音声認識されたテキスト
            child_id: 子どものID
            analysis_context: 分析のためのコンテキスト情報

        Returns:
            Dict[str, Any]: 分析結果

        """
        try:
            self.logger.info(f"音声分析開始: child_id={child_id}, text_length={len(voice_text)}")

            # ビジネスロジック: 子育て記録用プロンプトの構築
            prompt = self._build_childcare_voice_analysis_prompt(voice_text, child_id, analysis_context)

            # Infrastructure層の音声分析を実行（純粋な技術実装）
            raw_result = await self.voice_analyzer.analyze_text_with_prompt(
                text=voice_text,
                prompt=prompt,
            )

            # ビジネスロジック: AIレスポンスをビジネス概念に変換
            result = self._transform_to_childcare_analysis(raw_result, child_id)

            # ビジネスロジック: 結果の後処理・検証
            validated_result = self._validate_analysis_result(result)

            self.logger.info(
                f"音声分析完了: child_id={child_id}, events_count={len(validated_result.get('events', []))}",
            )

            return validated_result

        except Exception as e:
            self.logger.error(f"音声分析UseCase実行エラー: {e}")
            return self._create_error_response(str(e))

    def _build_childcare_voice_analysis_prompt(
        self,
        voice_text: str,
        child_id: str,
        analysis_context: dict[str, Any] | None = None,
    ) -> str:
        """子育て記録用音声分析プロンプトの構築（ビジネスロジック）"""
        analysis_type = analysis_context.get("analysis_type", "general") if analysis_context else "general"

        return f"""
        あなたは子育て記録の専門分析AIです。以下の音声テキストから、子供の育児記録を構造化データとして抽出してください。

        音声テキスト: "{voice_text}"
        子供ID: {child_id}
        分析タイプ: {analysis_type}

        以下のJSON形式で回答してください：
        {{
            "events": [
                {{
                    "type": "feeding/sleep/mood/activity/milestone",
                    "description": "イベントの説明",
                    "time": "相対時間表現（例：さっき、10分前、14:30）",
                    "confidence": 0.0-1.0,
                    "details": {{
                        "amount_ml": 数値（feeding時）,
                        "food_type": "食品名",
                        "duration_minutes": 数値（sleep時）,
                        "quality": "良好/普通/不調",
                        "mood_score": 0.0-1.0（mood時）,
                        "mood_description": "機嫌の説明"
                    }}
                }}
            ],
            "overall_confidence": 0.0-1.0,
            "insights": ["抽出された洞察のリスト"],
            "emotional_tone": "positive/neutral/concerned"
        }}

        重要な注意：
        - 時間表現は可能な限り具体的に解釈
        - 数値は正確に抽出
        - 不明な項目はnullまたは空文字列
        - 複数のイベントが含まれる場合は全て抽出
        - 親の感情状態も考慮してinsightsを生成
        """.strip()

    def _parse_ai_response(self, raw_response: str) -> dict[str, Any]:
        """AIの生レスポンスをJSONパース（ビジネスロジック）"""
        try:
            import json

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
                "events": [],
                "overall_confidence": 0.2,
                "insights": ["AI応答の解析中にエラーが発生しました"],
                "emotional_tone": "neutral",
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
            "events": parsed_data.get("events", []),
            "overall_confidence": parsed_data.get("overall_confidence", 0),
            "insights": parsed_data.get("insights", []),
            "emotional_tone": parsed_data.get("emotional_tone", "neutral"),
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
        required_fields = ["events", "overall_confidence", "insights", "emotional_tone"]
        for field in required_fields:
            if field not in result:
                result[field] = self._get_default_value(field)

        # 信頼度の正規化
        confidence = result.get("overall_confidence", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            result["overall_confidence"] = 0.3  # デフォルト値

        # イベントデータの検証
        events = result.get("events", [])
        validated_events = []
        for event in events:
            if isinstance(event, dict) and "type" in event:
                # 各イベントの信頼度も正規化
                event_confidence = event.get("confidence", 0.5)
                if not isinstance(event_confidence, (int, float)) or event_confidence < 0 or event_confidence > 1:
                    event["confidence"] = 0.5
                validated_events.append(event)

        result["events"] = validated_events

        # 感情トーンの正規化
        valid_tones = ["positive", "neutral", "concerned", "unknown"]
        if result.get("emotional_tone") not in valid_tones:
            result["emotional_tone"] = "neutral"

        return result

    def _get_default_value(self, field: str) -> Any:
        """フィールドのデフォルト値を取得"""
        defaults = {
            "events": [],
            "overall_confidence": 0.2,
            "insights": ["音声解析が部分的に完了しました"],
            "emotional_tone": "neutral",
        }
        return defaults.get(field, "")

    def _create_error_response(self, error_message: str) -> dict[str, Any]:
        """エラー時のレスポンス作成"""
        return {
            "success": False,
            "error": error_message,
            "events": [],
            "overall_confidence": 0.0,
            "insights": ["音声解析中にエラーが発生しました。後でもう一度お試しください。"],
            "emotional_tone": "unknown",
        }
