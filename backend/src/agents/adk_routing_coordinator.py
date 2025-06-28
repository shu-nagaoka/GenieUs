"""ADK標準パターンによるルーティングコーディネーター

Google ADKのベストプラクティスに従った、LlmAgent + sub_agents + transfer_to_agent()による
シンプルで効果的なルーティングシステム

GenieUs CLAUDE.md準拠:
- ADKファースト設計
- DIコンテナからのロガー注入
- 型アノテーション完備
- 段階的エラーハンドリング
"""

import logging

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


class AdkRoutingCoordinator:
    """ADK標準パターンによるルーティングコーディネーター

    特徴:
    - LlmAgentの transfer_to_agent() 機能を活用
    - sub_agents による自動ルーティング
    - シンプルな instruction ベース判定
    - ADKフレームワーク完全準拠
    """

    def __init__(
        self,
        specialist_agents: dict[str, LlmAgent],
        logger: logging.Logger,
        tools: dict[str, FunctionTool] | None = None,
    ) -> None:
        """ADKルーティングコーディネーター初期化

        Args:
            specialist_agents: 専門エージェント群
            logger: DIコンテナから注入されるロガー（必須）
            tools: 共通ツール群（オプション）

        Raises:
            ValueError: specialist_agentsが空の場合
            TypeError: loggerがNoneの場合

        """
        if not specialist_agents:
            raise ValueError("specialist_agentsは空にできません")
        if logger is None:
            raise TypeError("loggerはDIコンテナから注入する必要があります")

        self.logger = logger
        self.specialist_agents = specialist_agents
        self.tools = tools or {}

        try:
            # ADK標準パターンでコーディネーターエージェント作成
            self.coordinator_agent = self._create_coordinator_agent()

            self.logger.info(f"✅ ADKルーティングコーディネーター初期化完了: {len(specialist_agents)}専門エージェント")
        except Exception as e:
            self.logger.error(f"❌ ADKルーティングコーディネーター初期化失敗: {e}")
            raise

    def _create_coordinator_agent(self) -> LlmAgent:
        """ADK標準パターンでコーディネーターエージェント作成

        Returns:
            LlmAgent: 初期化されたコーディネーターエージェント

        Raises:
            Exception: エージェント作成に失敗した場合

        """
        try:
            # 専門エージェントリストを指示文で説明
            specialist_descriptions = self._build_specialist_descriptions()

            instruction = f"""あなたは子育て相談専門のルーティングコーディネーターです。

**重要**: あなたは相談に直接回答しません。必ず適切な専門エージェントに transfer_to_agent() で転送してください。

**必須動作**:
1. 相談内容を分析
2. 最適な専門エージェントを判定
3. transfer_to_agent('specialist_name') を実行（必須）

**🔍 最優先ルール（検索要求の検出）**:
以下のフラグが含まれる場合は、専門性に関係なく必ず SearchspecialistSpecialist に転送:
- 【最新情報を検索してください】
- 【検索してください】
- 【情報を検索】
- 【調べてください】
- 【最新情報を調べて】
- 【ネット検索】
- 【Google検索】
- "最新情報を検索"
- "ネットで検索"
- "Googleで検索"

**検索フラグ検出時の動作**:
→ 即座に transfer_to_agent('SearchspecialistSpecialist') を実行
→ 他の専門性分析は行わない

**絶対禁止**:
- 自分で相談に回答すること
- 「〜専門家が心を込めてお答えします」などのテキスト応答
- transfer_to_agent() を使わない回答

利用可能な専門エージェント:
{specialist_descriptions}

**転送例（これらの形式のみ使用）**:
- 睡眠相談 → transfer_to_agent('SleepspecialistSpecialist')
- 保育園選び → transfer_to_agent('WorklifespecialistSpecialist')  
- 食事の悩み → transfer_to_agent('NutritionspecialistSpecialist')
- 発達心配 → transfer_to_agent('DevelopmentspecialistSpecialist')
- 健康問題 → transfer_to_agent('HealthspecialistSpecialist')
- 行動の問題 → transfer_to_agent('BehaviorspecialistSpecialist')
- 遊び・学習 → transfer_to_agent('PlaylearningspecialistSpecialist')
- 安全対策 → transfer_to_agent('SafetyspecialistSpecialist')
- メンタルケア → transfer_to_agent('MentalcarespecialistSpecialist')
- 情報検索 → transfer_to_agent('SearchspecialistSpecialist')

**フォールバック処理（重要）**:
- 判断に迷う場合 → transfer_to_agent('SearchspecialistSpecialist')
- 複数分野にまたがる場合 → 最も関連の深い専門エージェントを選択
- 一般的な相談 → transfer_to_agent('SearchspecialistSpecialist')
- どの専門分野にも該当しない場合 → transfer_to_agent('SearchspecialistSpecialist')

**動作確認**: 全ての応答は transfer_to_agent() 関数呼び出しである必要があります。
"""

            # sub_agentsリストを作成
            sub_agents_list = list(self.specialist_agents.values())

            # ADKコーディネーターはtransfer_to_agent()のみ使用、他のツールは無効化
            # gemini-2.5-flashでtransfer_to_agent()機能を使用

            coordinator = LlmAgent(
                name="GenieUs子育てコーディネーター",
                model="gemini-2.5-flash",  # ADK用モデル指定（gemini-2.5-flash）
                instruction=instruction,
                sub_agents=sub_agents_list,
                # tools=[]  # ツールを無効化してtransfer_to_agent()のみ使用
            )

            self.logger.info(f"🎯 コーディネーターエージェント作成完了: {len(sub_agents_list)}サブエージェント登録")

            return coordinator

        except Exception as e:
            self.logger.error(f"❌ コーディネーターエージェント作成失敗: {e}")
            raise

    def _build_specialist_descriptions(self) -> str:
        """専門エージェントの説明文を構築

        Returns:
            str: 専門エージェントの説明文（改行区切り）

        """
        descriptions: list[str] = []

        # エージェント説明マッピング
        agent_descriptions: dict[str, str] = {
            "nutrition_specialist": "食事・栄養・離乳食・授乳・アレルギー・偏食の相談",
            "sleep_specialist": "睡眠・夜泣き・寝かしつけ・昼寝の相談",
            "development_specialist": "発達・成長・言葉・運動能力・個人差の相談",
            "health_specialist": "健康・病気・症状・医療・予防接種の相談",
            "behavior_specialist": "行動・しつけ・イヤイヤ期・癇癪・反抗の相談",
            "play_learning_specialist": "遊び・学習・教育・知育・創造性の相談",
            "safety_specialist": "安全・事故防止・怪我・危険回避の相談",
            "work_life_specialist": "保育園・仕事復帰・職場復帰・両立・保活の相談",
            "mental_care_specialist": "ストレス・不安・疲労・メンタルケア・心理サポートの相談",
            "search_specialist": "情報検索・調査・最新情報・データ収集の相談",
        }

        for agent_name in self.specialist_agents.keys():
            if agent_name in agent_descriptions:
                descriptions.append(f"- {agent_name}: {agent_descriptions[agent_name]}")

        return "\n".join(descriptions)

    def get_coordinator_agent(self) -> LlmAgent:
        """コーディネーターエージェントを取得

        Returns:
            LlmAgent: 初期化済みコーディネーターエージェント

        """
        return self.coordinator_agent

    def get_routing_strategy_name(self) -> str:
        """ルーティング戦略名を返す

        Returns:
            str: ADK標準ルーティング戦略名

        """
        return "ADK_Standard_LlmAgent_Routing"

    def get_available_specialists(self) -> list[str]:
        """利用可能な専門エージェントリストを取得

        Returns:
            List[str]: 専門エージェント名のリスト

        """
        return list(self.specialist_agents.keys())

    def add_specialist_agent(self, agent_name: str, agent: LlmAgent) -> None:
        """専門エージェントを追加（動的追加対応）

        Args:
            agent_name: エージェント名
            agent: LlmAgentインスタンス

        Raises:
            ValueError: agent_nameが空文字列の場合
            TypeError: agentがLlmAgentでない場合

        """
        if not agent_name.strip():
            raise ValueError("agent_nameは空文字列にできません")
        if not isinstance(agent, LlmAgent):
            raise TypeError("agentはLlmAgentである必要があります")

        try:
            self.specialist_agents[agent_name] = agent

            # コーディネーターエージェントを再作成
            self.coordinator_agent = self._create_coordinator_agent()

            self.logger.info(f"📈 専門エージェント追加: {agent_name}")
        except Exception as e:
            self.logger.error(f"❌ 専門エージェント追加失敗: {agent_name}, エラー: {e}")
            raise

    def remove_specialist_agent(self, agent_name: str) -> None:
        """専門エージェントを削除

        Args:
            agent_name: 削除するエージェント名

        Raises:
            KeyError: 指定されたエージェントが存在しない場合

        """
        if agent_name not in self.specialist_agents:
            raise KeyError(f"エージェント '{agent_name}' は存在しません")

        try:
            del self.specialist_agents[agent_name]

            # コーディネーターエージェントを再作成
            self.coordinator_agent = self._create_coordinator_agent()

            self.logger.info(f"📉 専門エージェント削除: {agent_name}")
        except Exception as e:
            self.logger.error(f"❌ 専門エージェント削除失敗: {agent_name}, エラー: {e}")
            raise

    def get_routing_statistics(self) -> dict[str, any]:
        """ルーティング統計情報を取得

        Returns:
            Dict[str, any]: ルーティングシステムの統計情報

        """
        return {
            "routing_strategy": self.get_routing_strategy_name(),
            "total_specialists": len(self.specialist_agents),
            "available_specialists": self.get_available_specialists(),
            "has_tools": len(self.tools) > 0,
            "coordinator_status": "active",
            "adk_compliance": True,
            "di_logger_injected": self.logger is not None,
        }
