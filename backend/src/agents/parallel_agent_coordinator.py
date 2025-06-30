"""シンプルなADKネイティブParallelAgent実装

ADK標準のParallelAgentを使用したシンプルな並列処理

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from google.adk.agents import ParallelAgent
from google.adk.runners import Runner
from google.genai import types
from src.agents.agent_manager import AgentManager


@dataclass
class ParallelAgentRequest:
    """パラレルエージェント処理リクエスト"""

    user_message: str
    selected_agents: list[str]
    user_id: str
    session_id: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """個別エージェントレスポンス"""

    agent_id: str
    agent_name: str
    response: str
    processing_time: float
    success: bool
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "response": self.response,
            "processing_time": self.processing_time,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class ParallelAgentResponse:
    """シンプルなパラレルエージェントレスポンス"""

    agents_responses: dict[str, str]
    agent_details: list[AgentResponse]
    processing_time: float
    success: bool
    error_message: str | None = None


class ParallelAgentCoordinator:
    """ADKネイティブParallelAgentを使用したシンプルな並列実行"""

    def __init__(self, agent_manager: AgentManager, logger: logging.Logger):
        """シンプルパラレルエージェントコーディネーター初期化

        Args:
            agent_manager: エージェント管理システム
            logger: DIコンテナから注入されるロガー
        """
        self.agent_manager = agent_manager
        self.logger = logger
        self.max_parallel_agents = 3
        self.timeout_seconds = 15.0  # タイムアウトを15秒に短縮

    async def execute_parallel_analysis(self, request: ParallelAgentRequest) -> ParallelAgentResponse:
        """シンプルなパラレル分析実行

        Args:
            request: パラレル処理リクエスト

        Returns:
            ParallelAgentResponse: 各エージェントの独立レスポンス
        """
        start_time = time.time()

        try:
            # 1. リクエスト検証
            await self._validate_request(request)

            # 2. 個別並列実行（SimpleParallelAgentスタイル）
            agent_responses = await self._execute_individual_parallel(request)

            processing_time = time.time() - start_time

            return ParallelAgentResponse(
                agents_responses={resp.agent_id: resp.response for resp in agent_responses if resp.success},
                agent_details=agent_responses,
                processing_time=processing_time,
                success=True,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"パラレル分析実行エラー: {e}")

            return ParallelAgentResponse(
                agents_responses={},
                agent_details=[],
                processing_time=processing_time,
                success=False,
                error_message=str(e),
            )

    async def _validate_request(self, request: ParallelAgentRequest) -> None:
        """リクエスト検証

        Args:
            request: 検証対象リクエスト

        Raises:
            ValueError: バリデーションエラー時
        """
        if not request.user_message.strip():
            raise ValueError("ユーザーメッセージが空です")

        if not request.selected_agents:
            raise ValueError("選択エージェントが指定されていません")

        if len(request.selected_agents) > self.max_parallel_agents:
            raise ValueError(f"並列実行可能エージェント数は最大{self.max_parallel_agents}個です")

        if not request.user_id.strip():
            raise ValueError("ユーザーIDが空です")

        if not request.session_id.strip():
            raise ValueError("セッションIDが空です")

        # エージェント存在確認
        available_agents = self.agent_manager._registry.get_agent_info()
        for agent_id in request.selected_agents:
            if agent_id not in available_agents:
                raise ValueError(f"エージェント '{agent_id}' は利用できません")

        self.logger.info(
            f"リクエスト検証完了: agents={request.selected_agents}, "
            f"user={request.user_id}, session={request.session_id}"
        )

    async def _execute_parallel_processing(self, request: ParallelAgentRequest) -> list[AgentResponse]:
        """並列処理実行

        Args:
            request: 並列処理リクエスト

        Returns:
            list[AgentResponse]: 各エージェントの実行結果
        """
        self.logger.info(f"並列処理開始: {len(request.selected_agents)}エージェント")

        # 🔧 一時的にADK標準パラレル処理を無効化して個別実行を使用
        # ADK標準パラレル処理で同一回答が生成される問題のため、
        # より確実な個別エージェント実行方式を使用する
        self.logger.info("🔧 個別エージェント実行モードを使用（ADK標準パラレル処理回避）")
        return await self._execute_individual_parallel(request)

    async def _execute_individual_parallel(self, request: ParallelAgentRequest) -> list[AgentResponse]:
        """個別並列処理実行（フォールバック）

        Args:
            request: 並列処理リクエスト

        Returns:
            list[AgentResponse]: 各エージェントの実行結果
        """
        # 並列処理タスク作成
        tasks = []
        for agent_id in request.selected_agents:
            task = self._execute_single_agent(
                agent_id=agent_id,
                message=request.user_message,
                user_id=request.user_id,
                session_id=request.session_id,
                context=request.context,
            )
            tasks.append(task)

        # 並列実行（タイムアウト付き）
        try:
            agent_responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True), timeout=self.timeout_seconds
            )

            # 例外処理
            results = []
            for i, response in enumerate(agent_responses):
                if isinstance(response, Exception):
                    agent_id = request.selected_agents[i]
                    self.logger.error(f"エージェント {agent_id} 実行エラー: {response}")
                    results.append(
                        AgentResponse(
                            agent_id=agent_id,
                            agent_name=agent_id,
                            response="",
                            processing_time=0.0,
                            success=False,
                            error_message=str(response),
                        )
                    )
                else:
                    results.append(response)

            self.logger.info(f"並列処理完了: {len(results)}件")
            return results

        except asyncio.TimeoutError:
            self.logger.warning(f"並列処理タイムアウト: {self.timeout_seconds}秒")
            # タイムアウト時のフォールバック応答
            return [
                AgentResponse(
                    agent_id=agent_id,
                    agent_name=agent_id,
                    response="処理時間が長すぎるため、回答を生成できませんでした。",
                    processing_time=self.timeout_seconds,
                    success=False,
                    error_message="タイムアウト",
                )
                for agent_id in request.selected_agents
            ]

    async def _execute_single_agent(
        self,
        agent_id: str,
        message: str,
        user_id: str,
        session_id: str,
        context: dict[str, Any],
    ) -> AgentResponse:
        """単一エージェント実行

        Args:
            agent_id: エージェントID
            message: ユーザーメッセージ
            user_id: ユーザーID
            session_id: セッションID
            context: コンテキスト情報

        Returns:
            AgentResponse: エージェント実行結果
        """
        start_time = time.time()

        try:
            # より安全なエージェント実行方式を使用
            self.logger.debug(f"🚀 個別エージェント実行開始: {agent_id}")

            # 専門分野に特化したメッセージ作成
            specialized_message = self._create_specialized_message(agent_id, message, context)

            # AgentManagerの既存のroute_query_asyncメソッドを使用
            try:
                # AgentManagerの標準ルーティング機能を使用（セッション問題を回避）
                response = await self.agent_manager.route_query_async(
                    message=specialized_message,
                    user_id=user_id,
                    session_id=f"{session_id}_{agent_id}",  # エージェント固有のセッションID
                    agent_type=agent_id,  # 特定エージェントを指定
                )

                self.logger.debug(f"✅ {agent_id} 実行成功: {len(response)}文字")

                processing_time = time.time() - start_time

                # エージェント情報取得
                agent_info = self.agent_manager._registry.get_agent_info()
                agent_display_name = agent_info.get(agent_id, {}).get("display_name", agent_id)

                self.logger.debug(f"✅ {agent_id} 実行完了: {len(response)}文字 (時間: {processing_time:.2f}s)")

                return AgentResponse(
                    agent_id=agent_id,
                    agent_name=agent_display_name,
                    response=response,
                    processing_time=processing_time,
                    success=True,
                )

            except Exception as route_error:
                processing_time = time.time() - start_time
                self.logger.error(f"❌ {agent_id} ルーティング実行エラー: {route_error}")

                # エージェント情報取得
                agent_info = self.agent_manager._registry.get_agent_info()
                agent_display_name = agent_info.get(agent_id, {}).get("display_name", agent_id)

                return AgentResponse(
                    agent_id=agent_id,
                    agent_name=agent_display_name,
                    response="",
                    processing_time=processing_time,
                    success=False,
                    error_message=f"ルーティング実行エラー: {route_error}",
                )

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"エージェント {agent_id} 実行エラー: {e}")

            return AgentResponse(
                agent_id=agent_id,
                agent_name=agent_id,
                response="",
                processing_time=processing_time,
                success=False,
                error_message=str(e),
            )

    def _create_specialized_message(self, agent_id: str, original_message: str, context: dict[str, Any]) -> str:
        """専門分野に特化したメッセージ作成

        Args:
            agent_id: エージェントID
            original_message: 元のメッセージ
            context: コンテキスト情報

        Returns:
            str: 専門化されたメッセージ
        """
        # 強化されたエージェント固有の専門指示
        agent_specializations = {
            "nutrition_specialist": {
                "role": "栄養・食事の専門家として",
                "focus": "食事、栄養、離乳食、食べムラ、偏食、授乳、栄養バランス、食材、調理法",
                "instruction": "あなたは栄養・食事の専門家です。食事・栄養の観点からのみアドバイスをしてください。睡眠や発達については触れず、食事と栄養に特化した回答をお願いします。",
            },
            "sleep_specialist": {
                "role": "睡眠の専門家として",
                "focus": "睡眠、夜泣き、寝かしつけ、生活リズム、お昼寝、睡眠環境、ねんトレ",
                "instruction": "あなたは睡眠の専門家です。睡眠・休息の観点からのみアドバイスをしてください。食事や発達については触れず、睡眠に特化した回答をお願いします。",
            },
            "development_specialist": {
                "role": "発達支援の専門家として",
                "focus": "発達、成長、マイルストーン、言語発達、運動発達、認知発達、月齢別発達段階",
                "instruction": "あなたは発達支援の専門家です。発達・成長の観点からのみアドバイスをしてください。食事や睡眠については触れず、発達支援に特化した回答をお願いします。",
            },
            "health_specialist": {
                "role": "健康管理の専門家として",
                "focus": "健康、病気、症状、医療機関受診、予防接種、健診、体調管理",
                "instruction": "あなたは健康管理の専門家です。健康・医療の観点からのみアドバイスをしてください。食事や睡眠については触れず、健康管理に特化した回答をお願いします。",
            },
            "behavior_specialist": {
                "role": "行動・しつけの専門家として",
                "focus": "行動、しつけ、習慣形成、ルール、態度、社会性、コミュニケーション",
                "instruction": "あなたは行動・しつけの専門家です。行動・しつけの観点からのみアドバイスをしてください。食事や睡眠については触れず、行動指導に特化した回答をお願いします。",
            },
            "play_learning_specialist": {
                "role": "遊び・学習の専門家として",
                "focus": "遊び、学習、知育、おもちゃ、絵本、創造性、想像力、学習環境",
                "instruction": "あなたは遊び・学習の専門家です。遊び・学習の観点からのみアドバイスをしてください。食事や睡眠については触れず、遊びと学習に特化した回答をお願いします。",
            },
            "safety_specialist": {
                "role": "安全・事故防止の専門家として",
                "focus": "安全、事故防止、危険回避、安全対策、家庭内安全、外出時安全",
                "instruction": "あなたは安全・事故防止の専門家です。安全・事故防止の観点からのみアドバイスをしてください。食事や睡眠については触れず、安全対策に特化した回答をお願いします。",
            },
            "work_life_specialist": {
                "role": "仕事両立の専門家として",
                "focus": "仕事と育児の両立、時間管理、保育園、働くママ・パパ支援、スケジュール調整",
                "instruction": "あなたは仕事両立の専門家です。仕事と育児の両立の観点からのみアドバイスをしてください。食事や睡眠については触れず、両立支援に特化した回答をお願いします。",
            },
            "mental_care_specialist": {
                "role": "メンタルケアの専門家として",
                "focus": "メンタルケア、ストレス解消、心理的サポート、育児不安、親の心理状態",
                "instruction": "あなたはメンタルケアの専門家です。心理・メンタルケアの観点からのみアドバイスをしてください。食事や睡眠については触れず、メンタルサポートに特化した回答をお願いします。",
            },
            "search_specialist": {
                "role": "情報検索の専門家として",
                "focus": "情報検索、最新情報、地域情報、サービス案内、調査結果",
                "instruction": "あなたは情報検索の専門家です。情報検索・調査の観点からのみアドバイスをしてください。他の専門分野については触れず、情報収集と検索に特化した回答をお願いします。",
            },
        }

        specialization = agent_specializations.get(
            agent_id,
            {
                "role": "専門的な観点から",
                "focus": "専門分野",
                "instruction": "専門的な観点からアドバイスをしてください。",
            },
        )

        specialized_message = f"""【専門エージェント指示】
{specialization["instruction"]}

