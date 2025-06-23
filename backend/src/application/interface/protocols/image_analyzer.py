"""画像分析サービスのプロトコル定義"""

from typing import Any, Protocol


class ImageAnalyzerProtocol(Protocol):
    """画像分析サービスのインターフェース"""

    async def analyze_image_with_prompt(
        self,
        image_path: str,
        prompt: str,
        model_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """画像とプロンプトでAI分析を実行（純粋な技術実装）

        Args:
            image_path: 画像ファイルのパス
            prompt: 分析用プロンプト（UseCase層から提供）
            model_options: モデル設定（temperature, max_tokens等）

        Returns:
            AIモデルの生レスポンス

        """
        ...
