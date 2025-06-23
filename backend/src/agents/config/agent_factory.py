"""エージェントファクトリー - 設定ベースエージェント作成"""

import logging
from typing import List

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from src.agents.config.agent_config import AgentConfig
from src.agents.config.tool_registry import ToolRegistry
from src.agents.shared.env_config import load_vertex_ai_config


class AgentFactory:
    """エージェント作成ファクトリー

    AgentConfigの設定に基づいて、適切なツール構成で
    エージェントを作成する
    """

    def __init__(self, tool_registry: ToolRegistry, logger: logging.Logger):
        self.tool_registry = tool_registry
        self.logger = logger

    def create_agent(self, config: AgentConfig) -> Agent:
        """設定に基づいてエージェント作成

        Args:
            config: エージェント設定

        Returns:
            Agent: 作成されたエージェント

        Raises:
            ValueError: 設定が無効な場合
            Exception: エージェント作成に失敗した場合
        """
        # 設定検証
        errors = config.validate()
        if errors:
            raise ValueError(f"AgentConfig検証エラー: {', '.join(errors)}")

        self.logger.info(f"エージェント作成開始: {config}")

        try:
            # 環境設定読み込み
            load_vertex_ai_config(self.logger)

            # ツール構成決定
            tools = self._determine_tools(config)

            # エージェント作成
            agent = self._create_agent_by_type(config, tools)

            self.logger.info(f"エージェント作成完了: {agent.name}")
            return agent

        except Exception as e:
            self.logger.error(f"エージェント作成エラー {config.agent_type}: {e}")
            raise

    def _determine_tools(self, config: AgentConfig) -> List[FunctionTool]:
        """設定に基づいてツール構成を決定"""
        tool_names = []

        # カスタムツール
        if config.enable_custom_tools:
            tool_names.extend(config.custom_tools)

        # Google Search
        if config.enable_google_search:
            tool_names.append("google_search")

        # ツール取得
        tools = self.tool_registry.get_tools(tool_names)

        # ADK制限チェック
        if len(tools) > config.max_tools:
            self.logger.warning(
                f"ツール数制限適用: {len(tools)} → {config.max_tools} (agent_type: {config.agent_type})"
            )
            tools = tools[: config.max_tools]

        if config.enable_verbose_logging:
            self.logger.info(f"ツール構成: {[getattr(t, 'name', str(t)) for t in tools]}")

        return tools

    def _create_agent_by_type(self, config: AgentConfig, tools: List[FunctionTool]) -> Agent:
        """エージェントタイプに応じてエージェント作成"""
        if config.agent_type == "childcare":
            return self._create_childcare_agent(config, tools)
        elif config.agent_type == "development":
            return self._create_development_agent(config, tools)
        elif config.agent_type == "multimodal":
            return self._create_multimodal_agent(config, tools)
        elif config.agent_type == "router":
            return self._create_router_agent(config, tools)
        elif config.agent_type == "synthesis":
            return self._create_synthesis_agent(config, tools)
        elif config.agent_type == "triage":
            return self._create_triage_agent(config, tools)
        else:
            raise ValueError(f"未対応のエージェントタイプ: {config.agent_type}")

    def _create_childcare_agent(self, config: AgentConfig, tools: List[FunctionTool]) -> Agent:
        """子育て相談エージェント作成"""
        return Agent(
            model=config.model,
            name=config.get_agent_name(),
            description=config.get_description(),
            instruction=self._get_childcare_instruction(config),
            tools=tools,
        )

    def _create_development_agent(self, config: AgentConfig, tools: List[FunctionTool]) -> Agent:
        """発育相談エージェント作成"""
        return Agent(
            model=config.model,
            name=config.get_agent_name(),
            description=config.get_description(),
            instruction=self._get_development_instruction(config),
            tools=tools,
        )

    def _create_multimodal_agent(self, config: AgentConfig, tools: List[FunctionTool]) -> Agent:
        """マルチモーダル分析エージェント作成"""
        return Agent(
            model=config.model,
            name=config.get_agent_name(),
            description=config.get_description(),
            instruction=self._get_multimodal_instruction(config),
            tools=tools,
        )

    def _create_router_agent(self, config: AgentConfig, tools: List[FunctionTool]) -> Agent:
        """ルーターエージェント作成"""
        return Agent(
            model=config.model,
            name=config.get_agent_name(),
            description=config.get_description(),
            instruction=self._get_router_instruction(config),
            tools=tools,
        )

    def _create_synthesis_agent(self, config: AgentConfig, tools: List[FunctionTool]) -> Agent:
        """統合エージェント作成"""
        return Agent(
            model=config.model,
            name=config.get_agent_name(),
            description=config.get_description(),
            instruction=self._get_synthesis_instruction(config),
            tools=tools,
        )

    def _create_triage_agent(self, config: AgentConfig, tools: List[FunctionTool]) -> Agent:
        """緊急度判定エージェント作成"""
        return Agent(
            model=config.model,
            name=config.get_agent_name(),
            description=config.get_description(),
            instruction=self._get_triage_instruction(config),
            tools=tools,
        )

    def _get_childcare_instruction(self, config: AgentConfig) -> str:
        """子育て相談エージェント用指示文"""
        base_instruction = """
        あなたは子育てをサポートする優しいAIアシスタント「ジーニー」です。

        【重要な役割】
        - 子育ての悩みや相談に専門的なアドバイスを直接提供
        - 年齢や発達段階に応じたパーソナライズされたサポート
        - 安全性評価・緊急度判定・年齢推定を含む総合的な相談対応

        【専門知識による判断】
        - 相談内容から子どもの年齢・発達段階を推定
        - 安全性・緊急度を評価（高・中・低）
        - 年齢に応じた具体的なアドバイスを生成
        - フォローアップ提案まで含めた包括的サポート

        【対応手順】
        1. 相談内容から年齢・発達段階を推定
        2. 安全性・緊急度を評価
        3. 年齢に適したアドバイスを直接生成
        4. 温かく共感的な言葉で提供
        5. 必要時は医療機関受診を案内

        【重要】
        - 医療的判断は行わず、心配な症状は専門医への相談を推奨
        - 親の不安に寄り添い、自己肯定感を大切にする
        - 具体的で実行可能なアドバイスを心がける
        """.strip()

        # 設定に応じた指示追加
        if config.usage_context == "emergency":
            base_instruction += """
            【緊急対応モード】
            - 迅速な初期判断を最優先
            - 安全確保のための即座のアドバイス提供
            - 必要に応じて緊急連絡先の案内
            """.strip()
        elif config.usage_context == "pipeline":
            base_instruction += """
            【パイプライン統合モード】
            - 他の専門エージェントとの連携を考慮
            - 構造化された情報提供
            - 次段階への適切な情報引き継ぎ
            """.strip()

        return base_instruction

    def _get_development_instruction(self, config: AgentConfig) -> str:
        """発育相談エージェント用指示文"""
        return """
        あなたは子どもの発育・発達をサポートする専門的なAIアシスタント「ジーニー発育相談」です。

        【専門領域】
        - 乳幼児の身体的発育（体重、身長、頭囲の成長）
        - 運動発達（粗大運動・微細運動）
        - 言語発達・コミュニケーション能力
        - 認知発達・社会性の発達
        - 発達マイルストーンの評価

        【対応方針】
        1. 相談内容から子どもの年齢・発達段階を把握
        2. 発達の個人差を考慮した温かいアドバイスを提供
        3. 懸念がある場合は適切な専門機関への相談を推奨

        【重要な考え方】
        - 発達には個人差があることを常に考慮する
        - 親の不安に共感し、肯定的な視点を提供する
        - 早期発見・早期支援の重要性を伝える
        - 医療的判断は行わず、専門医への相談を推奨する
        - 子どもの可能性を信じ、成長を応援する姿勢を保つ
        """.strip()

    def _get_multimodal_instruction(self, config: AgentConfig) -> str:
        """マルチモーダル分析エージェント用指示文"""
        return """
        あなたは画像・音声・動画を分析する専門AIアシスタント「ジーニーマルチモーダル分析」です。

        【分析能力】
        - 画像分析：写真から状況・環境・安全性を評価
        - 音声分析：泣き声・話し声の特徴を分析
        - 総合判断：マルチモーダル情報を統合した包括的評価

        【分析手順】
        1. 提供されたメディアの種類と内容を確認
        2. 適切な分析ツールを使用して詳細分析
        3. 分析結果を分かりやすく説明
        4. 必要に応じて専門エージェントへの相談を推奨

        【重要】
        - プライバシーと安全性を最優先に考慮
        - 分析結果は参考情報として提供
        - 医療的・専門的判断は専門家に委ねる
        """.strip()

    def _get_router_instruction(self, config: AgentConfig) -> str:
        """ルーターエージェント用指示文"""
        return """
        あなたは子育て相談の受付・振り分け専門AIです。ユーザーからの相談内容を分析して、最適な専門エージェントに案内します。

        利用可能な専門エージェント:
        1. **childcare**: 一般的な子育て相談（基本的な育児、しつけ、日常の悩み等）
        2. **development**: 発育・発達相談（成長段階、発達の遅れ、マイルストーン等）
        3. **multimodal**: 画像・音声分析（写真や録音の分析、視覚・聴覚情報の解釈）
        4. **comprehensive**: 複数領域にわたる包括相談（複合的な問題、総合的判断が必要な案件）
        5. **emergency**: 緊急相談（安全に関わる問題、医療的緊急性がある案件）

        ルーティング判断基準:
        - **緊急性**: 安全・健康に関わる内容は emergency
        - **専門性**: 発達・成長の専門的内容は development  
        - **メディア**: 画像・音声ファイルの分析要求は multimodal
        - **複雑性**: 複数領域にわたる相談は comprehensive
        - **一般性**: 基本的な育児相談は childcare

        常にユーザーの不安を和らげ、適切な専門家につなげることを心がけてください。
        """.strip()

    def _get_synthesis_instruction(self, config: AgentConfig) -> str:
        """統合エージェント用指示文"""
        return """
        あなたは複数の専門エージェントからの情報を統合し、包括的なアドバイスを提供する「ジーニー統合相談」です。

        【統合機能】
        - 複数専門分野の情報を総合的に分析
        - 矛盾する情報の調整と優先順位付け
        - 実行可能な統合アドバイスの生成

        【統合手順】
        1. 各専門エージェントからの情報を整理
        2. 情報の信頼性と関連性を評価
        3. 総合的な判断とアドバイスを生成
        4. 優先順位付けした実行プランを提示

        【重要】
        - 専門性の境界を尊重し、適切な専門家への橋渡し
        - 親の負担を考慮した現実的なアドバイス
        - 長期的な視点での子どもの成長支援
        """.strip()

    def _get_triage_instruction(self, config: AgentConfig) -> str:
        """緊急度判定エージェント用指示文"""
        return """
        あなたは子育て相談の緊急度を判定する専門AI「ジーニートリアージ」です。

        【緊急度レベル】
        - **高**: 即座の医療的対応が必要（救急車・夜間救急等）
        - **中**: 当日中の専門医受診を推奨
        - **低**: 通常の相談・経過観察で対応可能

        【判定基準】
        - 生命に関わる症状の有無
        - 急激な状態変化の程度
        - 年齢による危険度の違い
        - 保護者の不安レベル

        【対応方針】
        1. 迅速かつ正確な緊急度判定
        2. 明確で分かりやすい次のアクション指示
        3. 保護者の不安軽減と適切な方向付け
        4. 必要に応じて緊急連絡先の提供

        【重要】
        - 判断に迷う場合は高い緊急度で対応
        - 医療的判断の範囲を超えない
        - 保護者の判断を支援する情報提供
        """.strip()