【専門分野】{specialization["focus"]}

【相談内容】
{original_message}

重要：他の専門分野（{specialization["focus"]}以外）には触れず、あなたの専門分野に集中してアドバイスしてください。"""

        # コンテキスト情報があれば追加
        if context:
            context_str = "\n\n追加情報:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            specialized_message += context_str

        return specialized_message

    async def _create_dynamic_parallel_agent(self, selected_agent_ids: list[str]) -> ParallelAgent | None:
        """動的パラレルエージェント作成

        Args:
            selected_agent_ids: 選択されたエージェントIDリスト

        Returns:
            ParallelAgent | None: 作成されたパラレルエージェント（失敗時はNone）
        """
        try:
            self.logger.info(f"🔧 動的パラレルエージェント作成開始: {selected_agent_ids}")

            # 選択されたエージェントを取得
            parallel_specialists = []
            agent_registry = self.agent_manager._registry

            for agent_id in selected_agent_ids:
                if agent_id in agent_registry._agents:
                    original_agent = agent_registry._agents[agent_id]

                    # パラレル専用のエージェントコピーを作成
                    parallel_agent = Agent(
                        name=f"{original_agent.name}DynamicParallel",
                        model=original_agent.model,
                        instruction=original_agent.instruction,
                        tools=original_agent.tools,
                    )
                    parallel_specialists.append(parallel_agent)

                    self.logger.debug(f"✅ パラレルエージェント作成: {agent_id} -> {parallel_agent.name}")
                else:
                    self.logger.warning(f"⚠️ エージェント {agent_id} が見つかりません")

            if not parallel_specialists:
                self.logger.error("❌ 有効なエージェントが見つかりませんでした")
                return None

            # 動的パラレルエージェント作成
            dynamic_parallel_agent = ParallelAgent(
                name=f"DynamicParallel{len(parallel_specialists)}Specialists",
                sub_agents=parallel_specialists,
            )

            self.logger.info(
                f"🎯 動的パラレルエージェント作成完了: {dynamic_parallel_agent.name} "
                f"({len(parallel_specialists)}エージェント)"
            )

            return dynamic_parallel_agent

        except Exception as e:
            self.logger.error(f"❌ 動的パラレルエージェント作成エラー: {e}")
            return None

    async def _execute_adk_parallel(
        self, parallel_agent: ParallelAgent, request: ParallelAgentRequest
    ) -> list[AgentResponse]:
        """ADK標準パラレル実行

        Args:
            parallel_agent: パラレルエージェント
            request: リクエスト

        Returns:
            list[AgentResponse]: 実行結果
        """
        start_time = time.time()

        try:
            self.logger.info(f"🚀 ADK標準パラレル実行開始: {parallel_agent.name}")

            # 専門化されたメッセージ作成
            specialized_message = self._create_parallel_message(request)

            # ADKパラレル実行用のRunnerを作成 - 新しいセッションサービスを使用
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService

            # パラレル処理専用のセッションサービスを作成
            session_service = InMemorySessionService()
            parallel_runner = Runner(
                agent=parallel_agent,
                app_name="GenieUs_DynamicParallel",
                session_service=session_service,
            )

            # セッションを明示的に作成
            session = await session_service.create_session(
                app_name="GenieUs_DynamicParallel",
                user_id=request.user_id,
            )
            session_id = session.id

            # ADKパラレル実行 - run_asyncを使用
            # メッセージをContent形式に変換
            content = types.Content(role="user", parts=[types.Part(text=specialized_message)])

            events = []
            async for event in parallel_runner.run_async(
                user_id=request.user_id,
                session_id=session_id,
                new_message=content,
            ):
                events.append(event)
                self.logger.debug(f"📡 ParallelAgent event: {type(event).__name__}")

            processing_time = time.time() - start_time

            # ADKパラレル結果を個別レスポンス形式に変換
            return await self._parse_adk_parallel_response(events, request.selected_agents, processing_time)

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"❌ ADK標準パラレル実行エラー: {e}")

            # フォールバック: エラー応答を生成
            return [
                AgentResponse(
                    agent_id=agent_id,
                    agent_name=agent_id,
                    response=f"パラレル処理中にエラーが発生しました: {str(e)}",
                    confidence_score=0.0,
                    processing_time=processing_time,
                    success=False,
                    error_message=str(e),
                )
                for agent_id in request.selected_agents
            ]

    def _create_parallel_message(self, request: ParallelAgentRequest) -> str:
        """パラレル処理用メッセージ作成

        Args:
            request: パラレル処理リクエスト

        Returns:
            str: パラレル処理用メッセージ
        """
        agent_info = self.agent_manager._registry.get_agent_info()
        selected_names = []

        for agent_id in request.selected_agents:
            if agent_id in agent_info:
                display_name = agent_info[agent_id].get("display_name", agent_id)
                selected_names.append(display_name)

        specialists_text = "、".join(selected_names)

        parallel_message = f"""複数の専門家による協働分析をお願いします。

