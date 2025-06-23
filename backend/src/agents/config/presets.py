"""エージェント設定プリセット - よく使用される構成パターン"""

from src.agents.config.agent_config import AgentConfig


class AgentConfigPresets:
    """よく使用される設定のプリセット集

    典型的な利用パターンを事前定義し、
    Agent Managerから簡単に使用できるようにする
    """

    # ===== 子育て相談エージェント =====

    @staticmethod
    def minimal_childcare() -> AgentConfig:
        """最小構成の子育てエージェント

        - ツールなし
        - Google Search なし
        - 軽量・高速動作
        """
        return AgentConfig(
            agent_type="childcare",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=False,
            custom_tools=[],
            name_suffix="Minimal",
        )

    @staticmethod
    def standard_childcare() -> AgentConfig:
        """標準子育てエージェント

        - 専用ツールあり
        - Google Search なし（レスポンス速度重視）
        - バランス型
        """
        return AgentConfig(
            agent_type="childcare",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=True,
            custom_tools=["childcare_consultation"],
        )

    @staticmethod
    def full_childcare() -> AgentConfig:
        """フル機能子育てエージェント

        - 専用ツールあり
        - Google Search あり
        - 最新情報対応
        """
        return AgentConfig(
            agent_type="childcare",
            usage_context="interactive",
            enable_google_search=True,
            enable_custom_tools=True,
            custom_tools=["childcare_consultation"],
            name_suffix="Full",
        )

    @staticmethod
    def emergency_childcare() -> AgentConfig:
        """緊急対応特化子育てエージェント

        - 迅速対応重視
        - 必要最小限のツール
        - 緊急判断特化
        """
        return AgentConfig(
            agent_type="childcare",
            usage_context="emergency",
            enable_google_search=False,
            enable_custom_tools=True,
            custom_tools=["childcare_consultation"],
            name_suffix="Emergency",
        )

    # ===== 発育相談エージェント =====

    @staticmethod
    def minimal_development() -> AgentConfig:
        """最小構成の発育エージェント"""
        return AgentConfig(
            agent_type="development",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=False,
            custom_tools=[],
            name_suffix="Minimal",
        )

    @staticmethod
    def standard_development() -> AgentConfig:
        """標準発育エージェント"""
        return AgentConfig(
            agent_type="development",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=True,
            custom_tools=["development_assessment"],
        )

    @staticmethod
    def full_development() -> AgentConfig:
        """フル機能発育エージェント"""
        return AgentConfig(
            agent_type="development",
            usage_context="interactive",
            enable_google_search=True,
            enable_custom_tools=True,
            custom_tools=["development_assessment"],
            name_suffix="Full",
        )

    @staticmethod
    def pipeline_development() -> AgentConfig:
        """パイプライン用発育エージェント

        - 他エージェントとの連携特化
        - 構造化情報提供
        """
        return AgentConfig(
            agent_type="development",
            usage_context="pipeline",
            enable_google_search=True,
            enable_custom_tools=True,
            custom_tools=["development_assessment"],
            name_suffix="Pipeline",
        )

    # ===== マルチモーダルエージェント =====

    @staticmethod
    def standard_multimodal() -> AgentConfig:
        """標準マルチモーダルエージェント"""
        return AgentConfig(
            agent_type="multimodal",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=True,
            custom_tools=["image_analysis", "voice_analysis"],
        )

    @staticmethod
    def image_only_multimodal() -> AgentConfig:
        """画像分析特化エージェント"""
        return AgentConfig(
            agent_type="multimodal",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=True,
            custom_tools=["image_analysis"],
            name_suffix="ImageOnly",
        )

    @staticmethod
    def voice_only_multimodal() -> AgentConfig:
        """音声分析特化エージェント"""
        return AgentConfig(
            agent_type="multimodal",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=True,
            custom_tools=["voice_analysis"],
            name_suffix="VoiceOnly",
        )

    # ===== ルーターエージェント =====

    @staticmethod
    def standard_router() -> AgentConfig:
        """標準ルーターエージェント

        Note: ルーターエージェントは特別なルーティングツールを使用
        """
        return AgentConfig(
            agent_type="router",
            usage_context="interactive",
            enable_google_search=False,
            enable_custom_tools=False,  # ルーティングツールは動的に追加
            custom_tools=[],
        )

    # ===== 統合・特殊エージェント =====

    @staticmethod
    def standard_synthesis() -> AgentConfig:
        """標準統合エージェント"""
        return AgentConfig(
            agent_type="synthesis",
            usage_context="pipeline",
            enable_google_search=True,
            enable_custom_tools=True,
            custom_tools=["childcare_consultation", "development_assessment"],
        )

    @staticmethod
    def standard_triage() -> AgentConfig:
        """標準緊急度判定エージェント"""
        return AgentConfig(
            agent_type="triage",
            usage_context="emergency",
            enable_google_search=False,
            enable_custom_tools=True,
            custom_tools=["childcare_consultation"],
            max_tools=2,  # 緊急対応のため制限
        )

    # ===== テスト・開発用 =====

    @staticmethod
    def test_agent(agent_type: str = "childcare") -> AgentConfig:
        """テスト用エージェント

        - 全機能無効
        - 高速動作
        - デバッグログ有効
        """
        return AgentConfig(
            agent_type=agent_type,
            usage_context="test",
            enable_google_search=False,
            enable_custom_tools=False,
            custom_tools=[],
            name_suffix="Test",
            enable_verbose_logging=True,
        )

    @staticmethod
    def debug_agent(agent_type: str = "childcare") -> AgentConfig:
        """デバッグ用エージェント

        - 全機能有効
        - 詳細ログ有効
        - 開発・デバッグ用途
        """
        return AgentConfig(
            agent_type=agent_type,
            usage_context="interactive",
            enable_google_search=True,
            enable_custom_tools=True,
            custom_tools=["childcare_consultation", "development_assessment", "image_analysis"],
            name_suffix="Debug",
            enable_verbose_logging=True,
            max_tools=10,  # デバッグのため制限緩和
        )

    # ===== ユーティリティメソッド =====

    @staticmethod
    def get_all_presets() -> dict[str, AgentConfig]:
        """全プリセットを辞書形式で取得"""
        return {
            # 子育て相談
            "minimal_childcare": AgentConfigPresets.minimal_childcare(),
            "standard_childcare": AgentConfigPresets.standard_childcare(),
            "full_childcare": AgentConfigPresets.full_childcare(),
            "emergency_childcare": AgentConfigPresets.emergency_childcare(),
            # 発育相談
            "minimal_development": AgentConfigPresets.minimal_development(),
            "standard_development": AgentConfigPresets.standard_development(),
            "full_development": AgentConfigPresets.full_development(),
            "pipeline_development": AgentConfigPresets.pipeline_development(),
            # マルチモーダル
            "standard_multimodal": AgentConfigPresets.standard_multimodal(),
            "image_only_multimodal": AgentConfigPresets.image_only_multimodal(),
            "voice_only_multimodal": AgentConfigPresets.voice_only_multimodal(),
            # その他
            "standard_router": AgentConfigPresets.standard_router(),
            "standard_synthesis": AgentConfigPresets.standard_synthesis(),
            "standard_triage": AgentConfigPresets.standard_triage(),
        }

    @staticmethod
    def get_preset_names() -> list[str]:
        """利用可能なプリセット名一覧を取得"""
        return list(AgentConfigPresets.get_all_presets().keys())
