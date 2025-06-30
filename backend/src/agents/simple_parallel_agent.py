"""ADK公式ParallelAgent実装

Google ADK公式のParallelAgentとRunnerを使用した正しい並列処理

ADKプラクティス準拠:
- ParallelAgentでsub_agentsの並列実行
- 共有session.stateで状態管理
- 単一Runnerで全体オーケストレーション

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

from google.adk.agents import Agent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.agents.agent_manager import AgentManager


@dataclass
class SimpleParallelRequest:
    """シンプルパラレル処理リクエスト"""

    user_message: str
    selected_agents: list[str]
    user_id: str
    session_id: str


@dataclass
class SimpleAgentResponse:
    """シンプルエージェントレスポンス"""

    agent_id: str
    agent_name: str
    response: str
    success: bool


@dataclass
class SimpleParallelResponse:
    """シンプルパラレルレスポンス"""

    responses: list[SimpleAgentResponse]
    success: bool
    error_message: str | None = None


class SimpleParallelAgent:
    """ADK公式ParallelAgent実装

    Google ADKのParallelAgentとRunnerを使用した正しい実装
    """

    def __init__(self, agent_manager: AgentManager, logger: logging.Logger):
        """初期化

        Args:
            agent_manager: エージェント管理システム
            logger: DIコンテナから注入されるロガー
        """
        self.agent_manager = agent_manager
        self.logger = logger
        # ADK公式プラクティス: 共有セッションサービス
        self._session_service = InMemorySessionService()

    async def execute_parallel(self, request: SimpleParallelRequest) -> SimpleParallelResponse:
        """ADK公式ParallelAgentでの並列実行

        Args:
            request: パラレル処理リクエスト

        Returns:
            SimpleParallelResponse: 実行結果
        """
        try:
            self.logger.info(f"🚀 ADK公式ParallelAgent実行: {len(request.selected_agents)}エージェント")

            # ADK公式プラクティス: 新しいエージェントインスタンス作成
            agent_registry = self.agent_manager._registry
            all_agents = agent_registry.get_all_agents()

            sub_agents_list = []
            for agent_id in request.selected_agents:
                if agent_id in all_agents:
                    original_agent = all_agents[agent_id]
                    # 新しいエージェントインスタンスを作成（親子関係回避）
                    parallel_agent = Agent(
                        name=f"{original_agent.name}Parallel",
                        model=original_agent.model,
                        instruction=original_agent.instruction,
                        tools=original_agent.tools,
                    )
                    sub_agents_list.append(parallel_agent)
                    self.logger.info(f"✅ 並列エージェント作成: {agent_id} -> {parallel_agent.name}")
                else:
                    self.logger.warning(f"⚠️ エージェントが見つかりません: {agent_id}")

            if not sub_agents_list:
                raise RuntimeError("実行可能なエージェントがありません")

            parallel_agent = ParallelAgent(name="genieus_multi_specialist_parallel_agent", sub_agents=sub_agents_list)

            # ADK公式プラクティス: 単一Runner作成
            runner = Runner(agent=parallel_agent, app_name="ParallelExecution", session_service=self._session_service)

            # セッション作成
            session = await self._session_service.create_session(
                app_name="ParallelExecution",
                user_id=request.user_id,
                state={},  # ADK公式プラクティス: 初期状態
            )

            self.logger.info(f"📋 ADKセッション作成完了: {session.id}")

            # ADK公式プラクティス: メッセージ形式変換
            content = types.Content(role="user", parts=[types.Part(text=request.user_message)])

            # ADK公式プラクティス: ParallelAgent実行
            events = []
            final_response = ""
            async for event in runner.run_async(
                user_id=request.user_id,
                session_id=session.id,
                new_message=content,
            ):
                events.append(event)
                self.logger.info(f"📡 ParallelAgent event: {type(event).__name__}")

                # デバッグログ（簡潔化）
                if hasattr(event, "branch") and event.branch:
                    self.logger.debug(f"📡 Branch: {event.branch}")

                # レスポンス抽出を試行
                if hasattr(event, "message") and event.message:
                    if hasattr(event.message, "parts"):
                        for part in event.message.parts:
                            if hasattr(part, "text") and part.text:
                                final_response += part.text + "\n"

            self.logger.info(f"📡 総イベント数: {len(events)}")
            self.logger.info(f"📡 抽出レスポンス長: {len(final_response)}")

            # 結果抽出とレスポンス作成
            responses = self._extract_parallel_responses(events, request.selected_agents)

            success_count = sum(1 for resp in responses if resp.success)
            self.logger.info(f"✅ ADK公式ParallelAgent実行完了: {success_count}/{len(responses)}件成功")

            return SimpleParallelResponse(responses=responses, success=success_count > 0)

        except Exception as e:
            self.logger.error(f"❌ ADK公式ParallelAgent実行エラー: {e}")
            self.logger.exception("エラースタックトレース:")

            return SimpleParallelResponse(responses=[], success=False, error_message=str(e))

    def _extract_parallel_responses(self, events: list, selected_agents: list[str]) -> list[SimpleAgentResponse]:
        """ParallelAgentからのイベントからレスポンスを抽出

        Args:
            events: ADKからのイベントリスト
            selected_agents: 選択されたエージェントIDリスト

        Returns:
            list[SimpleAgentResponse]: エージェントレスポンスリスト
        """
        responses = []
        agent_info = self.agent_manager._registry.get_agent_info()

        # エージェント名とIDのマッピング作成
        agent_name_mapping = {}
        for agent_id in selected_agents:
            agent_registry = self.agent_manager._registry
            all_agents = agent_registry.get_all_agents()
            if agent_id in all_agents:
                original_agent = all_agents[agent_id]
                parallel_name = f"{original_agent.name}Parallel"
                agent_name_mapping[parallel_name] = agent_id
                self.logger.debug(f"🔗 Agent mapping: {parallel_name} -> {agent_id}")

        # 全てのイベントからテキストを抽出（エージェント特定付き）
        agent_responses = {}

        for i, event in enumerate(events):
            self.logger.debug(f"🔍 Event {i}: type={type(event).__name__}")

            # エージェント特定を試行
            agent_name = None
            if hasattr(event, "branch") and event.branch:
                self.logger.debug(f"🔍 Event {i}: branch={event.branch}")
                agent_name = event.branch
            elif hasattr(event, "agent") and event.agent:
                agent_name = event.agent
            elif hasattr(event, "source") and event.source:
                agent_name = event.source

            # レスポンステキスト抽出
            response_text = None

            # パターン1: message.parts.text
            if hasattr(event, "message") and event.message:
                if hasattr(event.message, "parts"):
                    for j, part in enumerate(event.message.parts):
                        if hasattr(part, "text") and part.text:
                            response_text = part.text.strip()
                            break
                elif hasattr(event.message, "text"):
                    response_text = event.message.text.strip()

            # パターン2: content.parts.text
            elif hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts"):
                    for j, part in enumerate(event.content.parts):
                        if hasattr(part, "text") and part.text:
                            response_text = part.text.strip()
                            break
                elif hasattr(event.content, "text"):
                    response_text = event.content.text.strip()

            # パターン3: 直接text属性
            elif hasattr(event, "text") and event.text:
                response_text = event.text.strip()

            if response_text and agent_name:
                # エージェント名からIDを特定
                agent_id = agent_name_mapping.get(agent_name)
                if agent_id:
                    agent_responses[agent_id] = response_text
                    self.logger.info(f"✅ Event {i}: {agent_id} レスポンス抽出成功 {len(response_text)}文字")
                else:
                    self.logger.warning(f"⚠️ Event {i}: エージェント名 {agent_name} の対応が見つかりません")
            elif response_text:
                self.logger.debug(f"📝 Event {i}: レスポンス抽出済み（エージェント不明）: {len(response_text)}文字")

        self.logger.info(f"📊 特定されたエージェントレスポンス数: {len(agent_responses)}")

        # 順序問題対応: エージェント特定できなかった場合のフォールバック
        if len(agent_responses) < len(selected_agents):
            self.logger.warning("⚠️ エージェント特定不完全、順序ベースフォールバック実行")

            # 全レスポンステキストを再収集
            all_responses = []
            for i, event in enumerate(events):
                response_text = None

                if hasattr(event, "message") and event.message:
                    if hasattr(event.message, "parts"):
                        for part in event.message.parts:
                            if hasattr(part, "text") and part.text:
                                response_text = part.text.strip()
                                break
                    elif hasattr(event.message, "text"):
                        response_text = event.message.text.strip()
                elif hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                response_text = part.text.strip()
                                break
                    elif hasattr(event.content, "text"):
                        response_text = event.content.text.strip()
                elif hasattr(event, "text") and event.text:
                    response_text = event.text.strip()

                if response_text:
                    all_responses.append(response_text)

            # 順序ベース分配（フォールバック）
            for i, agent_id in enumerate(selected_agents):
                if agent_id not in agent_responses and i < len(all_responses):
                    agent_responses[agent_id] = all_responses[i]
                    self.logger.info(f"🔄 フォールバック: {agent_id} レスポンス割り当て完了")

        # 最終レスポンス作成
        for agent_id in selected_agents:
            display_name = agent_info.get(agent_id, {}).get("display_name", agent_id)

            if agent_id in agent_responses and agent_responses[agent_id]:
                response_text = agent_responses[agent_id]

                # エージェント自己紹介の修正
                response_text = self._fix_agent_greeting(response_text, agent_id, display_name)

                responses.append(
                    SimpleAgentResponse(
                        agent_id=agent_id,
                        agent_name=display_name,
                        response=response_text,
                        success=True,
                    )
                )
                self.logger.info(f"✅ {agent_id} 最終レスポンス作成完了: {len(response_text)}文字")
            else:
                self.logger.warning(f"⚠️ {agent_id} レスポンスが空")
                responses.append(
                    SimpleAgentResponse(
                        agent_id=agent_id,
                        agent_name=display_name,
                        response="レスポンスが取得できませんでした。",
                        success=False,
                    )
                )

        return responses

    def _fix_agent_greeting(self, response_text: str, agent_id: str, display_name: str) -> str:
        """エージェント自己紹介の修正

        Args:
            response_text: 元のレスポンステキスト
            agent_id: エージェントID
            display_name: 表示名

        Returns:
            str: 修正されたレスポンステキスト
        """
        try:
            # 正しいエージェント名の定義
            correct_greetings = {
                "sleep_specialist": "睡眠のジーニーです😴",
                "nutrition_specialist": "栄養・食事のジーニーです🍎",
                "development_specialist": "発達支援のジーニーです✨",
            }

            correct_greeting = correct_greetings.get(agent_id)
            if not correct_greeting:
                return response_text

            # 間違った挨拶パターンを検出・修正
            wrong_patterns = ["睡眠のジーニーです😴", "栄養・食事のジーニーです🍎", "発達支援のジーニーです✨"]

            # 正しい挨拶以外を修正
            for wrong_pattern in wrong_patterns:
                if wrong_pattern != correct_greeting and wrong_pattern in response_text:
                    response_text = response_text.replace(wrong_pattern, correct_greeting)
                    self.logger.info(f"🔧 {agent_id}: エージェント挨拶修正 {wrong_pattern} -> {correct_greeting}")
                    break

            return response_text

        except Exception as e:
            self.logger.warning(f"⚠️ エージェント挨拶修正エラー: {e}")
            return response_text

    def _extract_response_from_events(self, events: list) -> str:
        """イベントからレスポンス抽出（レガシー用）

        Args:
            events: ADKからのイベントリスト

        Returns:
            str: 抽出されたレスポンス
        """
        final_response = ""

        for event in events:
            if hasattr(event, "message") and event.message:
                if hasattr(event.message, "parts"):
                    for part in event.message.parts:
                        if hasattr(part, "text") and part.text:
                            final_response += part.text + "\n"
                else:
                    final_response += str(event.message) + "\n"
            elif hasattr(event, "content"):
                if hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            final_response += part.text + "\n"
                else:
                    final_response += str(event.content) + "\n"

        # デフォルトレスポンス
        if not final_response.strip():
            final_response = "複数の専門家による分析が完了しました。"

        return final_response.strip()