【選択された専門家】
{specialists_text}

【相談内容】
{request.user_message}

【指示】
各専門家は自分の専門分野の観点から、独立して分析・回答してください。
他の専門家の回答は考慮せず、あなたの専門知識に基づいた具体的で実用的なアドバイスを提供してください。"""

        # コンテキスト情報があれば追加
        if request.context:
            context_str = "\n\n【追加情報】\n"
            for key, value in request.context.items():
                context_str += f"- {key}: {value}\n"
            parallel_message += context_str

        return parallel_message

    async def _parse_adk_parallel_response(
        self, events: list, selected_agents: list[str], processing_time: float
    ) -> list[AgentResponse]:
        """ADKパラレル結果の解析

        Args:
            events: ADKからのイベントリスト
            selected_agents: 選択されたエージェント
            processing_time: 処理時間

        Returns:
            list[AgentResponse]: 解析結果
        """
        try:
            self.logger.info(f"🔍 ADKパラレル結果解析開始: {len(events)}個のイベント")

            responses = []
            agent_info = self.agent_manager._registry.get_agent_info()

            # 全イベントから最終的なレスポンスを抽出
            final_response = ""
            for event in events:
                if hasattr(event, "message") and event.message:
                    # メッセージからテキスト内容を抽出
                    if hasattr(event.message, "parts"):
                        for part in event.message.parts:
                            if hasattr(part, "text") and part.text:
                                final_response += part.text + "\n"
                    else:
                        final_response += str(event.message) + "\n"
                elif hasattr(event, "content"):
                    # Contentからテキスト内容を抽出
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                final_response += part.text + "\n"
                    else:
                        final_response += str(event.content) + "\n"

            # レスポンスが空の場合は、イベント情報から構築
            if not final_response.strip() and events:
                final_response = (
                    f"複数エージェントが並列で処理を完了しました。{len(events)}個のイベントが生成されました。"
                )

            # 各エージェントに対して結果を作成
            for agent_id in selected_agents:
                display_name = agent_info.get(agent_id, {}).get("display_name", agent_id)

                responses.append(
                    AgentResponse(
                        agent_id=agent_id,
                        agent_name=display_name,
                        response=final_response.strip(),
                        processing_time=processing_time / len(selected_agents),
                        success=True,
                    )
                )

            self.logger.info(f"📊 ADKパラレル結果解析完了: {len(responses)}件")
            return responses

        except Exception as e:
            self.logger.error(f"❌ ADKパラレル結果解析エラー: {e}")

            # フォールバック応答
            return [
                AgentResponse(
                    agent_id=agent_id,
                    agent_name=agent_id,
                    response="パラレル結果の解析中にエラーが発生しました。",
                    processing_time=processing_time,
                    success=False,
                    error_message=str(e),
                )
                for agent_id in selected_agents
            ]

    async def _integrate_responses(self, agent_responses: list[AgentResponse], original_message: str) -> str:
        """複数エージェントの回答統合

        Args:
            agent_responses: エージェントレスポンスリスト
            original_message: 元のユーザーメッセージ

        Returns:
            str: 統合された回答
        """
        successful_responses = [resp for resp in agent_responses if resp.success and resp.response.strip()]

        if not successful_responses:
            return "申し訳ございません。全てのエージェントで回答を生成できませんでした。"

        # 統合サマリーを生成
        try:
            self.logger.info(f"🔄 統合処理開始: {len(successful_responses)}件のレスポンスを統合")
            summary_prompt = self._create_integration_prompt(successful_responses, original_message)
            self.logger.debug(f"📝 統合プロンプト作成完了: {len(summary_prompt)}文字")

            # coordinatorエージェントで統合処理
            coordinator_runner = self.agent_manager._registry.get_runner("coordinator")
            if not coordinator_runner:
                raise RuntimeError("coordinatorエージェントのRunnerが見つかりません")

            # coordinatorエージェントで統合処理 - セッション作成
            session_service = self.agent_manager._session_service
            if not session_service:
                raise RuntimeError("SessionServiceが見つかりません")

            # 統合処理用の固定セッションIDを使用（新規作成せず、既存セッションサービスを利用）
            integration_user_id = "parallel_integration"
            integration_session_id = "parallel_integration_session"

            # セッションの存在確認と作成
            try:
                existing_session = await session_service.get_session(integration_session_id)
                if not existing_session:
                    integration_session = await session_service.create_session(
                        app_name="GenieUs_Integration",
                        user_id=integration_user_id,
                    )
                    integration_session_id = integration_session.id
                    self.logger.debug(f"📋 新規統合セッション作成: {integration_session_id}")
                else:
                    self.logger.debug(f"📋 既存統合セッション使用: {integration_session_id}")
            except Exception as session_error:
                self.logger.warning(f"⚠️ セッション処理エラー: {session_error}")
                # フォールバック: 新しいセッションを作成
                integration_session = await session_service.create_session(
                    app_name="GenieUs_Integration",
                    user_id=integration_user_id,
                )
                integration_session_id = integration_session.id
                self.logger.debug(f"📋 フォールバック統合セッション作成: {integration_session_id}")

            # メッセージをContent形式に変換
            content = types.Content(role="user", parts=[types.Part(text=summary_prompt)])

            events = []
            async for event in coordinator_runner.run_async(
                user_id="parallel_integration",
                session_id=integration_session_id,
                new_message=content,
            ):
                events.append(event)

            # 統合結果を取得
            integrated_summary = ""
            self.logger.debug(f"📡 統合処理イベント数: {len(events)}")

            for i, event in enumerate(events):
                self.logger.debug(f"🔍 イベント{i}: {type(event).__name__}")

                if hasattr(event, "message") and event.message:
                    # メッセージからテキスト内容を抽出
                    if hasattr(event.message, "parts"):
                        for part in event.message.parts:
                            if hasattr(part, "text") and part.text:
                                integrated_summary += part.text
                                self.logger.debug(f"📝 メッセージテキスト追加: {len(part.text)}文字")
                    else:
                        integrated_summary += str(event.message)
                        self.logger.debug(f"📝 メッセージ追加: {len(str(event.message))}文字")
                elif hasattr(event, "content"):
                    # Contentからテキスト内容を抽出
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                integrated_summary += part.text
                                self.logger.debug(f"📝 コンテンツテキスト追加: {len(part.text)}文字")
                    else:
                        integrated_summary += str(event.content)
                        self.logger.debug(f"📝 コンテンツ追加: {len(str(event.content))}文字")

            self.logger.debug(f"📋 統合結果: {len(integrated_summary)}文字")

            if not integrated_summary and events:
                # フォールバック: 簡易統合
                integrated_summary = "複数の専門家からの回答を統合しました。"
                self.logger.warning("⚠️ 統合結果が空のため、フォールバック処理を実行")

            self.logger.info(f"✅ 回答統合完了: {len(successful_responses)}件のレスポンスを統合")
            return integrated_summary

        except Exception as e:
            self.logger.error(f"回答統合エラー: {e}")

            # フォールバック: 簡潔な要約統合
            try:
                fallback_summary = "## 🌟 複数専門家による総合アドバイス\n\n"

                # 各専門家の要点を要約
                for i, resp in enumerate(successful_responses, 1):
                    summary = self._summarize_response(resp.agent_name, resp.response)
                    fallback_summary += f"**{resp.agent_name}**: {summary[:150]}...\n\n"

                fallback_summary += "\n各専門家のアドバイスを参考に、お子さんに最適な方法を見つけてくださいね。"

                return fallback_summary
            except Exception as fallback_error:
                self.logger.error(f"フォールバック統合エラー: {fallback_error}")
                return (
                    "複数の専門家からアドバイスをいただきました。お子さんの状況に合わせて、最適な方法をお試しください。"
                )

    def _create_integration_prompt(self, responses: list[AgentResponse], original_message: str) -> str:
        """統合プロンプト作成

        Args:
            responses: 成功したエージェントレスポンス
            original_message: 元のユーザーメッセージ

        Returns:
            str: 統合用プロンプト
        """
        # 各エージェントの回答を要約して重複を避ける
        specialist_summaries = []
        for resp in responses:
            # 長い回答は要約
            summary = self._summarize_response(resp.agent_name, resp.response)
            specialist_summaries.append(f"【{resp.agent_name}】{summary}")

        specialists_text = "\n".join(specialist_summaries)

        prompt = f"""以下の複数専門家からの回答を、簡潔で読みやすい統合アドバイスにまとめてください。

