"""ADKルーティングコーディネーターのRoutingStrategy互換アダプター

既存のRoutingStrategyインターフェースとADK標準ルーティングの橋渡し役
GenieUs CLAUDE.md準拠:
- DIコンテナからのロガー注入
- 型アノテーション完備
- 段階的エラーハンドリング
"""

import logging

from src.agents.adk_routing_coordinator import AdkRoutingCoordinator
from src.agents.routing_strategy import RoutingStrategy


class AdkRoutingStrategyAdapter(RoutingStrategy):
    """ADKルーティングコーディネーターをRoutingStrategyインターフェースに適合させるアダプター

    既存のAgentManagerがRoutingStrategyインターフェースを期待しているため、
    ADK標準のLlmAgentベースルーティングを既存システムに統合するアダプター
    """

    def __init__(
        self,
        adk_coordinator: AdkRoutingCoordinator,
        logger: logging.Logger,
    ) -> None:
        """ADKルーティング戦略アダプター初期化

        Args:
            adk_coordinator: ADKルーティングコーディネーター
            logger: DIコンテナから注入されるロガー（必須）

        Raises:
            TypeError: 必須パラメータがNoneの場合

        """
        if adk_coordinator is None:
            raise TypeError("adk_coordinatorは必須です")
        if logger is None:
            raise TypeError("loggerはDIコンテナから注入する必要があります")

        super().__init__(logger)
        self.adk_coordinator = adk_coordinator

        self.logger.info("✅ ADKルーティング戦略アダプター初期化完了")

    def determine_agent(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
        family_info: dict | None = None,
    ) -> tuple[str, dict]:
        """エージェント決定（RoutingStrategyインターフェース実装）

        Args:
            message: ユーザーからのメッセージ
            conversation_history: 会話履歴（オプション）
            family_info: 家族情報（オプション）

        Returns:
            Tuple[str, Dict]: (エージェントID, ルーティング情報)

        Note:
            ADK標準では実際のルーティングはLlmAgentが自動で行うため、
            このメソッドは互換性のため暫定的に"adk_coordinator"を返す

        """
        try:
            self.logger.info(f"🎯 ADKルーティング実行: '{message[:50]}...'")

            # ADK標準では、実際のルーティングはLlmAgentのtransfer_to_agent()機能が自動で行う
            # このアダプターでは互換性を保つため、coordinator_agentを指示する

            routing_info = {
                "confidence": 1.0,  # ADK標準では常に高信頼度
                "reasoning": "ADK標準LlmAgentによる自動ルーティング",
                "strategy": "adk_standard",
                "routing_strategy": self.adk_coordinator.get_routing_strategy_name(),
                "available_specialists": self.adk_coordinator.get_available_specialists(),
                "coordinator_agent": True,
                "auto_transfer_enabled": True,
            }

            # 🔍 **最優先**: 明示的検索フラグの検出（ADK制約回避）
            from src.agents.constants import EXPLICIT_SEARCH_FLAGS
            
            # 明示的検索フラグの検出
            explicit_search_detected = False
            matched_flag = None
            for search_flag in EXPLICIT_SEARCH_FLAGS:
                if search_flag.lower() in message.lower() or search_flag in message:
                    explicit_search_detected = True
                    matched_flag = search_flag
                    break
            
            if explicit_search_detected:
                selected_agent = "search_specialist"
                routing_info.update(
                    {
                        "reasoning": f"明示的検索要求フラグ検出: {matched_flag} → 直接search_specialistに転送",
                        "direct_routing": True,
                        "explicit_search": True,
                        "priority": "highest",
                        "matched_flag": matched_flag,
                    }
                )
                self.logger.info(f"🎯 ADK: 明示的検索フラグ検出 '{matched_flag}' → search_specialist")
            else:
                # 検索関連の質問は直接search_specialistに転送（function calling回避）
                search_keywords = ["検索", "調べ", "情報", "万博", "イベント", "おでかけ", "どう", "どこ"]
                if any(keyword in message for keyword in search_keywords):
                    selected_agent = "search_specialist"
                    routing_info.update(
                        {
                            "reasoning": "検索関連質問のため直接search_specialistに転送（ADK制約回避）",
                            "direct_routing": True,
                        }
                    )
                else:
                    # その他はADK coordinatorエージェントを使用
                    selected_agent = "adk_coordinator"

            self.logger.info(f"✅ ADKルーティング完了: {selected_agent}")

            return selected_agent, routing_info

        except Exception as e:
            self.logger.error(f"❌ ADKルーティングエラー: {e}")

            # エラー時はフォールバック
            return "coordinator", {
                "confidence": 0.5,
                "reasoning": f"ADKルーティングエラー、フォールバック: {e!s}",
                "strategy": "adk_fallback",
                "error": str(e),
            }

    def get_strategy_name(self) -> str:
        """戦略名を返す

        Returns:
            str: ADK標準ルーティング戦略名

        """
        return self.adk_coordinator.get_routing_strategy_name()

    def get_coordinator_agent(self):
        """ADKコーディネーターエージェントを取得

        Returns:
            LlmAgent: ADK標準コーディネーターエージェント

        Note:
            既存のAgentManagerがこのエージェントを直接使用する可能性があるため

        """
        return self.adk_coordinator.get_coordinator_agent()

    def get_routing_statistics(self) -> dict[str, any]:
        """ルーティング統計情報を取得

        Returns:
            Dict[str, any]: 統計情報（アダプター情報も含む）

        """
        stats = self.adk_coordinator.get_routing_statistics()
        stats.update({"adapter_used": True, "compatible_with_routing_strategy": True, "fallback_supported": True})
        return stats
