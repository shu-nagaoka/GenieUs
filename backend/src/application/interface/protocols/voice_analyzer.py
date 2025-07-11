"""音声分析サービスのプロトコル定義"""

from typing import Any, Protocol


class VoiceAnalyzerProtocol(Protocol):
    """音声分析サービスのインターフェース"""

    async def analyze_text_with_prompt(
        self,
        text: str,
        prompt: str,
        model_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """テキストとプロンプトでAI分析を実行（純粋な技術実装）

        Args:
            text: 分析対象のテキスト
            prompt: 分析用プロンプト（UseCase層から提供）
            model_options: モデル設定（temperature, max_tokens等）

        Returns:
            AIモデルの生レスポンス

        """
        ...
