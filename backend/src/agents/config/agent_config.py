"""エージェント設定クラス - 設定ベース設計の基盤"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentConfig:
    """エージェント構成設定

    エージェントの動作モード、使用ツール、パフォーマンス設定を一元管理
    """

    # 基本設定
    agent_type: str  # "childcare", "development", "multimodal", "router", etc.
    usage_context: str  # "interactive", "pipeline", "emergency", "test"

    # ツール設定
    enable_google_search: bool = True
    enable_custom_tools: bool = True
    custom_tools: List[str] = field(default_factory=list)  # ["childcare_consultation", "development_assessment"]

    # パフォーマンス設定
    model: str = "gemini-2.5-flash-preview-05-20"
    max_tools: int = 5  # ADK制限対応

    # 詳細設定
    name_suffix: str = ""  # エージェント名のサフィックス
    enable_verbose_logging: bool = False

    def get_agent_name(self) -> str:
        """エージェント名を生成"""
        base_names = {
            "childcare": "GenieChildcareConsultant",
            "development": "GenieDevelopmentConsultant",
            "multimodal": "GenieMultimodalAnalyst",
            "router": "GenieRouter",
            "synthesis": "GenieSynthesis",
            "triage": "GenieTriage",
        }

        base_name = base_names.get(self.agent_type, f"Genie{self.agent_type.title()}")

        if self.name_suffix:
            return f"{base_name}_{self.name_suffix}"
        return base_name

    def get_description(self) -> str:
        """エージェント説明を生成"""
        descriptions = {
            "childcare": "子育て相談専門エージェント",
            "development": "発育・発達評価専門エージェント",
            "multimodal": "マルチモーダル分析エージェント",
            "router": "クエリルーティングエージェント",
            "synthesis": "情報統合エージェント",
            "triage": "緊急度判定エージェント",
        }

        base_desc = descriptions.get(self.agent_type, f"{self.agent_type}エージェント")

        # 設定に基づく説明の追加
        features = []
        if self.enable_google_search:
            features.append("Google検索対応")
        if self.enable_custom_tools and self.custom_tools:
            features.append(f"専用ツール{len(self.custom_tools)}個")
        if self.usage_context == "pipeline":
            features.append("パイプライン統合")
        elif self.usage_context == "emergency":
            features.append("緊急対応特化")

        if features:
            return f"{base_desc}（{' | '.join(features)}）"
        return base_desc

    def validate(self) -> List[str]:
        """設定値の検証"""
        errors = []

        if not self.agent_type:
            errors.append("agent_typeは必須です")

        if not self.usage_context:
            errors.append("usage_contextは必須です")

        if self.max_tools < 0:
            errors.append("max_toolsは0以上である必要があります")

        if self.enable_custom_tools and len(self.custom_tools) > self.max_tools:
            errors.append(f"custom_toolsの数({len(self.custom_tools)})がmax_tools({self.max_tools})を超えています")

        return errors

    def __str__(self) -> str:
        """設定の文字列表現"""
        return (
            f"AgentConfig("
            f"type={self.agent_type}, "
            f"context={self.usage_context}, "
            f"search={self.enable_google_search}, "
            f"tools={len(self.custom_tools) if self.enable_custom_tools else 0}"
            f")"
        )
