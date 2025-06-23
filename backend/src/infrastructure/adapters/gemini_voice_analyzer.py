"""Gemini音声分析アダプター
ADK非依存の実装クラス
"""

import logging
from typing import Any

import google.generativeai as genai

from src.application.interface.protocols.voice_analyzer import VoiceAnalyzerProtocol


class GeminiVoiceAnalyzer(VoiceAnalyzerProtocol):
    """Geminiを使用した音声テキスト分析の具体的実装"""

    def __init__(self, model_name: str = "gemini-2.5-flash-preview-05-20", logger: logging.Logger | None = None):
        self.model_name = model_name
        self.logger = logger or logging.getLogger(__name__)
        self.model = genai.GenerativeModel(model_name)

    async def analyze_text_with_prompt(
        self,
        text: str,
        prompt: str,
        model_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """テキストとプロンプトでAI分析を実行（純粋な技術実装）"""
        try:
            # モデル設定の適用
            if model_options:
                # temperature, max_tokens等の設定をここで適用
                pass

            # Gemini APIコール（プロンプトはそのまま使用）
            response = await self.model.generate_content_async(prompt)

            # 生レスポンスを返す（最小限の技術的処理のみ）
            result = {
                "raw_response": response.text,
                "model_name": self.model_name,
                "success": True,
                "timestamp": self._get_current_timestamp(),
            }

            self.logger.info("Gemini text analysis API call completed")
            return result

        except Exception as e:
            self.logger.error(f"Gemini text analysis API error: {e}")
            return {
                "raw_response": "",
                "model_name": self.model_name,
                "success": False,
                "error": str(e),
                "timestamp": self._get_current_timestamp(),
            }

    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        from datetime import datetime

        return datetime.now().isoformat()
