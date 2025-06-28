"""Gemini画像分析アダプター

ADK非依存の実装クラス - Vertex AI SDK使用
"""

import base64
import io
import logging
import os
from typing import Any

import PIL.Image
import vertexai
from vertexai.generative_models import GenerativeModel, Part

from src.application.interface.protocols.image_analyzer import ImageAnalyzerProtocol


class GeminiImageAnalyzer(ImageAnalyzerProtocol):
    """Vertex AI Geminiを使用した画像分析の具体的実装"""

    def __init__(self, logger: logging.Logger, model_name: str = "gemini-2.5-flash") -> None:
        self.model_name = model_name
        self.logger = logger  # DIコンテナから必須注入

        # Vertex AI初期化
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "blog-sample-381923")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        self.logger.info(f"Vertex AI初期化: project={project_id}, location={location}")
        vertexai.init(project=project_id, location=location)

        self.model = GenerativeModel(model_name)
        self.logger.info(f"Vertex AI Gemini初期化完了: model={model_name}")

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

            # Vertex AI Gemini APIコール（プロンプトはそのまま使用）
            # 画像をVertex AI Part形式に変換
            image_bytes = io.BytesIO()
            image.save(image_bytes, format=image.format or "PNG")
            image_bytes = image_bytes.getvalue()

            # MIMEタイプを決定
            image_format = (image.format or "PNG").lower()
            if image_format == "jpeg":
                mime_type = "image/jpeg"
            elif image_format == "png":
                mime_type = "image/png"
            elif image_format == "webp":
                mime_type = "image/webp"
            else:
                mime_type = "image/png"  # デフォルト

            image_part = Part.from_data(mime_type=mime_type, data=image_bytes)

            # 非同期でコンテンツ生成
            response = await self.model.generate_content_async([prompt, image_part])

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
