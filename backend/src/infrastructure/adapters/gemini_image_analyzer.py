"""Gemini画像分析アダプター
ADK非依存の実装クラス
"""

import json
import logging
from typing import Any

import google.generativeai as genai
import PIL.Image

from src.application.interface.protocols.image_analyzer import ImageAnalyzerProtocol


class GeminiImageAnalyzer(ImageAnalyzerProtocol):
    """Geminiを使用した画像分析の具体的実装"""

    def __init__(self, model_name: str = "gemini-2.5-flash-preview-05-20", logger: logging.Logger | None = None):
        self.model_name = model_name
        self.logger = logger or logging.getLogger(__name__)
        self.model = genai.GenerativeModel(model_name)

    async def analyze_image_with_prompt(
        self,
        image_path: str,
        prompt: str,
        model_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """画像とプロンプトでAI分析を実行（純粋な技術実装）"""
        try:
            # 画像読み込み
            image = PIL.Image.open(image_path)

            # モデル設定の適用
            if model_options:
                # temperature, max_tokens等の設定をここで適用
                pass

            # Gemini APIコール（プロンプトはそのまま使用）
            response = await self.model.generate_content_async([prompt, image])

            # 生レスポンスを返す（最小限の技術的処理のみ）
            result = {
                "raw_response": response.text,
                "model_name": self.model_name,
                "ssuccess": True,
                "timestamp": self._get_current_timestamp(),
            }

            self.logger.info("Gemini API call completed")
            return result

        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
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