【相談内容】
{original_message}

【各専門家の要点】
{specialists_text}

【統合回答の要件】
- 400文字以内の簡潔なサマリー
- 重複を避け、最も重要なポイントのみ抽出
- 実践的で具体的なアドバイス
- 親しみやすい温かい文章

以下の形式で統合回答を作成してください：

## 🌟 複数専門家による総合アドバイス

### 📋 重要ポイント
- [要点1]
- [要点2] 
- [要点3]

### 🎯 実践アドバイス
1. **[対策1]** - [簡潔な説明]
2. **[対策2]** - [簡潔な説明]

### 🤗 応援メッセージ
[短い励ましの言葉]

統合回答："""

        return prompt

    def _summarize_response(self, agent_name: str, response: str) -> str:
        """エージェント回答を要約

        Args:
            agent_name: エージェント名
            response: 元の回答

        Returns:
            str: 要約された回答
        """
        try:
            # 長い回答の場合は重要部分を抽出
            if len(response) > 500:
                # 箇条書きや番号付きリストの部分を優先的に抽出
                import re

                # 重要なポイントを抽出するパターン
                patterns = [
                    r"[0-9]+\.\s*\*\*([^*]+)\*\*[^:]*:?([^1-9\n]+)",  # 番号付きの太字項目
                    r"[•\-]\s*\*\*([^*]+)\*\*[^:]*:?([^•\-\n]+)",  # 箇条書きの太字項目
                    r"[0-9]+\.\s*([^1-9\n]{20,100})",  # 番号付きリスト
                    r"[•\-]\s*([^•\-\n]{20,100})",  # 箇条書き
                ]

                key_points = []
                for pattern in patterns:
                    matches = re.findall(pattern, response)
                    for match in matches[:2]:  # 最大2つまで
                        if isinstance(match, tuple):
                            point = f"{match[0].strip()}: {match[1].strip()}"
                        else:
                            point = match.strip()

                        if len(point) > 10 and point not in key_points:
                            key_points.append(point)

                if key_points:
                    return " / ".join(key_points[:3])  # 最大3つのポイント
                else:
                    # パターンマッチしない場合は先頭部分を使用
                    return response[:200].strip() + "..."
            else:
                return response.strip()

        except Exception as e:
            self.logger.warning(f"⚠️ 回答要約エラー: {e}")
            # エラー時は先頭200文字を返す
            return response[:200].strip() + ("..." if len(response) > 200 else "")

    def get_available_agents_for_parallel(self) -> list[dict[str, Any]]:
        """並列処理に利用可能なエージェント一覧取得

        Returns:
            list[dict]: エージェント情報リスト
        """
        agent_info = self.agent_manager._registry.get_agent_info()

        # 並列処理に適したエージェントを選択
        suitable_agents = []
        excluded_types = {"sequential_pipeline", "parallel_pipeline", "coordinator", "followup_question_generator"}

        for agent_id, info in agent_info.items():
            if agent_id not in excluded_types and info.get("type") == "specialist":
                suitable_agents.append(
                    {
                        "id": agent_id,
                        "name": info.get("display_name", agent_id),
                        "description": self._get_agent_description(agent_id),
                        "has_tools": info.get("has_tools", False),
                        "confidence_rating": self._get_agent_confidence_rating(agent_id),
                    }
                )

        return suitable_agents

    def _get_agent_description(self, agent_id: str) -> str:
        """エージェント説明取得

        Args:
            agent_id: エージェントID

        Returns:
            str: エージェント説明
        """
        descriptions = {
            "nutrition_specialist": "栄養バランス、食事内容、離乳食などの食事に関する専門的なアドバイス",
            "sleep_specialist": "睡眠リズム、夜泣き対策、寝かしつけなどの睡眠に関する専門的なアドバイス",
            "development_specialist": "発達段階、成長マイルストーン、知育などの発達に関する専門的なアドバイス",
            "health_specialist": "健康管理、病気対応、予防接種などの健康に関する専門的なアドバイス",
            "behavior_specialist": "しつけ、問題行動、習慣形成などの行動に関する専門的なアドバイス",
            "play_learning_specialist": "遊び方、学習方法、おもちゃ選びなどの遊び・学習に関する専門的なアドバイス",
            "safety_specialist": "事故防止、安全対策、危険回避などの安全に関する専門的なアドバイス",
            "work_life_specialist": "仕事と育児の両立、時間管理、ストレス対処などの専門的なアドバイス",
            "mental_care_specialist": "親のメンタルケア、ストレス解消、心理的サポートなどの専門的なアドバイス",
            "search_specialist": "情報検索、地域情報、サービス案内などの調査・検索に関する専門的なサポート",
        }
        return descriptions.get(agent_id, "専門的なアドバイス")

    def _get_agent_confidence_rating(self, agent_id: str) -> str:
        """エージェント信頼度評価取得

        Args:
            agent_id: エージェントID

        Returns:
            str: 信頼度評価
        """
        # ツール有無に基づく基本評価
        agent_info = self.agent_manager._registry.get_agent_info()
        has_tools = agent_info.get(agent_id, {}).get("has_tools", False)

        if has_tools:
            return "高"
        else:
            return "中"

    def _generate_parallel_agent_tag(self, processing_time: float) -> str:
        """パラレルエージェント実行タグ生成

        Args:
            processing_time: 実行時間（秒）

        Returns:
            str: フォーマットされたパラレルエージェント実行タグ
        """
        try:
            # 実行時間をフォーマット
            if processing_time < 1.0:
                time_display = f"{processing_time * 1000:.1f}ms"
            else:
                time_display = f"{processing_time:.1f}s"

            # パラレルエージェント専用タグ
            tag = f"**parallel_agents使用{time_display}**"

            self.logger.debug(f"🏷️ パラレルエージェントタグ生成: {tag}")

            return tag

        except Exception as e:
            self.logger.warning(f"⚠️ パラレルエージェントタグ生成エラー: {e}")
            return f"**parallel_agents使用{processing_time:.1f}s**"
