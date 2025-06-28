"""ルーティング戦略インターフェース

GenieUsのDIパターンに準拠した戦略パターン実装
すべてのロガーはDIコンテナから注入される
"""

import logging
from abc import ABC, abstractmethod


class RoutingStrategy(ABC):
    """ルーティング戦略の抽象基底クラス"""

    def __init__(self, logger: logging.Logger):
        """Args:
        logger: DIコンテナから注入されるロガー

        """
        self.logger = logger

    @abstractmethod
    def determine_agent(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
        family_info: dict | None = None,
        # 画像・マルチモーダル対応パラメータ追加
        has_image: bool = False,
        message_type: str = "text",
    ) -> tuple[str, dict]:
        """エージェントを決定する

        Args:
            message: ユーザーからのメッセージ
            conversation_history: 会話履歴（オプション）
            family_info: 家族情報（オプション）
            has_image: 画像添付フラグ（オプション）
            message_type: メッセージタイプ（オプション）

        Returns:
            Tuple[str, Dict]: (エージェントID, ルーティング情報)
                ルーティング情報には以下を含む:
                - confidence: 確信度（0.0-1.0）
                - reasoning: 決定理由
                - matched_keywords: マッチしたキーワード（該当する場合）

        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """戦略名を返す"""
        pass
