"""AgentManager - 18専門エージェント統合版

18人の専門エージェントによる包括的子育て支援システム
- プロンプト管理の統一（constants.py使用）
- 専門領域の細分化とルーティング最適化
- マルチエージェント協調による高度な支援
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
import google.generativeai as genai
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from src.agents.constants import (
    AGENT_PROMPTS,
    AGENT_DISPLAY_NAMES,
    AGENT_CONFIG,
    LIGHTWEIGHT_AGENT_CONFIG,
    TOOL_ENABLED_AGENTS,
    AGENT_KEYWORDS,
    AGENT_PRIORITY,
    FORCE_ROUTING_KEYWORDS,
)

# ADK環境変数を明示的に読み込み
load_dotenv()


class AgentManager:
    """18専門エージェント統合管理システム"""

    def __init__(self, tools: dict, logger: logging.Logger, settings):
        """AgentManager初期化 - 18エージェント対応"""
        self.logger = logger
        self.settings = settings
        self.tools = tools

        # 18専門エージェント管理
        self._agents: dict[str, Agent] = {}
        self._runners: dict[str, Runner] = {}
        self._sequential_agent: SequentialAgent = None
        self._parallel_agent: ParallelAgent = None
        self._session_service = InMemorySessionService()
        self._app_name = "GenieUs"

        # エージェント作成状況記録
        self._created_agents = set()
        self._failed_agents = set()

    def initialize_all_components(self) -> None:
        """18専門エージェント初期化"""
        self.logger.info("18専門エージェント統合システム初期化開始")

        try:
            # 1. 18専門エージェント作成（constants.pyベース）
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
                f"18専門エージェント初期化完了: {total_agents}個作成成功, {success_count}個正常, {failed_count}個失敗"
            )

            if self._failed_agents:
                self.logger.warning(f"作成失敗エージェント: {', '.join(self._failed_agents)}")

        except Exception as e:
            self.logger.error(f"18専門エージェント初期化エラー: {e}")
            raise

    def _create_all_specialist_agents(self) -> None:
        """18専門エージェント一括作成（constants.pyベース）"""
        # 環境変数確認（デバッグ）
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
        self.logger.info(f"ADK環境変数: PROJECT={project}, LOCATION={location}, USE_VERTEXAI={use_vertexai}")

        # Vertex AI設定の初期化（ADK用）
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
        # エージェント名を決定（大文字開始の英語名）
        agent_name = agent_id.replace("_", "").title() + "Specialist"

        # ツール設定（ツール利用可能エージェントのみ）
        tools = []
        if agent_id in TOOL_ENABLED_AGENTS:
            tool_names = TOOL_ENABLED_AGENTS[agent_id]
            tools = [self.tools[tool_name] for tool_name in tool_names if tool_name in self.tools]

            # ツールが利用できない場合はスキップまたは警告
            if not tools:
                self.logger.warning(f"⚠️ {agent_id}: 必要なツールが利用できません ({tool_names})")
                tools = []

        # エージェント作成（環境変数のみに依存）
        # フォローアップクエスチョン生成は軽量モデルを使用
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

        self.logger.debug(f"エージェント作成パラメータ ({agent_id}): model={model}, tools={len(tools) if tools else 0}")
        self._agents[agent_id] = Agent(**agent_kwargs)

    def _create_multi_agent_pipelines(self) -> None:
        """18専門エージェント対応Sequential/Parallelパイプライン作成"""
        available_specialists = list(self._agents.values())

        if len(available_specialists) >= 1:
            # 段階的分析パイプライン（主要3専門家で構成）
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
                sub_agents=primary_agents[:3],  # 最大3専門家
            )
            self.logger.info(f"🔄 Sequential18専門家パイプライン作成完了: {len(primary_agents[:3])}エージェント")
        else:
            self.logger.error("❌ 専門エージェントが不足してSequentialパイプライン作成不可")

        # 並列分析パイプライン（主要5専門家で構成）
        if len(available_specialists) >= 2:
            parallel_specialists = []
            # 重要な専門家を優先選択
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
                    # 複製エージェント作成（並列実行用）
                    parallel_agent = Agent(
                        name=f"{original_agent.name}Parallel",
                        model=original_agent.model,
                        instruction=original_agent.instruction,
                        tools=original_agent.tools,
                    )
                    parallel_specialists.append(parallel_agent)

            # 不足分を他の専門家で補完
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
                sub_agents=parallel_specialists[:5],  # 最大5専門家
            )
            self.logger.info(f"⚡ Parallel18専門家パイプライン作成完了: {len(parallel_specialists[:5])}エージェント")
        else:
            self.logger.warning("⚠️ 専門エージェント不足。Parallel分析パイプライン未作成")

    def _create_runners(self) -> None:
        """各エージェント用のRunner作成"""
        for agent_name, agent in self._agents.items():
            self._runners[agent_name] = Runner(
                agent=agent, app_name=self._app_name, session_service=self._session_service
            )

        # Sequential/Parallel用のRunner
        if self._sequential_agent:
            self._runners["sequential"] = Runner(
                agent=self._sequential_agent, app_name=self._app_name, session_service=self._session_service
            )

        if self._parallel_agent:
            self._runners["parallel"] = Runner(
                agent=self._parallel_agent, app_name=self._app_name, session_service=self._session_service
            )

        self.logger.info(f"🏃 Runner作成完了: {len(self._runners)}個")

    # ========== 外部インターフェース ==========

    def get_agent(self, agent_type: str = "coordinator") -> Agent:
        """エージェント取得"""
        if agent_type not in self._agents:
            available = list(self._agents.keys())
            raise RuntimeError(f"エージェント '{agent_type}' が見つかりません。利用可能: {available}")
        return self._agents[agent_type]

    async def route_query_async(
        self,
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session",
        agent_type: str = "auto",
        conversation_history: list = None,
        family_info: dict = None,
    ) -> str:
        """マルチエージェント対応クエリ実行（非同期）"""
        try:
            # エージェント選択ロジック（監視強化）
            routing_start_time = self._import_time()
            if agent_type == "auto":
                selected_agent_type = self._determine_agent_type(message)
                self._log_routing_decision(message, selected_agent_type, "auto_routing")
            elif agent_type in ["sequential", "parallel"]:
                selected_agent_type = agent_type
                self._log_routing_decision(message, selected_agent_type, "explicit_routing")
            else:
                selected_agent_type = agent_type
                self._log_routing_decision(message, selected_agent_type, "direct_routing")

            routing_duration = self._import_time() - routing_start_time
            self.logger.info(f"🎯 ルーティング決定: {selected_agent_type} (判定時間: {routing_duration:.3f}s)")
            self.logger.info(f"🔧 利用可能なRunners: {list(self._runners.keys())}")

            # ルーティング妥当性事前チェック
            if not self._validate_routing_decision(message, selected_agent_type):
                self.logger.warning(f"⚠️ ルーティング妥当性警告: {selected_agent_type} が適切でない可能性")
                # 自動修正ロジック
                corrected_agent = self._auto_correct_routing(message, selected_agent_type)
                if corrected_agent != selected_agent_type:
                    self.logger.info(f"🔧 ルーティング自動修正: {selected_agent_type} → {corrected_agent}")
                    selected_agent_type = corrected_agent

            # Runner取得
            if selected_agent_type not in self._runners:
                self.logger.warning(f"⚠️ {selected_agent_type} Runnerが見つかりません。coordinatorを使用")
                selected_agent_type = "coordinator"

            runner = self._runners[selected_agent_type]
            self.logger.info(f"🚀 実行エージェント: {selected_agent_type} (Agent: {runner.agent.name})")
            await self._ensure_session_exists(user_id, session_id)

            # 履歴と家族情報を含めたメッセージ作成
            enhanced_message = self._create_message_with_context(message, conversation_history, family_info)
            content = Content(role="user", parts=[Part(text=enhanced_message)])

            # ADK実行
            events = []
            tool_used = False
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                events.append(event)

                # ツール使用検出（詳細ログ）
                if hasattr(event, "actions") and event.actions:
                    tool_used = True
                    try:
                        action_count = len(list(event.actions)) if hasattr(event.actions, "__iter__") else 1
                        self.logger.info(f"🔧 {selected_agent_type} ツール実行検出: {action_count}個のアクション")

                        # アクション詳細をログ出力
                        for i, action in enumerate(event.actions):
                            self.logger.info(f"📋 アクション#{i + 1}: {type(action).__name__}")
                            self.logger.info(f"📄 アクション内容: {str(action)[:500]}...")
                    except Exception as e:
                        self.logger.info(f"🔧 ツール実行検出: アクションあり (詳細取得エラー: {e})")

                # レスポンス内容の詳細ログ
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts") and event.content.parts:
                        for i, part in enumerate(event.content.parts):
                            if hasattr(part, "function_response"):
                                self.logger.info(f"🔧 ツールレスポンス#{i + 1}: {str(part.function_response)[:500]}...")
                            elif hasattr(part, "text") and len(str(part.text)) > 0:
                                self.logger.info(f"💬 {selected_agent_type} 文章#{i + 1}: {str(part.text)[:200]}...")

            self.logger.info(
                f"🔧 {selected_agent_type} ツール使用結果: {'使用された' if tool_used else '使用されなかった'}"
            )

            # レスポンス抽出
            if events and hasattr(events[-1], "content") and events[-1].content:
                response = self._extract_response_text(events[-1].content)

                # コーディネーターの回答を分析して、専門家への紹介があるかチェック
                if selected_agent_type == "coordinator":
                    specialist_response = await self._check_and_route_to_specialist(
                        message, response, user_id, session_id, conversation_history, family_info
                    )
                    if specialist_response:
                        # フォローアップクエスチョンを生成
                        followup_questions = await self._generate_followup_questions(message, specialist_response)

                        # 専門家回答を直接使用（ルーティング案内は削除）
                        combined_response = specialist_response

                        if followup_questions:
                            combined_response += f"\n\n**【続けて相談したい方へ】**\n{followup_questions}"

                        return combined_response

                # 専門家の直接回答の場合もフォローアップクエスチョンを追加
                if selected_agent_type != "coordinator" and selected_agent_type not in ["sequential", "parallel"]:
                    followup_questions = await self._generate_followup_questions(message, response)
                    if followup_questions:
                        return f"{response}\n\n**【続けて相談したい方へ】**\n{followup_questions}"

                return response
            else:
                raise Exception("No response from agent")

        except Exception as e:
            self.logger.error(f"エージェント実行エラー: {e}")
            return f"申し訳ございません。システムエラーが発生しました: {str(e)}"

    def _determine_agent_type(self, message: str) -> str:
        """強化されたルーティング決定ロジック（安定化対応）"""
        message_lower = message.lower()

        # ステップ1: 強制ルーティングキーワードチェック（最優先）
        force_routed_agent = self._check_force_routing(message_lower)
        if force_routed_agent:
            self.logger.info(f"🚨 強制ルーティング: {force_routed_agent}")
            return force_routed_agent

        # ステップ2: 並列・順次分析キーワードチェック
        if self._is_parallel_analysis_requested(message_lower):
            return "parallel"

        if self._is_sequential_analysis_requested(message_lower):
            return "sequential"

        # ステップ3: 専門エージェント決定論的ルーティング
        specialist_agent = self._determine_specialist_agent(message_lower)
        if specialist_agent and specialist_agent != "coordinator":
            self.logger.info(f"🎯 専門エージェント決定: {specialist_agent}")
            return "coordinator"  # コーディネーター経由で専門家へ

        # ステップ4: デフォルト（コーディネーター）
        self.logger.info("📋 デフォルトルーティング: coordinator")
        return "coordinator"

    def _check_force_routing(self, message_lower: str) -> str:
        """強制ルーティングキーワードチェック（緊急性・専門性が高い）"""
        for agent_id, force_keywords in FORCE_ROUTING_KEYWORDS.items():
            matched_keywords = [kw for kw in force_keywords if kw in message_lower]
            if matched_keywords:
                self.logger.info(
                    f"🚨 強制ルーティング検出: {AGENT_DISPLAY_NAMES.get(agent_id, agent_id)} (キーワード: {matched_keywords[:3]})"
                )
                return agent_id
        return None

    def _is_parallel_analysis_requested(self, message_lower: str) -> bool:
        """並列分析要求の判定"""
        parallel_keywords = [
            "総合的に",
            "詳しく分析",
            "複数の視点",
            "全体的に",
            "多角的に",
            "いろんな角度から",
            "様々な専門家に",
            "チーム分析",
            "みんなで分析",
            "複数の専門家",
            "多面的",
            "包括的",
            "トータル",
            "全ての専門家",
            "複合的",
        ]
        return any(keyword in message_lower for keyword in parallel_keywords)

    def _is_sequential_analysis_requested(self, message_lower: str) -> bool:
        """順次分析要求の判定"""
        sequential_keywords = ["段階的に", "順番に", "ステップごとに", "順序立てて", "一つずつ", "順次", "段階的分析"]
        return any(keyword in message_lower for keyword in sequential_keywords)

    def _determine_specialist_agent(self, message_lower: str) -> str:
        """専門エージェント決定（優先度ベース + 信頼性向上）"""
        # マッチしたエージェントとスコアを計算
        agent_scores = {}

        for agent_id, keywords in AGENT_KEYWORDS.items():
            if agent_id in AGENT_PRIORITY:  # 専門エージェントのみ対象
                matched_keywords = [kw for kw in keywords if kw in message_lower]
                if matched_keywords:
                    # スコア計算: マッチ数 × 優先度 × キーワード長さ重み
                    keyword_weight = sum(len(kw) for kw in matched_keywords)  # 長いキーワードほど重み大
                    score = len(matched_keywords) * AGENT_PRIORITY[agent_id] * (1 + keyword_weight * 0.1)
                    agent_scores[agent_id] = {
                        "score": score,
                        "matched_keywords": matched_keywords[:3],  # ログ用
                        "match_count": len(matched_keywords),
                    }

        if not agent_scores:
            return "coordinator"

        # 最高スコアのエージェントを選択
        best_agent = max(agent_scores.items(), key=lambda x: x[1]["score"])
        agent_id, score_info = best_agent

        self.logger.info(
            f"🎯 専門エージェント決定論的選択: {agent_id} "
            f"(スコア: {score_info['score']:.1f}, マッチ: {score_info['match_count']}件, "
            f"キーワード: {score_info['matched_keywords']})"
        )

        # 競合がある場合の追加ログ
        if len(agent_scores) > 1:
            sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1]["score"], reverse=True)
            competitors = [f"{aid}({info['score']:.1f})" for aid, info in sorted_agents[1:3]]
            self.logger.info(f"🔄 他候補: {', '.join(competitors)}")

        return agent_id

    async def _perform_specialist_routing(
        self, message: str, user_id: str, session_id: str, conversation_history: list = None, family_info: dict = None
    ) -> str:
        """強化されたスペシャリストルーティング（フォールバック対応）"""
        message_lower = message.lower()

        # ステップ1: 強制ルーティングチェック
        force_agent = self._check_force_routing(message_lower)
        if force_agent and force_agent in self._agents:
            self.logger.info(f"🚨 強制ルーティング実行: {AGENT_DISPLAY_NAMES.get(force_agent, force_agent)}")
            return await self._route_to_specific_agent_with_fallback(
                force_agent, message, user_id, session_id, conversation_history, family_info
            )

        # ステップ2: 決定論的専門エージェント選択
        specialist_agent = self._determine_specialist_agent(message_lower)
        if specialist_agent and specialist_agent != "coordinator" and specialist_agent in self._agents:
            self.logger.info(
                f"🔄 コーディネーター→{AGENT_DISPLAY_NAMES.get(specialist_agent, specialist_agent)}へルーティング"
            )
            return await self._route_to_specific_agent_with_fallback(
                specialist_agent, message, user_id, session_id, conversation_history, family_info
            )

        # ステップ3: フォールバック階層（汎用性の高い順）
        fallback_priority = [
            "development_specialist",
            "play_learning_specialist",
            "health_specialist",
            "nutrition_specialist",
        ]
        for fallback_agent in fallback_priority:
            if fallback_agent in self._agents:
                self.logger.info(
                    f"🔄 フォールバックルーティング: {AGENT_DISPLAY_NAMES.get(fallback_agent, fallback_agent)}"
                )
                return await self._route_to_specific_agent_with_fallback(
                    fallback_agent, message, user_id, session_id, conversation_history, family_info
                )

        # ステップ4: 最終フォールバック
        self.logger.warning("⚠️ 全ての専門エージェントが利用できません。コーディネーターで対応します。")
        return "コーディネーターで直接対応いたします。"

    async def _route_to_specific_agent_with_fallback(
        self,
        agent_id: str,
        message: str,
        user_id: str,
        session_id: str,
        conversation_history: list = None,
        family_info: dict = None,
        retry_count: int = 0,
        max_retries: int = 2,
    ) -> str:
        """フォールバック機能付き専門エージェント実行"""
        if agent_id not in self._agents:
            self.logger.error(f"❌ エージェント {agent_id} が存在しません")
            return await self._execute_fallback_agent(message, user_id, session_id, conversation_history, family_info)

        try:
            # 専門エージェント実行
            runner = self._runners.get(agent_id)
            if not runner:
                self.logger.error(f"❌ Runner {agent_id} が存在しません")
                return await self._execute_fallback_agent(
                    message, user_id, session_id, conversation_history, family_info
                )

            await self._ensure_session_exists(user_id, session_id)
            enhanced_message = self._create_message_with_context(message, conversation_history, family_info)
            content = Content(role="user", parts=[Part(text=enhanced_message)])

            # 実行結果検証
            events = []
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                events.append(event)

            # レスポンス品質検証
            if events and hasattr(events[-1], "content") and events[-1].content:
                response = self._extract_response_text(events[-1].content)

                # レスポンス妥当性チェック
                if self._validate_agent_response(response, agent_id, message):
                    self.logger.info(f"✅ {agent_id} レスポンス検証成功")
                    return response
                else:
                    self.logger.warning(f"⚠️ {agent_id} レスポンス品質不良、リトライ実行")
                    if retry_count < max_retries:
                        return await self._route_to_specific_agent_with_fallback(
                            agent_id,
                            message,
                            user_id,
                            session_id,
                            conversation_history,
                            family_info,
                            retry_count + 1,
                            max_retries,
                        )
                    else:
                        self.logger.error(f"❌ {agent_id} 最大リトライ回数到達、フォールバック実行")
                        return await self._execute_fallback_agent(
                            message, user_id, session_id, conversation_history, family_info
                        )
            else:
                self.logger.error(f"❌ {agent_id} からレスポンスを取得できませんでした")
                return await self._execute_fallback_agent(
                    message, user_id, session_id, conversation_history, family_info
                )

        except Exception as e:
            self.logger.error(f"❌ 専門エージェント({agent_id})実行エラー: {e}")
            if retry_count < max_retries:
                self.logger.info(f"🔄 リトライ実行 ({retry_count + 1}/{max_retries})")
                return await self._route_to_specific_agent_with_fallback(
                    agent_id,
                    message,
                    user_id,
                    session_id,
                    conversation_history,
                    family_info,
                    retry_count + 1,
                    max_retries,
                )
            else:
                return await self._execute_fallback_agent(
                    message, user_id, session_id, conversation_history, family_info
                )

    def _validate_agent_response(self, response: str, agent_id: str, original_message: str) -> bool:
        """エージェントレスポンスの妥当性検証"""
        if not response or len(response.strip()) < 20:
            return False

        # エージェント固有の妥当性チェック
        expected_patterns = {
            "nutrition_specialist": ["栄養", "食事", "離乳食", "食べ"],
            "sleep_specialist": ["睡眠", "寝", "夜泣き"],
            "health_specialist": ["健康", "体調", "症状", "病院"],
            "development_specialist": ["発達", "成長", "言葉"],
            "behavior_specialist": ["行動", "しつけ", "イヤイヤ"],
        }

        if agent_id in expected_patterns:
            patterns = expected_patterns[agent_id]
            if not any(pattern in response for pattern in patterns):
                self.logger.warning(f"⚠️ {agent_id} 専門性関連キーワードが不足: {patterns}")
                return False

        # 一般的品質チェック
        error_indicators = ["エラー", "申し訳", "システム", "問題が発生"]
        if any(indicator in response for indicator in error_indicators):
            self.logger.warning(f"⚠️ エラー指標を含むレスポンス: {error_indicators}")
            return False

        return True

    async def _execute_fallback_agent(
        self, message: str, user_id: str, session_id: str, conversation_history: list = None, family_info: dict = None
    ) -> str:
        """フォールバックエージェント実行"""
        # 安全なフォールバック順序
        fallback_agents = ["coordinator", "nutrition_specialist", "health_specialist"]

        for fallback_agent in fallback_agents:
            if fallback_agent in self._agents and fallback_agent in self._runners:
                try:
                    self.logger.info(f"🔄 フォールバックエージェント実行: {fallback_agent}")
                    runner = self._runners[fallback_agent]
                    await self._ensure_session_exists(user_id, session_id)
                    enhanced_message = self._create_message_with_context(message, conversation_history, family_info)
                    content = Content(role="user", parts=[Part(text=enhanced_message)])

                    events = []
                    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                        events.append(event)

                    if events and hasattr(events[-1], "content") and events[-1].content:
                        response = self._extract_response_text(events[-1].content)
                        if response and len(response.strip()) > 10:
                            self.logger.info(f"✅ フォールバック成功: {fallback_agent}")
                            return f"【{AGENT_DISPLAY_NAMES.get(fallback_agent, fallback_agent)}より】\n{response}"

                except Exception as e:
                    self.logger.error(f"❌ フォールバックエージェント({fallback_agent})エラー: {e}")
                    continue

        # 最終的なエラーメッセージ
        self.logger.error("❌ 全てのフォールバック手段が失敗しました")
        return "申し訳ございません。現在システムで問題が発生しており、専門的なアドバイスを提供できません。しばらく時間をおいてから再度お試しいただくか、緊急の場合は直接医療機関にご相談ください。"

    async def _route_to_specific_agent(
        self,
        agent_id: str,
        message: str,
        user_id: str,
        session_id: str,
        conversation_history: list = None,
        family_info: dict = None,
    ) -> str:
        """指定された専門エージェントへの直接ルーティング"""
        if agent_id not in self._agents:
            return f"申し訳ございません。{AGENT_DISPLAY_NAMES.get(agent_id, agent_id)}は現在利用できません。"

        try:
            # 専門エージェント実行
            runner = self._runners.get(agent_id)
            if not runner:
                return (
                    f"申し訳ございません。{AGENT_DISPLAY_NAMES.get(agent_id, agent_id)}のシステムエラーが発生しました。"
                )

            await self._ensure_session_exists(user_id, session_id)
            enhanced_message = self._create_message_with_context(message, conversation_history, family_info)
            content = Content(role="user", parts=[Part(text=enhanced_message)])

            # 専門エージェント実行
            events = []
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                events.append(event)

            # レスポンス抽出
            if events and hasattr(events[-1], "content") and events[-1].content:
                return self._extract_response_text(events[-1].content)
            else:
                return f"{AGENT_DISPLAY_NAMES.get(agent_id, agent_id)}からの回答を取得できませんでした。"

        except Exception as e:
            self.logger.error(f"専門エージェント({agent_id})実行エラー: {e}")
            return f"申し訳ございません。{AGENT_DISPLAY_NAMES.get(agent_id, agent_id)}でエラーが発生しました。"

    async def _check_and_route_to_specialist(
        self,
        original_message: str,
        coordinator_response: str,
        user_id: str,
        session_id: str,
        conversation_history: list = None,
        family_info: dict = None,
    ) -> str:
        """コーディネーターのレスポンスから専門家紹介を検出し、自動ルーティング"""
        response_lower = coordinator_response.lower()

        # 専門家への紹介キーワードを検出
        routing_keywords = [
            "専門家",
            "専門医",
            "栄養士",
            "睡眠専門",
            "発達専門",
            "健康管理",
            "行動専門",
            "遊び専門",
            "安全専門",
            "心理専門",
            "仕事両立",
            "特別支援",
            "詳しく相談",
            "専門的なアドバイス",
            "より詳しく",
            "専門家に相談",
            # 新しいキーワードパターン（ジーニー表現）
            "ジーニーが心を込めて",
            "ジーニーが",
            "お答えします",
            "回答します",
            "サポートします",
            "アドバイスします",
        ]

        # キーワード検出による自動ルーティング
        keyword_match = any(keyword in response_lower for keyword in routing_keywords)

        # 元のメッセージが専門的な相談の場合は強制的にルーティング（キーワードに依存しない）
        specialist_agent = self._determine_specialist_agent(original_message.lower())
        should_route_automatically = (
            specialist_agent and specialist_agent != "coordinator" and specialist_agent in self._agents
        )

        if keyword_match or should_route_automatically:
            if keyword_match:
                self.logger.info("🔄 コーディネーターが専門家紹介を提案、自動ルーティング開始")
            else:
                self.logger.info("🔄 専門的相談を検出、強制的に専門家ルーティング開始")

            # 元のメッセージから適切な専門家を判定
            specialist_response = await self._perform_specialist_routing(
                original_message, user_id, session_id, conversation_history, family_info
            )

            if specialist_response and specialist_response != "コーディネーターで直接対応いたします。":
                self.logger.info(f"✅ 専門家ルーティング成功: レスポンス長={len(specialist_response)}")
                return specialist_response
            else:
                self.logger.warning("⚠️ 専門家ルーティングが失敗またはフォールバック")

        return None

    def _get_specialist_name_from_response(self, response: str) -> str:
        """コーディネーターのレスポンスから紹介された専門家名を抽出"""
        response_lower = response.lower()

        # 専門家名のマッピング
        specialist_mappings = {
            "栄養": "栄養・食事専門家",
            "食事": "栄養・食事専門家",
            "睡眠": "睡眠専門家",
            "夜泣き": "睡眠専門家",
            "発達": "発達支援専門家",
            "健康": "健康管理専門家",
            "体調": "健康管理専門家",
            "行動": "行動・しつけ専門家",
            "しつけ": "行動・しつけ専門家",
            "遊び": "遊び・学習専門家",
            "学習": "遊び・学習専門家",
            "安全": "安全・事故防止専門家",
            "事故": "安全・事故防止専門家",
            "心理": "心理・メンタルケア専門家",
            "メンタル": "心理・メンタルケア専門家",
            "仕事": "社会復帰・仕事両立専門家",
            "両立": "社会復帰・仕事両立専門家",
            "特別支援": "特別支援・療育専門家",
            "療育": "特別支援・療育専門家",
        }

        for keyword, specialist_name in specialist_mappings.items():
            if keyword in response_lower:
                return specialist_name

        return "専門家"

    def _create_routing_message(self, original_message: str, specialist_name: str) -> str:
        """ジーニーらしい自然なルーティング案内を生成"""
        try:
            # メッセージの内容に応じたジーニーらしいルーティング案内を生成
            message_lower = original_message.lower()

            # 相談内容のキーワード検出と具体的な理由説明（優先順位順）
            # 1. 特別支援・療育（最優先）
            if any(
                keyword in message_lower
                for keyword in ["特別支援", "療育", "発達障害", "自閉症", "ADHD", "支援級", "合理的配慮"]
            ):
                reason = self._get_special_support_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。特別支援・療育のジーニーが心を込めてお答えします。\n\n---\n\n"
            # 2. 安全・緊急事項（高優先）
            elif any(
                keyword in message_lower
                for keyword in ["安全", "事故", "危険", "転落", "誤飲", "やけど", "ケガ", "怪我"]
            ):
                reason = self._get_safety_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。安全・事故防止のジーニーが心を込めてお答えします。\n\n---\n\n"
            # 3. 健康・体調（高優先）
            elif any(
                keyword in message_lower
                for keyword in ["体調", "熱", "病気", "健康", "咳", "鼻水", "風邪", "受診", "症状"]
            ):
                reason = self._get_health_reason(message_lower)
                return (
                    f"✨ ご質問ありがとうございます！{reason}。健康管理のジーニーが心を込めてお答えします。\n\n---\n\n"
                )
            # 4. 発達関連（歩く、言葉など）
            elif any(
                keyword in message_lower
                for keyword in [
                    "発達",
                    "成長",
                    "言葉",
                    "歩かない",
                    "歩く",
                    "話さない",
                    "話す",
                    "立つ",
                    "這う",
                    "座る",
                    "まだ歩",
                ]
            ):
                reason = self._get_development_reason(message_lower)
                return (
                    f"✨ ご質問ありがとうございます！{reason}。発達支援のジーニーが心を込めてお答えします。\n\n---\n\n"
                )
            # 5. 仕事復帰・両立関連
            elif any(
                keyword in message_lower
                for keyword in [
                    "仕事復帰",
                    "職場復帰",
                    "保育園が心配",
                    "保育園",
                    "両立",
                    "働く",
                    "時短",
                    "育休",
                    "仕事",
                ]
            ):
                reason = self._get_work_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。社会復帰・仕事両立のジーニーが心を込めてお答えします。\n\n---\n\n"
            # 6. 栄養・食事関連
            elif any(
                keyword in message_lower
                for keyword in ["アレルギー", "食べない", "離乳食", "栄養", "食事", "ミルク", "母乳", "偏食", "野菜"]
            ):
                reason = self._get_nutrition_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。栄養・食事のジーニーが心を込めてお答えします。\n\n---\n\n"
            # 7. 睡眠関連
            elif any(
                keyword in message_lower
                for keyword in ["夜泣き", "寝ない", "睡眠", "寝かしつけ", "昼寝", "夜中", "朝方", "寝つき", "起きる"]
            ):
                reason = self._get_sleep_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。睡眠のジーニーが心を込めてお答えします。\n\n---\n\n"
            # 8. 行動・しつけ関連
            elif any(
                keyword in message_lower
                for keyword in ["イヤイヤ", "しつけ", "行動", "わがまま", "かんしゃく", "癇癪", "反抗", "叱り"]
            ):
                reason = self._get_behavior_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。行動・しつけのジーニーが心を込めてお答えします。\n\n---\n\n"
            # 9. 遊び・学習関連
            elif any(
                keyword in message_lower
                for keyword in ["遊び", "学習", "知育", "おもちゃ", "工作", "絵本", "読み聞かせ"]
            ):
                reason = self._get_play_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。遊び・学習のジーニーが心を込めてお答えします。\n\n---\n\n"
            # 10. メンタルケア関連（広いキーワードなので後の方に配置）
            elif any(keyword in message_lower for keyword in ["ストレス", "疲れ", "産後", "気持ち", "メンタル"]):
                reason = self._get_mental_reason(message_lower)
                return f"✨ ご質問ありがとうございます！{reason}。心理・メンタルケアのジーニーが心を込めてお答えします。\n\n---\n\n"
            else:
                # specialist_nameを使用してフォールバック
                return f"✨ ご質問ありがとうございます！この件について詳しい{specialist_name}が心を込めてお答えします。\n\n---\n\n"

        except Exception as e:
            self.logger.warning(f"ルーティングメッセージ生成エラー: {e}")
            return f"✨ ご質問ありがとうございます！専門のジーニーが心を込めてお答えします。\n\n---\n\n"

    def _get_nutrition_reason(self, message_lower: str) -> str:
        """栄養・食事専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["離乳食", "食べない", "食べてくれない"]):
            return "離乳食・お食事のご相談ですね"
        elif any(word in message_lower for word in ["アレルギー", "アレルギー反応"]):
            return "アレルギーについてのご心配ですね"
        elif any(word in message_lower for word in ["栄養", "栄養バランス", "栄養不足"]):
            return "栄養バランスのご相談ですね"
        elif any(word in message_lower for word in ["偏食", "好き嫌い", "野菜を食べない"]):
            return "偏食・好き嫌いのご相談ですね"
        elif any(word in message_lower for word in ["ミルク", "母乳", "授乳"]):
            return "授乳・ミルクのご相談ですね"
        else:
            return "お食事・栄養のご相談ですね"

    def _get_sleep_reason(self, message_lower: str) -> str:
        """睡眠専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["夜泣き", "夜中に起きる"]):
            return "夜泣きでお困りですね"
        elif any(word in message_lower for word in ["寝ない", "寝てくれない", "眠らない"]):
            return "なかなか寝てくれないご相談ですね"
        elif any(word in message_lower for word in ["寝かしつけ", "寝つき"]):
            return "寝かしつけについてのご相談ですね"
        elif any(word in message_lower for word in ["昼寝", "お昼寝"]):
            return "昼寝についてのご相談ですね"
        elif any(word in message_lower for word in ["睡眠リズム", "生活リズム"]):
            return "睡眠リズムのご相談ですね"
        else:
            return "睡眠についてのご相談ですね"

    def _get_development_reason(self, message_lower: str) -> str:
        """発達支援専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["言葉", "話さない", "言葉が遅い"]):
            return "言葉の発達についてのご相談ですね"
        elif any(word in message_lower for word in ["歩かない", "歩く", "立つ"]):
            return "運動発達についてのご相談ですね"
        elif any(word in message_lower for word in ["成長", "発達"]):
            return "お子さんの成長・発達についてのご相談ですね"
        elif any(word in message_lower for word in ["這う", "座る", "寝返り"]):
            return "運動機能の発達についてのご相談ですね"
        else:
            return "お子さんの発達についてのご相談ですね"

    def _get_health_reason(self, message_lower: str) -> str:
        """健康管理専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["熱", "発熱", "高熱"]):
            return "発熱についてのご心配ですね"
        elif any(word in message_lower for word in ["咳", "鼻水", "風邪"]):
            return "風邪症状についてのご心配ですね"
        elif any(word in message_lower for word in ["体調", "具合", "調子"]):
            return "体調についてのご心配ですね"
        elif any(word in message_lower for word in ["病院", "受診", "医者"]):
            return "受診についてのご相談ですね"
        elif any(word in message_lower for word in ["予防接種", "ワクチン"]):
            return "予防接種についてのご相談ですね"
        else:
            return "健康管理についてのご相談ですね"

    def _get_behavior_reason(self, message_lower: str) -> str:
        """行動・しつけ専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["イヤイヤ期", "イヤイヤ"]):
            return "イヤイヤ期についてのご相談ですね"
        elif any(word in message_lower for word in ["かんしゃく", "癇癪"]):
            return "かんしゃくについてのご相談ですね"
        elif any(word in message_lower for word in ["しつけ", "叱り方"]):
            return "しつけについてのご相談ですね"
        elif any(word in message_lower for word in ["わがまま", "反抗"]):
            return "お子さんの行動についてのご相談ですね"
        elif any(word in message_lower for word in ["生活習慣", "マナー"]):
            return "生活習慣についてのご相談ですね"
        else:
            return "行動・しつけについてのご相談ですね"

    def _get_play_reason(self, message_lower: str) -> str:
        """遊び・学習専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["遊び", "遊んで"]):
            return "遊びについてのご相談ですね"
        elif any(word in message_lower for word in ["おもちゃ", "玩具"]):
            return "おもちゃについてのご相談ですね"
        elif any(word in message_lower for word in ["知育", "学習"]):
            return "知育・学習についてのご相談ですね"
        elif any(word in message_lower for word in ["絵本", "読み聞かせ"]):
            return "読み聞かせについてのご相談ですね"
        elif any(word in message_lower for word in ["工作", "お絵かき"]):
            return "創作活動についてのご相談ですね"
        else:
            return "遊び・学習についてのご相談ですね"

    def _get_safety_reason(self, message_lower: str) -> str:
        """安全・事故防止専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["事故", "ケガ", "怪我"]):
            return "事故・ケガについてのご心配ですね"
        elif any(word in message_lower for word in ["誤飲", "飲み込む"]):
            return "誤飲についてのご心配ですね"
        elif any(word in message_lower for word in ["転落", "落ちる", "転ぶ"]):
            return "転落事故についてのご心配ですね"
        elif any(word in message_lower for word in ["やけど", "火傷"]):
            return "やけどについてのご心配ですね"
        elif any(word in message_lower for word in ["安全対策", "危険"]):
            return "安全対策についてのご相談ですね"
        else:
            return "安全・事故防止についてのご相談ですね"

    def _get_mental_reason(self, message_lower: str) -> str:
        """心理・メンタルケア専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["ストレス", "疲れ"]):
            return "育児ストレスについてのご相談ですね"
        elif any(word in message_lower for word in ["不安", "心配"]):
            return "育児の不安についてのご相談ですね"
        elif any(word in message_lower for word in ["産後うつ", "産後"]):
            return "産後のメンタルケアについてのご相談ですね"
        elif any(word in message_lower for word in ["気持ち", "メンタル"]):
            return "心のケアについてのご相談ですね"
        else:
            return "メンタルケアについてのご相談ですね"

    def _get_work_reason(self, message_lower: str) -> str:
        """社会復帰・仕事両立専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["仕事復帰", "職場復帰"]):
            return "仕事復帰についてのご相談ですね"
        elif any(word in message_lower for word in ["保育園", "保育所"]):
            return "保育園についてのご相談ですね"
        elif any(word in message_lower for word in ["両立", "仕事と育児"]):
            return "仕事と育児の両立についてのご相談ですね"
        elif any(word in message_lower for word in ["働く", "仕事"]):
            return "働きながらの育児についてのご相談ですね"
        elif any(word in message_lower for word in ["時短", "育休"]):
            return "働き方についてのご相談ですね"
        else:
            return "仕事と育児の両立についてのご相談ですね"

    def _get_special_support_reason(self, message_lower: str) -> str:
        """特別支援・療育専門エージェントへのルーティング理由を生成"""
        if any(word in message_lower for word in ["発達障害", "自閉症", "ADHD"]):
            return "発達障害についてのご相談ですね"
        elif any(word in message_lower for word in ["療育", "訓練"]):
            return "療育についてのご相談ですね"
        elif any(word in message_lower for word in ["特別支援", "支援級"]):
            return "特別支援についてのご相談ですね"
        elif any(word in message_lower for word in ["個別支援", "合理的配慮"]):
            return "支援方法についてのご相談ですね"
        else:
            return "特別支援・療育についてのご相談ですね"

    async def _generate_followup_questions(self, original_message: str, specialist_response: str) -> str:
        """専門家回答に基づくフォローアップクエスチョン生成"""
        try:
            self.logger.info(f"🔍 フォローアップクエスチョン生成開始: 利用可能エージェント={list(self._agents.keys())}")

            if "followup_question_generator" not in self._agents:
                self.logger.warning("⚠️ フォローアップクエスチョン生成エージェントが利用できません")
                # フォールバック: 回答内容に基づく動的質問生成
                return self._generate_dynamic_fallback_questions(original_message, specialist_response)

            # フォローアップクエスチョン生成用のプロンプト作成
            followup_prompt = f"""
以下の専門家のアドバイスに基づいて、親御さんが続けて質問したくなるような具体的で実用的なフォローアップクエスチョンを3つ生成してください。

【元の相談内容】
{original_message}

【専門家からのアドバイス】
{specialist_response}

上記の専門家のアドバイス内容を分析し、「他の親御さんもよく聞かれる」ような自然で具体的な派生質問を3つ提案してください。

例：
- 専門家が離乳食について説明した場合 → 「アレルギーが心配な時はどうすれば？」「食べない日が続く時の対処法は？」「手作りと市販品どちらがいい？」
- 専門家が夜泣きについて説明した場合 → 「何時間くらいで改善しますか？」「昼寝の時間も関係ありますか？」「パパでも同じ方法で大丈夫？」

質問は以下の形式で回答してください：
{{
  "followup_questions": [
    "具体的で実用的な質問1",
    "具体的で実用的な質問2", 
    "具体的で実用的な質問3"
  ]
}}
"""

            runner = self._runners.get("followup_question_generator")
            if not runner:
                return ""

            # セッションを確実に作成
            session_id = "followup_gen"
            user_id = "system"
            await self._ensure_session_exists(user_id, session_id)

            content = Content(role="user", parts=[Part(text=followup_prompt)])

            events = []
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                events.append(event)

            if events and hasattr(events[-1], "content") and events[-1].content:
                followup_response = self._extract_response_text(events[-1].content)

                # JSON形式のレスポンスを解析して質問リストを作成
                return self._format_followup_questions(followup_response)

            return ""

        except Exception as e:
            self.logger.error(f"フォローアップクエスチョン生成エラー: {e}")
            return ""

    def _format_followup_questions(self, followup_response: str) -> str:
        """フォローアップクエスチョンのフォーマット"""
        try:
            import json
            import re

            # JSON部分を抽出
            json_match = re.search(r"\{.*?\}", followup_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                questions = data.get("followup_questions", [])
            else:
                # JSON形式でない場合の fallback処理
                lines = followup_response.split("\n")
                questions = []
                for line in lines:
                    line = line.strip()
                    if line and ("？" in line or "?" in line) and len(line) < 50:
                        # 不要な記号を除去
                        clean_question = re.sub(r"^[-•\d\.\)\]\s]*", "", line)
                        questions.append(clean_question)

                questions = questions[:3]  # 最大3つまで

            if not questions:
                return ""

            # 質問を番号付きリストで整形
            formatted_questions = []
            for i, question in enumerate(questions[:3], 1):
                if question.strip():
                    formatted_questions.append(f"💭 {question}")

            if formatted_questions:
                return "\n".join(formatted_questions)

            return ""

        except Exception as e:
            self.logger.error(f"フォローアップクエスチョンフォーマットエラー: {e}")
            # フォールバック: シンプルな質問リスト
            return "💭 具体的なやり方を教えて\n💭 うまくいかない時はどうする？\n💭 注意すべきポイントは？"

    def _generate_dynamic_fallback_questions(self, original_message: str, specialist_response: str) -> str:
        """回答内容に基づく動的フォールバック質問生成"""
        try:
            # 簡単なキーワードベースの質問生成
            message_lower = original_message.lower()
            response_lower = specialist_response.lower()

            questions = []

            # 離乳食関連
            if any(word in message_lower or word in response_lower for word in ["離乳食", "食事", "栄養"]):
                questions = [
                    "アレルギーが心配な時はどうすれば？",
                    "食べない日が続く時の対処法は？",
                    "手作りと市販品どちらがいい？",
                ]
            # 睡眠・夜泣き関連
            elif any(word in message_lower or word in response_lower for word in ["夜泣き", "睡眠", "寝かしつけ"]):
                questions = [
                    "何時間くらいで改善しますか？",
                    "昼寝の時間も関係ありますか？",
                    "パパでも同じ方法で大丈夫？",
                ]
            # 発達関連
            elif any(word in message_lower or word in response_lower for word in ["発達", "成長", "言葉"]):
                questions = [
                    "他の子と比べて遅れていませんか？",
                    "家庭でできることはありますか？",
                    "専門機関に相談するタイミングは？",
                ]
            # 健康関連
            elif any(word in message_lower or word in response_lower for word in ["体調", "健康", "熱", "病気"]):
                questions = ["病院に行く目安はありますか？", "家庭でできる対処法は？", "予防するにはどうすれば？"]
            # 行動・しつけ関連
            elif any(word in message_lower or word in response_lower for word in ["しつけ", "行動", "イヤイヤ"]):
                questions = ["どのくらいの期間続きますか？", "効果的な声かけ方法は？", "やってはいけないことは？"]
            # デフォルト
            else:
                questions = [
                    "他の親御さんはどう対処してますか？",
                    "年齢によって方法は変わりますか？",
                    "注意すべきサインはありますか？",
                ]

            formatted_questions = []
            for question in questions:
                formatted_questions.append(f"💭 {question}")

            return "**【続けて相談したい方へ】**\n" + "\n".join(formatted_questions)

        except Exception as e:
            self.logger.error(f"動的フォールバック質問生成エラー: {e}")
            return "**【続けて相談したい方へ】**\n💭 具体的なやり方を教えて\n💭 うまくいかない時はどうする？\n💭 注意すべきポイントは？"

    def route_query(self, message: str, user_id: str = "default_user", session_id: str = "default_session") -> str:
        """クエリ実行（同期）"""
        return asyncio.run(self.route_query_async(message, user_id, session_id))

    async def route_query_async_with_info(
        self,
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session",
        agent_type: str = "auto",
        conversation_history: list = None,
        family_info: dict = None,
    ) -> dict:
        """ルーティング情報付きマルチエージェント対応クエリ実行（非同期）"""
        routing_path = []
        agent_info = {}

        try:
            # エージェント選択ロジック
            if agent_type == "auto":
                selected_agent_type = self._determine_agent_type(message)
            elif agent_type in ["sequential", "parallel"]:
                selected_agent_type = agent_type
            else:
                selected_agent_type = agent_type

            routing_path.append(
                {
                    "step": "routing_decision",
                    "selected_agent": selected_agent_type,
                    "display_name": AGENT_DISPLAY_NAMES.get(selected_agent_type, selected_agent_type),
                    "timestamp": self._import_time(),
                }
            )

            self.logger.info(f"🎯 選択されたエージェント: {selected_agent_type}")
            self.logger.info(f"🔧 利用可能なRunners: {list(self._runners.keys())}")

            # Runner取得
            if selected_agent_type not in self._runners:
                self.logger.warning(f"⚠️ {selected_agent_type} Runnerが見つかりません。coordinatorを使用")
                selected_agent_type = "coordinator"

            runner = self._runners[selected_agent_type]
            agent_info = {
                "agent_id": selected_agent_type,
                "agent_name": runner.agent.name,
                "display_name": AGENT_DISPLAY_NAMES.get(selected_agent_type, selected_agent_type),
                "model": getattr(runner.agent, "model", "unknown"),
                "has_tools": hasattr(runner.agent, "tools") and runner.agent.tools is not None,
            }

            self.logger.info(f"🚀 実行エージェント: {selected_agent_type} (Agent: {runner.agent.name})")

            # 検索系エージェントの場合の特別ログ
            if selected_agent_type in ["search_specialist", "outing_event_specialist"]:
                self.logger.info(
                    f"🔍 検索系エージェント実行中: {AGENT_DISPLAY_NAMES.get(selected_agent_type, selected_agent_type)}"
                )
                self.logger.info(f"🔍 Web検索ツールを利用してリアルタイム情報を取得します")

            await self._ensure_session_exists(user_id, session_id)

            routing_path.append(
                {
                    "step": "agent_execution",
                    "agent": selected_agent_type,
                    "display_name": AGENT_DISPLAY_NAMES.get(selected_agent_type, selected_agent_type),
                    "timestamp": self._import_time(),
                }
            )

            # 履歴と家族情報を含めたメッセージ作成
            enhanced_message = self._create_message_with_context(message, conversation_history, family_info)
            content = Content(role="user", parts=[Part(text=enhanced_message)])

            # ADK実行
            events = []
            tool_used = False
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                events.append(event)

                # ツール使用検出（詳細ログ）
                if hasattr(event, "actions") and event.actions:
                    tool_used = True
                    try:
                        action_count = len(list(event.actions)) if hasattr(event.actions, "__iter__") else 1
                        self.logger.info(f"🔧 {selected_agent_type} ツール実行検出: {action_count}個のアクション")

                        # アクション詳細をログ出力
                        for i, action in enumerate(event.actions):
                            self.logger.info(f"📋 アクション#{i + 1}: {type(action).__name__}")
                            self.logger.info(f"📄 アクション内容: {str(action)[:500]}...")
                    except Exception as e:
                        self.logger.info(f"🔧 ツール実行検出: アクションあり (詳細取得エラー: {e})")

                # レスポンス内容の詳細ログ
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts") and event.content.parts:
                        for i, part in enumerate(event.content.parts):
                            if hasattr(part, "function_response"):
                                self.logger.info(f"🔧 ツールレスポンス#{i + 1}: {str(part.function_response)[:500]}...")
                            elif hasattr(part, "text") and len(str(part.text)) > 0:
                                self.logger.info(f"💬 {selected_agent_type} 文章#{i + 1}: {str(part.text)[:200]}...")

            self.logger.info(
                f"🔧 {selected_agent_type} ツール使用結果: {'使用された' if tool_used else '使用されなかった'}"
            )

            # レスポンス抽出
            if events and hasattr(events[-1], "content") and events[-1].content:
                response = self._extract_response_text(events[-1].content)

                # コーディネーターの回答を分析して、専門家への紹介があるかチェック
                if selected_agent_type == "coordinator":
                    specialist_response = await self._check_and_route_to_specialist(
                        message, response, user_id, session_id, conversation_history, family_info
                    )
                    if specialist_response:
                        # 専門家ルーティング情報を追加
                        specialist_agent_id = self._determine_specialist_from_message(message)
                        routing_path.append(
                            {
                                "step": "specialist_routing",
                                "agent": specialist_agent_id,
                                "display_name": AGENT_DISPLAY_NAMES.get(specialist_agent_id, "専門家"),
                                "timestamp": self._import_time(),
                            }
                        )

                        # フォローアップクエスチョンを生成
                        self.logger.info("🎯 コーディネーター経由: フォローアップクエスチョン生成を開始します")
                        followup_questions = await self._generate_followup_questions(message, specialist_response)
                        self.logger.info(
                            f"🎯 コーディネーター経由: フォローアップクエスチョン生成結果: 長さ={len(followup_questions)}"
                        )

                        # 専門家回答を直接使用（ルーティング案内は削除）
                        combined_response = specialist_response

                        if followup_questions:
                            combined_response += f"\n\n{followup_questions}"
                            self.logger.info("🎯 フォローアップクエスチョンをレスポンスに追加しました")
                        else:
                            self.logger.warning("⚠️ フォローアップクエスチョンが空でした")
                            # 強制的にフォールバックを追加
                            combined_response += "\n\n**【続けて相談したい方へ】**\n💭 具体的なやり方を教えて\n💭 うまくいかない時はどうする？\n💭 注意すべきポイントは？"

                        return {"response": combined_response, "agent_info": agent_info, "routing_path": routing_path}

                # 専門家の直接回答の場合もフォローアップクエスチョンを追加
                if selected_agent_type != "coordinator" and selected_agent_type not in ["sequential", "parallel"]:
                    followup_questions = await self._generate_followup_questions(message, response)
                    if followup_questions:
                        response = f"{response}\n\n**【続けて相談したい方へ】**\n{followup_questions}"

                return {"response": response, "agent_info": agent_info, "routing_path": routing_path}
            else:
                raise Exception("No response from agent")

        except Exception as e:
            self.logger.error(f"エージェント実行エラー: {e}")
            return {
                "response": f"申し訳ございません。システムエラーが発生しました: {str(e)}",
                "agent_info": agent_info,
                "routing_path": routing_path,
            }

    def _determine_specialist_from_message(self, message: str) -> str:
        """メッセージから専門家IDを判定"""
        message_lower = message.lower()

        # 各専門エージェントのキーワードマッチング
        for agent_id, keywords in AGENT_KEYWORDS.items():
            if any(keyword in message_lower for keyword in keywords):
                return agent_id

        return "nutrition_specialist"  # デフォルト

    async def _ensure_session_exists(self, user_id: str, session_id: str) -> None:
        """セッション存在確認・作成"""
        try:
            await self._session_service.get_session(self._app_name, user_id, session_id)
        except Exception:
            await self._session_service.create_session(app_name=self._app_name, user_id=user_id, session_id=session_id)

    def _import_time(self):
        """時間インポート（循環インポート回避）"""
        import time

        return time.time()

    def _create_message_with_context(
        self, message: str, conversation_history: list = None, family_info: dict = None
    ) -> str:
        """会話履歴と家族情報を含めたメッセージを作成"""
        context_parts = []

        # 家族情報セクション
        if family_info:
            self.logger.info(f"🏠 家族情報をプロンプトに含めます: {family_info}")
            # 現在の日付を含める
            from datetime import date

            today = date.today()
            family_text = f"【家族情報】（本日: {today.strftime('%Y年%m月%d日')}）\n"

            # 子どもの情報
            children = family_info.get("children", [])
            if children:
                family_text += "お子さん:\n"
                for child in children:
                    child_info = []
                    if child.get("name"):
                        child_info.append(f"お名前: {child['name']}")

                    # 年齢を正確に計算
                    if child.get("birth_date"):
                        try:
                            from datetime import datetime, date

                            birth_date = datetime.strptime(child["birth_date"], "%Y-%m-%d").date()
                            today = date.today()

                            # 年齢計算
                            years = today.year - birth_date.year
                            months = today.month - birth_date.month
                            days = today.day - birth_date.day

                            # 誕生日がまだ来ていない場合の調整
                            if months < 0 or (months == 0 and days < 0):
                                years -= 1
                                months += 12
                            if days < 0:
                                months -= 1
                                # 前月の日数を取得して調整
                                import calendar

                                prev_month = today.month - 1 if today.month > 1 else 12
                                prev_year = today.year if today.month > 1 else today.year - 1
                                days_in_prev_month = calendar.monthrange(prev_year, prev_month)[1]
                                days += days_in_prev_month

                            # 年齢表示の生成
                            if years > 0:
                                if months > 0:
                                    age_str = f"{years}歳{months}ヶ月"
                                else:
                                    age_str = f"{years}歳"
                            else:
                                if months > 0:
                                    age_str = f"{months}ヶ月"
                                else:
                                    age_str = f"{days}日"

                            child_info.append(f"年齢: {age_str}")
                            child_info.append(f"生年月日: {child['birth_date']}")

                        except (ValueError, KeyError) as e:
                            # 日付解析に失敗した場合は元の値を使用
                            if child.get("age"):
                                child_info.append(f"年齢: {child['age']}")
                            child_info.append(f"生年月日: {child['birth_date']}")
                    elif child.get("age"):
                        child_info.append(f"年齢: {child['age']}")

                    if child.get("gender"):
                        child_info.append(f"性別: {child['gender']}")
                    if child.get("characteristics"):
                        child_info.append(f"特徴: {child['characteristics']}")
                    if child.get("allergies"):
                        child_info.append(f"アレルギー: {child['allergies']}")
                    if child.get("medical_notes"):
                        child_info.append(f"健康メモ: {child['medical_notes']}")

                    if child_info:
                        family_text += f"  - {', '.join(child_info)}\n"

            # 保護者情報
            if family_info.get("parent_name"):
                family_text += f"保護者: {family_info['parent_name']}\n"
            if family_info.get("family_structure"):
                family_text += f"家族構成: {family_info['family_structure']}\n"
            if family_info.get("concerns"):
                family_text += f"主な心配事: {family_info['concerns']}\n"

            context_parts.append(family_text)

        # 会話履歴セクション
        if conversation_history and len(conversation_history) > 0:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history

            history_text = "【会話履歴】\n"
            for hist in recent_history:
                sender = hist.get("sender", "unknown")
                content = hist.get("content", "")
                if sender == "user":
                    history_text += f"親御さん: {content}\n"
                elif sender == "assistant":
                    history_text += f"アドバイザー: {content}\n"

            context_parts.append(history_text)

        # 現在のメッセージ
        current_message = f"【現在のメッセージ】\n親御さん: {message}\n"
        context_parts.append(current_message)

        # 指示文
        if context_parts[:-1]:  # 家族情報や履歴がある場合
            # 保護者名による個別挨拶の促進
            greeting_instruction = ""
            if family_info and family_info.get("parent_name"):
                parent_name = family_info["parent_name"]
                greeting_instruction = (
                    f"\n\n**重要**: 回答の冒頭で必ず「こんにちは！{parent_name}さん！」と親しみやすく挨拶してください。"
                )

            instruction = f"\n上記の家族情報と会話履歴を踏まえて、お子さんの個性や状況に合わせた個別的なアドバイスを提供してください。家族の状況を理解した上で、親御さんの現在のメッセージに温かく回答してください。{greeting_instruction}"
            context_parts.append(instruction)

        enhanced_message = "\n".join(context_parts)

        context_info = []
        if family_info:
            children_count = len(family_info.get("children", []))
            context_info.append(f"家族情報(子{children_count}人)")
        if conversation_history:
            context_info.append(f"履歴{len(conversation_history)}件")

        self.logger.info(
            f"📚 コンテキスト付きメッセージ作成: {', '.join(context_info) if context_info else '基本メッセージ'}"
        )
        return enhanced_message

    def _extract_response_text(self, response_content) -> str:
        """レスポンステキスト抽出"""
        if hasattr(response_content, "parts") and response_content.parts:
            response_text = ""
            for part in response_content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text
            return response_text
        elif isinstance(response_content, str):
            return response_content
        else:
            return str(response_content)

    # ========== 互換性メソッド ==========

    @property
    def _runner(self) -> Runner:
        """互換性のための_runner属性（coordinatorのRunnerを返す）"""
        if "coordinator" in self._runners:
            return self._runners["coordinator"]
        elif self._runners:
            # coordinatorがない場合は最初のRunnerを返す
            return list(self._runners.values())[0]
        else:
            raise RuntimeError("Runnerが初期化されていません")

    def get_all_agents(self) -> dict[str, Agent]:
        """全エージェント取得"""
        return self._agents.copy()

    def get_agent_info(self) -> dict[str, dict[str, str]]:
        """18専門エージェント情報取得"""
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
                "display_name": "Sequential18専門家パイプライン",
                "model": "pipeline",
                "sub_agents_count": len(self._sequential_agent.sub_agents),
                "type": "sequential",
                "has_tools": False,
                "keywords_count": 0,
            }

        if self._parallel_agent:
            info["parallel_pipeline"] = {
                "name": self._parallel_agent.name,
                "display_name": "Parallel18専門家パイプライン",
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

    # ========== 監視・検証メソッド ==========

    def _log_routing_decision(self, message: str, selected_agent: str, routing_type: str) -> None:
        """ルーティング決定の詳細ログ"""
        message_preview = message[:50] + "..." if len(message) > 50 else message
        agent_display = AGENT_DISPLAY_NAMES.get(selected_agent, selected_agent)

        self.logger.info(
            f"📋 ルーティング詳細 - タイプ: {routing_type}, 選択: {agent_display}, メッセージ: '{message_preview}'"
        )

    def _validate_routing_decision(self, message: str, selected_agent: str) -> bool:
        """ルーティング決定の妥当性検証"""
        message_lower = message.lower()

        # 明らかに不適切なルーティングを検出
        inappropriate_routing = {
            "sleep_specialist": ["食事", "離乳食", "栄養", "食べない"],
            "nutrition_specialist": ["夜泣き", "寝ない", "睡眠", "寝かしつけ"],
            "health_specialist": ["遊び", "おもちゃ", "知育"],
            "play_learning_specialist": ["熱", "病気", "体調不良"],
        }

        if selected_agent in inappropriate_routing:
            inappropriate_keywords = inappropriate_routing[selected_agent]
            if any(keyword in message_lower for keyword in inappropriate_keywords):
                matched = [kw for kw in inappropriate_keywords if kw in message_lower]
                self.logger.warning(f"⚠️ 不適切ルーティング検出: {selected_agent} に {matched} が含まれる")
                return False

        return True

    def _auto_correct_routing(self, message: str, original_agent: str) -> str:
        """自動ルーティング修正"""
        message_lower = message.lower()

        # 強制ルーティングをまず確認
        force_agent = self._check_force_routing(message_lower)
        if force_agent:
            return force_agent

        # 決定論的再ルーティング
        corrected_agent = self._determine_specialist_agent(message_lower)
        if corrected_agent and corrected_agent != "coordinator":
            return "coordinator"  # コーディネーター経由

        # フォールバック
        return "coordinator"
