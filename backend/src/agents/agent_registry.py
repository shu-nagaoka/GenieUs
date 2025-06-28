"""AgentRegistry - エージェント初期化とRunner管理

15専門エージェントの初期化、登録、Runner管理を担当
"""

import logging
import os

from dotenv import load_dotenv
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from src.agents.constants import (
    AGENT_CONFIG,
    AGENT_DISPLAY_NAMES,
    AGENT_PROMPTS,
    LIGHTWEIGHT_AGENT_CONFIG,
    TOOL_ENABLED_AGENTS,
)

# ADK環境変数を明示的に読み込み
load_dotenv()


class AgentRegistry:
    """エージェント登録・管理システム

    責務:
    - 15専門エージェントの初期化
    - Sequential/Parallelパイプラインの構築
    - Runner管理
    - エージェント情報の提供
    """

    def __init__(self, tools: dict, logger: logging.Logger, app_name: str = "GenieUs"):
        """AgentRegistry初期化

        Args:
            tools: エージェントが使用するツール群
            logger: DIコンテナから注入されるロガー
            app_name: アプリケーション名

        """
        self.logger = logger
        self.tools = tools
        self._app_name = app_name

        # エージェント管理
        self._agents: dict[str, Agent] = {}
        self._runners: dict[str, Runner] = {}
        self._sequential_agent: SequentialAgent = None
        self._parallel_agent: ParallelAgent = None
        self._session_service = InMemorySessionService()

        # エージェント作成状況記録
        self._created_agents: set[str] = set()
        self._failed_agents: set[str] = set()

    def initialize_all_agents(self) -> None:
        """15専門エージェント初期化"""
        self.logger.info("15専門エージェント統合システム初期化開始")

        try:
            # 1. 15専門エージェント作成
            self._create_all_specialist_agents()

            # 2. Sequential/Parallelエージェント作成
            self._create_multi_agent_pipelines()

            # 3. Runner作成
            self._create_runners()

            # 初期化結果報告
            success_count = len(self._created_agents)
            failed_count = len(self._failed_agents)
            total_agents = len(self._agents)

            self.logger.info(
                f"15専門エージェント初期化完了: {total_agents}個作成成功, {success_count}個正常, {failed_count}個失敗",
            )

            if self._failed_agents:
                self.logger.warning(f"作成失敗エージェント: {', '.join(self._failed_agents)}")

        except Exception as e:
            self.logger.error(f"15専門エージェント初期化エラー: {e}")
            raise

    def _create_all_specialist_agents(self) -> None:
        """15専門エージェント一括作成"""
        # 環境変数確認
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
        self.logger.info(
            f"ADK環境変数: PROJECT={project}, LOCATION={location}, USE_VERTEXAI={use_vertexai}",
        )

        # Vertex AI設定の初期化
        if use_vertexai == "True" and project:
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
            os.environ["GOOGLE_CLOUD_PROJECT"] = project
            os.environ["GOOGLE_CLOUD_LOCATION"] = location
            self.logger.info(f"🔧 Vertex AI環境変数設定完了: {project}/{location}")

        # ツール確認ログ
        self.logger.info(f"🔧 利用可能ツール: {list(self.tools.keys())}")

        # 全エージェントを統一的に作成
        for agent_id, prompt in AGENT_PROMPTS.items():
            try:
                self._create_single_agent(agent_id, prompt)
                self._created_agents.add(agent_id)
                display_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
                self.logger.info(f"✅ {display_name}エージェント作成完了")
            except Exception as e:
                self._failed_agents.add(agent_id)
                display_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
                self.logger.error(f"❌ {display_name}エージェント作成失敗: {e}")

    def _create_single_agent(self, agent_id: str, instruction: str) -> None:
        """単一エージェント作成"""
        # エージェント名を決定
        # アンダースコア区切りを適切にCapitalCaseに変換
        # 既に"specialist"が含まれている場合は追加しない
        parts = agent_id.split("_")
        agent_name = "".join(part.capitalize() for part in parts)
        if not agent_name.endswith("Specialist"):
            agent_name += "Specialist"

        # ツール設定
        tools = []
        if agent_id in TOOL_ENABLED_AGENTS:
            tool_names = TOOL_ENABLED_AGENTS[agent_id]
            tools = [self.tools[tool_name] for tool_name in tool_names if tool_name in self.tools]

            if not tools:
                self.logger.warning(f"⚠️ {agent_id}: 必要なツールが利用できません ({tool_names})")
                tools = []

        # モデル選択
        model = (
            LIGHTWEIGHT_AGENT_CONFIG["model"] if agent_id == "followup_question_generator" else AGENT_CONFIG["model"]
        )

        agent_kwargs = {
            "name": agent_name,
            "model": model,
            "instruction": instruction,
        }

        # ツールがある場合のみtools引数を追加
        if tools:
            agent_kwargs["tools"] = tools

        self.logger.debug(
            f"エージェント作成パラメータ ({agent_id}): model={model}, tools={len(tools) if tools else 0}",
        )
        self._agents[agent_id] = Agent(**agent_kwargs)

    def _create_multi_agent_pipelines(self) -> None:
        """Sequential/Parallelパイプライン作成"""
        available_specialists = list(self._agents.values())

        # Sequential Pipeline
        if len(available_specialists) >= 1:
            primary_agents = []
            priority_agents = ["coordinator", "nutrition_specialist", "development_specialist"]

            for agent_id in priority_agents:
                if agent_id in self._agents:
                    primary_agents.append(self._agents[agent_id])

            # 不足分を他の専門家で補完
            remaining_agents = [agent for agent in available_specialists if agent not in primary_agents]
            while len(primary_agents) < 3 and remaining_agents:
                primary_agents.append(remaining_agents.pop(0))

            self._sequential_agent = SequentialAgent(
                name="Sequential18SpecialistPipeline",
                sub_agents=primary_agents[:3],
            )
            self.logger.info(
                f"🔄 Sequential15専門家パイプライン作成完了: {len(primary_agents[:3])}エージェント",
            )
        else:
            self.logger.error("❌ 専門エージェントが不足してSequentialパイプライン作成不可")

        # Parallel Pipeline
        if len(available_specialists) >= 2:
            parallel_specialists = []
            priority_parallel = [
                "coordinator",
                "nutrition_specialist",
                "development_specialist",
                "sleep_specialist",
                "behavior_specialist",
            ]

            for agent_id in priority_parallel:
                if agent_id in self._agents:
                    original_agent = self._agents[agent_id]
                    parallel_agent = Agent(
                        name=f"{original_agent.name}Parallel",
                        model=original_agent.model,
                        instruction=original_agent.instruction,
                        tools=original_agent.tools,
                    )
                    parallel_specialists.append(parallel_agent)

            # 不足分を補完
            if len(parallel_specialists) < 5:
                remaining_ids = [aid for aid in self._agents.keys() if aid not in priority_parallel]
                for agent_id in remaining_ids:
                    if len(parallel_specialists) >= 5:
                        break
                    original_agent = self._agents[agent_id]
                    parallel_agent = Agent(
                        name=f"{original_agent.name}Parallel",
                        model=original_agent.model,
                        instruction=original_agent.instruction,
                        tools=original_agent.tools,
                    )
                    parallel_specialists.append(parallel_agent)

            self._parallel_agent = ParallelAgent(
                name="Parallel18SpecialistPipeline",
                sub_agents=parallel_specialists[:5],
            )
            self.logger.info(
                f"⚡ Parallel15専門家パイプライン作成完了: {len(parallel_specialists[:5])}エージェント",
            )
        else:
            self.logger.warning("⚠️ 専門エージェント不足。Parallel分析パイプライン未作成")

    def _create_runners(self) -> None:
        """各エージェント用のRunner作成"""
        for agent_name, agent in self._agents.items():
            self._runners[agent_name] = Runner(
                agent=agent,
                app_name=self._app_name,
                session_service=self._session_service,
            )

        # Sequential/Parallel用のRunner
        if self._sequential_agent:
            self._runners["sequential"] = Runner(
                agent=self._sequential_agent,
                app_name=self._app_name,
                session_service=self._session_service,
            )

        if self._parallel_agent:
            self._runners["parallel"] = Runner(
                agent=self._parallel_agent,
                app_name=self._app_name,
                session_service=self._session_service,
            )

        self.logger.info(f"🏃 Runner作成完了: {len(self._runners)}個")

    # ========== 外部インターフェース ==========

    def get_agent(self, agent_type: str = "coordinator") -> Agent:
        """エージェント取得"""
        if agent_type not in self._agents:
            available = list(self._agents.keys())
            raise RuntimeError(f"エージェント '{agent_type}' が見つかりません。利用可能: {available}")
        return self._agents[agent_type]

    def get_runner(self, agent_type: str) -> Runner:
        """Runner取得"""
        if agent_type not in self._runners:
            raise RuntimeError(f"Runner '{agent_type}' が見つかりません")
        return self._runners[agent_type]

    def get_all_agents(self) -> dict[str, Agent]:
        """全エージェント取得"""
        return self._agents.copy()

    def get_all_runners(self) -> dict[str, Runner]:
        """全Runner取得"""
        return self._runners.copy()

    def get_session_service(self) -> InMemorySessionService:
        """セッションサービス取得"""
        return self._session_service

    def get_agent_info(self) -> dict[str, dict[str, any]]:
        """15専門エージェント情報取得"""
        from src.agents.constants import AGENT_KEYWORDS

        info = {}
        for agent_id, agent in self._agents.items():
            display_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
            info[agent_id] = {
                "name": agent.name,
                "display_name": display_name,
                "model": agent.model,
                "tools_count": len(agent.tools) if agent.tools else 0,
                "type": "specialist",
                "has_tools": agent_id in TOOL_ENABLED_AGENTS,
                "keywords_count": len(AGENT_KEYWORDS.get(agent_id, [])),
            }

        # Sequential/Parallel情報追加
        if self._sequential_agent:
            info["sequential_pipeline"] = {
                "name": self._sequential_agent.name,
                "display_name": "Sequential15専門家パイプライン",
                "model": "pipeline",
                "sub_agents_count": len(self._sequential_agent.sub_agents),
                "type": "sequential",
                "has_tools": False,
                "keywords_count": 0,
            }

        if self._parallel_agent:
            info["parallel_pipeline"] = {
                "name": self._parallel_agent.name,
                "display_name": "Parallel15専門家パイプライン",
                "model": "pipeline",
                "sub_agents_count": len(self._parallel_agent.sub_agents),
                "type": "parallel",
                "has_tools": False,
                "keywords_count": 0,
            }

        return info

    def get_available_agent_types(self) -> list[str]:
        """利用可能なエージェントタイプ一覧"""
        types = list(self._agents.keys())
        if self._sequential_agent:
            types.append("sequential")
        if self._parallel_agent:
            types.append("parallel")
        types.append("auto")  # 自動選択
        return types

    def get_specialist_llm_agents(self) -> dict[str, "LlmAgent"]:
        """専門エージェントをLlmAgent形式で取得（ADKルーティング統合用）

        Returns:
            Dict[str, LlmAgent]: 専門エージェントのLlmAgent変換版

        Note:
            既存のAgentをLlmAgentでラップして、ADK標準ルーティングとの互換性を確保

        """
        from google.adk.agents import LlmAgent

        specialist_llm_agents = {}

        # 専門エージェントのリスト（sequential/parallelを除く）
        specialist_types = [
            "nutrition_specialist",
            "sleep_specialist",
            "development_specialist",
            "health_specialist",
            "behavior_specialist",
            "play_learning_specialist",
            "safety_specialist",
            "work_life_specialist",
            "mental_care_specialist",
            "search_specialist",
        ]

        for agent_id in specialist_types:
            if agent_id in self._agents:
                original_agent = self._agents[agent_id]

                # 既存AgentをLlmAgentでラップ（ADK標準対応）
                # 注意: specialist agentは転送機能を無効化（自分の専門分野で回答）
                # ただし、search_specialistのみgoogle_searchツールを有効化
                # specialist agentのツール設定
                tools_for_agent = []
                if agent_id == "search_specialist":
                    # search_specialistのみADKのgoogle_searchツールを有効化
                    from google.adk.tools import google_search

                    tools_for_agent = [google_search]

                llm_agent = LlmAgent(
                    name=original_agent.name,
                    model="gemini-2.5-flash",  # ADK標準モデル
                    instruction=original_agent.instruction,
                    tools=tools_for_agent,  # search_specialistのみツール有効、他は空配列
                )

                specialist_llm_agents[agent_id] = llm_agent

        self.logger.info(f"🔄 専門エージェントLlmAgent変換完了: {len(specialist_llm_agents)}個")
        return specialist_llm_agents

    def register_adk_coordinator(self, coordinator_agent: "LlmAgent") -> None:
        """ADKコーディネーターエージェントを登録してRunner作成

        Args:
            coordinator_agent: ADK標準LlmAgentコーディネーター

        """
        from google.adk.runners import Runner

        self.logger.info("🔧 ADKコーディネーター登録開始...")

        # ADKコーディネーターエージェントを登録
        self._agents["adk_coordinator"] = coordinator_agent
        self.logger.info(f"📋 ADKコーディネーターAgent登録: {coordinator_agent.name}")

        # ADKコーディネーター用のRunner作成
        self._runners["adk_coordinator"] = Runner(
            agent=coordinator_agent,
            app_name=self._app_name,
            session_service=self._session_service,
        )
        self.logger.info(f"🏃 ADKコーディネーターRunner登録: app_name={self._app_name}")

        # 登録確認
        total_runners = len(self._runners)
        self.logger.info(f"✅ ADKコーディネーターAgent & Runner登録完了 (総Runner数: {total_runners})")

    @property
    def default_runner(self) -> Runner:
        """デフォルトRunner（coordinatorを返す）"""
        if "coordinator" in self._runners:
            return self._runners["coordinator"]
        elif self._runners:
            return list(self._runners.values())[0]
        else:
            raise RuntimeError("Runnerが初期化されていません")
