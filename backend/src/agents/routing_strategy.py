"""ルーティング戦略インターフェース

GenieUsのDIパターンに準拠した戦略パターン実装
すべてのロガーはDIコンテナから注入される
"""

import logging
from abc import ABC, abstractmethod

from src.agents.constants import PARALLEL_ANALYSIS_KEYWORDS, SEQUENTIAL_ANALYSIS_KEYWORDS


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
    ) -> tuple[str, dict]:
        """エージェントを決定する
        
        Args:
            message: ユーザーからのメッセージ
            conversation_history: 会話履歴（オプション）
            family_info: 家族情報（オプション）
            
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


class KeywordRoutingStrategy(RoutingStrategy):
    """既存のキーワードベースルーティング戦略
    
    現在のAgentManagerの_determine_agent_typeロジックを移植
    """

    def __init__(
        self,
        logger: logging.Logger,
        agent_keywords: dict[str, list[str]],
        force_routing_keywords: dict[str, list[str]],
        agent_priority: dict[str, float],
    ):
        """Args:
        logger: DIコンテナから注入されるロガー
        agent_keywords: エージェントごとのキーワードリスト
        force_routing_keywords: 強制ルーティング用キーワード
        agent_priority: エージェントの優先度

        """
        super().__init__(logger)
        self.agent_keywords = agent_keywords
        self.force_routing_keywords = force_routing_keywords
        self.agent_priority = agent_priority

    def determine_agent(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
        family_info: dict | None = None,
    ) -> tuple[str, dict]:
        """キーワードマッチングによるエージェント決定"""
        message_lower = message.lower()

        # ステップ1: 強制ルーティングキーワードチェック
        force_routed_agent = self._check_force_routing(message_lower)
        if force_routed_agent:
            self.logger.info(f"🚨 強制ルーティング: {force_routed_agent}")
            return force_routed_agent, {
                "confidence": 1.0,
                "reasoning": "緊急キーワードによる強制ルーティング",
                "strategy": "keyword_force",
            }

        # ステップ2: 並列・順次分析キーワードチェック
        if self._is_parallel_analysis_requested(message_lower):
            return "parallel", {
                "confidence": 0.9,
                "reasoning": "並列分析キーワードを検出",
                "strategy": "keyword_parallel",
            }

        if self._is_sequential_analysis_requested(message_lower):
            return "sequential", {
                "confidence": 0.9,
                "reasoning": "順次分析キーワードを検出",
                "strategy": "keyword_sequential",
            }

        # ステップ3: 専門エージェント決定論的ルーティング
        specialist_agent, routing_info = self._determine_specialist_agent(message_lower)
        if specialist_agent and specialist_agent != "coordinator":
            self.logger.info(f"🎯 専門エージェント決定: {specialist_agent}")
            routing_info["strategy"] = "keyword_specialist"
            return specialist_agent, routing_info

        # ステップ4: デフォルト（コーディネーター）
        self.logger.info("📋 デフォルトルーティング: coordinator")
        return "coordinator", {
            "confidence": 0.3,
            "reasoning": "明確なキーワードなし、コーディネーターへ",
            "strategy": "keyword_default",
        }

    def _check_force_routing(self, message_lower: str) -> str | None:
        """強制ルーティングキーワードチェック"""
        for agent_id, force_keywords in self.force_routing_keywords.items():
            matched_keywords = [kw for kw in force_keywords if kw in message_lower]
            if matched_keywords:
                self.logger.info(
                    f"🚨 強制ルーティング検出: {agent_id} (キーワード: {matched_keywords[:3]})",
                )
                return agent_id
        return None

    def _is_parallel_analysis_requested(self, message_lower: str) -> bool:
        """並列分析要求の判定"""
        return any(keyword in message_lower for keyword in PARALLEL_ANALYSIS_KEYWORDS)

    def _is_sequential_analysis_requested(self, message_lower: str) -> bool:
        """順次分析要求の判定"""
        return any(keyword in message_lower for keyword in SEQUENTIAL_ANALYSIS_KEYWORDS)

    def _determine_specialist_agent(self, message_lower: str) -> tuple[str | None, dict]:
        """専門エージェント決定"""
        agent_scores = {}

        for agent_id, keywords in self.agent_keywords.items():
            if agent_id in self.agent_priority:
                matched_keywords = [kw for kw in keywords if kw in message_lower]
                if matched_keywords:
                    # スコア計算
                    keyword_weight = sum(len(kw) for kw in matched_keywords)
                    score = len(matched_keywords) * self.agent_priority[agent_id] * (1 + keyword_weight * 0.1)
                    agent_scores[agent_id] = {
                        "score": score,
                        "matched_keywords": matched_keywords[:3],
                        "match_count": len(matched_keywords),
                    }

        if not agent_scores:
            return None, {}

        # 最高スコアのエージェントを選択
        best_agent = max(agent_scores.items(), key=lambda x: x[1]["score"])
        agent_id, score_info = best_agent

        # 確信度の計算（スコアを0-1に正規化）
        max_possible_score = 50.0  # 経験的な最大スコア
        confidence = min(score_info["score"] / max_possible_score, 1.0)

        self.logger.info(
            f"🎯 専門エージェント選択: {agent_id} "
            f"(スコア: {score_info['score']:.1f}, マッチ: {score_info['match_count']}件)",
        )

        return agent_id, {
            "confidence": confidence,
            "reasoning": f"キーワード {score_info['matched_keywords']} にマッチ",
            "matched_keywords": score_info["matched_keywords"],
            "score": score_info["score"],
        }

    def get_strategy_name(self) -> str:
        """戦略名を返す"""
        return "KeywordRouting"
