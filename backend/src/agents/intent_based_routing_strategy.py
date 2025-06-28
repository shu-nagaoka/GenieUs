"""IntentBasedRoutingStrategy - 意図ベースルーティング戦略

ユーザーの明確な意図（検索、画像分析等）を最優先し、
UI状態に基づく強制ルーティングとキーワードマッチングを実装
"""

import logging

from src.agents.constants import AGENT_KEYWORDS, EXPLICIT_SEARCH_FLAGS
from src.agents.routing_strategy import RoutingStrategy


class IntentBasedRoutingStrategy(RoutingStrategy):
    """意図ベースルーティング戦略
    
    ユーザーの明確な意図（検索、画像分析等）を最優先し、
    UI状態に基づく強制ルーティングとキーワードマッチングを実装
    """

    def __init__(self, logger: logging.Logger):
        """初期化
        
        Args:
            logger: DIコンテナから注入されるロガー
        """
        self.logger = logger

    def determine_agent(
        self,
        message: str,
        conversation_history: list | None = None,
        family_info: dict | None = None,
        # 画像・マルチモーダル対応パラメータ追加
        has_image: bool = False,
        message_type: str = "text",
    ) -> tuple[str, dict]:
        """エージェント決定（キーワードマッチング）
        
        Args:
            message: ユーザーメッセージ
            conversation_history: 会話履歴（未使用）
            family_info: 家族情報（未使用）
            has_image: 画像添付フラグ
            message_type: メッセージタイプ
            
        Returns:
            Tuple[agent_id, routing_info]
        """
        message_lower = message.lower()
        
        # 🖼️ **最優先**: 強制画像分析ルーティング指示検出
        if "FORCE_IMAGE_ANALYSIS_ROUTING" in message:
            self.logger.info(f"🎯 強制画像分析ルーティング指示検出 → image_specialist")
            return "image_specialist", {
                "confidence": 1.0,
                "reasoning": "フロントエンドからの強制画像分析ルーティング指示",
                "matched_keywords": ["FORCE_IMAGE_ANALYSIS_ROUTING"],
                "priority": "highest",
                "force_routing": True
            }
        
        # 🖼️ **第2優先**: 画像添付検出
        if has_image or message_type == "image":
            self.logger.info(f"🎯 画像添付検出: has_image={has_image}, message_type={message_type} → image_specialist")
            return "image_specialist", {
                "confidence": 1.0,
                "reasoning": "画像添付検出による優先ルーティング",
                "matched_keywords": ["image_attachment"],
                "priority": "highest",
                "image_priority": True
            }
        
        # 🔍 **第3優先**: 強制検索ルーティング指示検出
        if "FORCE_SEARCH_AGENT_ROUTING" in message:
            self.logger.info(f"🎯 強制検索ルーティング指示検出 → search_specialist")
            return "search_specialist", {
                "confidence": 1.0,
                "reasoning": "フロントエンドからの強制検索ルーティング指示",
                "matched_keywords": ["FORCE_SEARCH_AGENT_ROUTING"],
                "priority": "highest",
                "force_routing": True
            }
        
        # 🔍 **第4優先**: 明示的検索フラグの検出
        for search_flag in EXPLICIT_SEARCH_FLAGS:
            if search_flag.lower() in message_lower or search_flag in message:
                self.logger.info(f"🎯 明示的検索フラグ検出: '{search_flag}' → search_specialist")
                return "search_specialist", {
                    "confidence": 1.0,
                    "reasoning": f"明示的検索要求フラグ検出: {search_flag}",
                    "matched_keywords": [search_flag],
                    "priority": "highest",
                    "explicit_search": True
                }
        
        # 各エージェントのキーワードマッチング
        for agent_id, keywords in AGENT_KEYWORDS.items():
            match_count = sum(1 for keyword in keywords if keyword in message_lower)
            if match_count > 0:
                confidence = min(match_count / len(keywords), 1.0)
                routing_info = {
                    "confidence": confidence,
                    "reasoning": f"キーワードマッチ: {match_count}個",
                    "matched_keywords": [kw for kw in keywords if kw in message_lower]
                }
                return agent_id, routing_info
        
        # デフォルトはコーディネーター
        return "coordinator", {
            "confidence": 0.5,
            "reasoning": "デフォルトルーティング",
            "matched_keywords": []
        }

    def get_strategy_name(self) -> str:
        """戦略名取得"""
        return "IntentBasedRouting"