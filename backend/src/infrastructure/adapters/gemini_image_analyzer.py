"""Gemini画像分析アダプター

ADK非依存の実装クラス
"""

import base64
import io
import logging
from typing import Any

import google.generativeai as genai
import PIL.Image

from src.application.interface.protocols.image_analyzer import ImageAnalyzerProtocol


class GeminiImageAnalyzer(ImageAnalyzerProtocol):
    """Geminiを使用した画像分析の具体的実装"""

    def __init__(self, logger: logging.Logger, model_name: str = "gemini-2.5-flash-preview-05-20") -> None:
        self.model_name = model_name
        self.logger = logger  # DIコンテナから必須注入
        self.model = genai.GenerativeModel(model_name)

    async def analyze_image_with_prompt(
        self,
        image_path: str,
        prompt: str,
        model_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """画像とプロンプトでAI分析を実行（純粋な技術実装）"""
        try:
            # 詳細ログでデバッグ
            self.logger.info(f"画像パス詳細: 長さ={len(image_path)}, 先頭50文字={image_path[:50]}...")
            # 画像読み込み（Base64データ対応）
            if image_path.startswith("data:image/"):
                # Base64データの場合
                self.logger.info("Base64データとして処理開始")
                header, data = image_path.split(",", 1)
                self.logger.info(f"Base64ヘッダー: {header}")
                self.logger.info(f"Base64データ長: {len(data)}")
                image_data = base64.b64decode(data)
                image = PIL.Image.open(io.BytesIO(image_data))
                self.logger.info(f"Base64画像データから画像を読み込み成功: サイズ={image.size}")
            else:
                # ファイルパスの場合
                self.logger.info(f"ファイルパスとして処理: {image_path}")
                image = PIL.Image.open(image_path)
                self.logger.info(f"ファイルパス {image_path} から画像を読み込み成功")

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
                "success": True,
                "timestamp": self._get_current_timestamp(),
            }

            self.logger.info("Gemini API call completed")
            return result

        except Exception as e:  # noqa: BLE001
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
