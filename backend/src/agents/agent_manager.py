"""Agent管理クラス - 設定ベース設計による統一管理"""

import asyncio
from typing import Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content

from src.agents.config import AgentConfigPresets
from src.agents.pipelines.comprehensive_consultation_pipeline import (
    create_comprehensive_consultation_pipeline,
    create_emergency_consultation_pipeline,
    get_pipeline_info,
)
from src.di_provider.container import DIContainer


class AgentManager:
    """エージェント一元管理クラス - 設定ベース設計

    設定ベースでエージェントを作成・管理し、柔軟なツール構成を実現
    個別エージェントとマルチエージェントパイプラインの両方を統一管理
    """

    def __init__(self, container: DIContainer):
        self.container = container
        self.logger = container.logger()

        # 設定ベース設計の基盤コンポーネント（DIコンテナから取得）
        self.tool_registry = container.tool_registry()
        self.agent_factory = container.agent_factory()

        # エージェント管理
        self._agents: dict[str, Agent] = {}
        self._pipelines: dict[str, Agent] = {}
        self._runners: dict[str, Runner] = {}
        self._session_service = InMemorySessionService()
        self._app_name = "GenieUs"

    def initialize_all_agents(self) -> None:
        """全エージェントを初期化（設定ベース）"""
        self.logger.info("全エージェント初期化開始（設定ベース設計）")

        try:
            # 設定ベースでエージェント初期化
            self._initialize_core_agents()
            self.logger.info(f"コアエージェント初期化完了: {len(self._agents)}個")

            # パイプライン初期化（frontendは/chatを使うため最初から初期化）
            self._initialize_pipelines()

            self.logger.info(f"初期化完了: {len(self._agents)}個のエージェント, {len(self._pipelines)}個のパイプライン")

        except Exception as e:
            self.logger.error(f"エージェント初期化エラー: {e}")
            raise

    def _initialize_core_agents(self) -> None:
        """コアエージェントを設定ベースで初期化"""

        # エージェント設定定義（プリセット使用）
        agent_configs = {
            "childcare": AgentConfigPresets.standard_childcare(),
            "development": AgentConfigPresets.standard_development(),
            "multimodal": AgentConfigPresets.standard_multimodal(),
            # router は特別なツールが必要なので後で個別処理
        }

        # 各エージェントを設定ベースで作成
        for agent_key, config in agent_configs.items():
            try:
                self.logger.info(f"{agent_key}エージェント初期化開始: {config}")

                # エージェント作成
                agent = self.agent_factory.create_agent(config)
                self._agents[agent_key] = agent

                # Runner作成
                runner = Runner(agent=agent, app_name=self._app_name, session_service=self._session_service)
                self._runners[agent_key] = runner

                self.logger.info(f"{agent_key}エージェント初期化完了: {agent.name}")

            except Exception as e:
                self.logger.error(f"{agent_key}エージェント初期化エラー: {e}")
                raise

        # マルチモーダル統合childcareエージェントを追加作成
        self._initialize_multimodal_childcare_agent()

        # ルーターエージェントは特別処理（ルーティングツールが必要）
        self._initialize_router_agent()

    def _initialize_multimodal_childcare_agent(self) -> None:
        """マルチモーダル統合childcareエージェント初期化"""
        try:
            self.logger.info("マルチモーダル統合childcareエージェント初期化開始")

            # ツールを取得
            childcare_tool = self.tool_registry.get_childcare_consultation_tool()
            file_tool = self.tool_registry.get_file_management_tool()
            image_tool = self.tool_registry.get_image_analysis_tool()
            voice_tool = self.tool_registry.get_voice_analysis_tool()

            # ツール取得状況をログ
            tool_status = {
                "childcare_tool": childcare_tool is not None,
                "file_tool": file_tool is not None,
                "image_tool": image_tool is not None,
                "voice_tool": voice_tool is not None,
            }
            self.logger.info(f"ツール取得状況: {tool_status}")

            # マルチモーダル統合エージェント作成
            from src.agents.individual.childcare_agent import create_childcare_agent_with_tools

            agent = create_childcare_agent_with_tools(
                childcare_tool=childcare_tool,
                file_management_tool=file_tool,
                image_analysis_tool=image_tool,
                voice_analysis_tool=voice_tool,
                logger=self.logger,
            )

            # 既存のchildcareエージェントを置き換え
            self._agents["childcare"] = agent

            # Runner再作成
            runner = Runner(agent=agent, app_name=self._app_name, session_service=self._session_service)
            self._runners["childcare"] = runner

            self.logger.info("マルチモーダル統合childcareエージェント初期化完了")

        except Exception as e:
            self.logger.error(f"マルチモーダル統合childcareエージェント初期化エラー: {e}")
            # エラー時は標準childcareエージェントを使用（フォールバック）
            self.logger.warning("フォールバック: 標準childcareエージェントを使用")
            raise

    def _initialize_router_agent(self) -> None:
        """ルーターエージェント初期化（特別処理）"""
        try:
            # 循環参照を避けるため、ツールを直接作成
            from src.tools.routing_tool import create_routing_tool
            from google.adk.tools import FunctionTool

            routing_function = create_routing_tool(self, self.logger)
            routing_tool = FunctionTool(routing_function)

            # ルーター用設定を取得し、ツールを動的追加
            config = AgentConfigPresets.standard_router()

            # ルーティングツールを一時的にレジストリに登録
            self.tool_registry.register_external_tool("routing", lambda: routing_tool)

            # 設定を更新してルーティングツールを追加
            config.enable_custom_tools = True
            config.custom_tools = ["routing"]

            # エージェント作成
            agent = self.agent_factory.create_agent(config)
            self._agents["router"] = agent

            self.logger.info("ルーターエージェント初期化完了")

        except Exception as e:
            self.logger.error(f"ルーターエージェント初期化エラー: {e}")
            raise

    def get_agent(self, agent_type: str) -> Agent:
        """指定されたタイプのエージェントを取得

        Args:
            agent_type: エージェントタイプ ("childcare", "development", etc.)

        Returns:
            Agent: 要求されたエージェント

        Raises:
            ValueError: 指定されたエージェントが存在しない場合

        """
        if agent_type not in self._agents:
            available = list(self._agents.keys())
            raise ValueError(f"エージェント '{agent_type}' が見つかりません. 利用可能: {available}")

        return self._agents[agent_type]

    def get_all_agents(self) -> dict[str, Agent]:
        """全エージェントを取得"""
        return self._agents.copy()

    def _initialize_pipelines(self) -> None:
        """マルチエージェントパイプラインを初期化（設定ベース）"""
        try:
            self.logger.info("マルチエージェントパイプライン初期化開始（設定ベース）")

            self._pipelines["comprehensive"] = create_comprehensive_consultation_pipeline(
                childcare_agent=self._agents["childcare"],
                development_agent=self._agents["development"],
                logger=self.logger,
            )

            emergency_childcare_agent = self.agent_factory.create_agent(AgentConfigPresets.emergency_childcare())
            emergency_development_agent = self.agent_factory.create_agent(AgentConfigPresets.minimal_development())

            self._pipelines["emergency"] = create_emergency_consultation_pipeline(
                childcare_agent=emergency_childcare_agent,
                development_agent=emergency_development_agent,
                logger=self.logger,
            )

            self.logger.info("マルチエージェントパイプライン初期化完了")

        except Exception as e:
            self.logger.error(f"パイプライン初期化エラー: {e}")
            raise

    def get_pipeline(self, pipeline_name: str) -> Agent:
        """指定されたパイプラインを取得

        Args:
            pipeline_name: パイプライン名 ("comprehensive", "emergency", etc.)

        Returns:
            Agent: 要求されたパイプライン

        Raises:
            ValueError: 指定されたパイプラインが存在しない場合

        """
        if pipeline_name not in self._pipelines:
            available = list(self._pipelines.keys())
            raise ValueError(f"パイプライン '{pipeline_name}' が見つかりません. 利用可能: {available}")

        return self._pipelines[pipeline_name]

    def get_all_pipelines(self) -> dict[str, Agent]:
        """全パイプラインを取得"""
        return self._pipelines.copy()

    def get_pipeline_info(self) -> dict[str, str]:
        """利用可能なパイプライン情報を取得"""
        return get_pipeline_info()

    def get_agent_info(self) -> dict[str, dict[str, str]]:
        """エージェント情報を取得（デバッグ用）"""
        info = {}
        for agent_type, agent in self._agents.items():
            info[agent_type] = {
                "name": agent.name,
                "model": agent.model,
                "tools_count": len(agent.tools) if agent.tools else 0,
            }
        return info

    def get_system_info(self) -> dict[str, any]:
        """システム全体の情報を取得（デバッグ用）"""
        return {
            "individual_agents": {
                "count": len(self._agents),
                "types": list(self._agents.keys()),
            },
            "pipelines": {
                "count": len(self._pipelines),
                "types": list(self._pipelines.keys()),
            },
            "pipeline_descriptions": get_pipeline_info(),
            "tool_registry": {
                "available_tools": self.tool_registry.get_available_tools(),
                "tool_info": self.tool_registry.get_tool_info(),
            },
            "config_presets": {
                "available_presets": AgentConfigPresets.get_preset_names(),
            },
            "architecture": "config_based_design_v2",
        }

    def create_agent_with_config(self, config) -> Agent:
        """設定オブジェクトから新しいエージェントを作成

        Args:
            config: AgentConfig設定オブジェクト

        Returns:
            Agent: 作成されたエージェント
        """
        return self.agent_factory.create_agent(config)

    def get_tool_info(self) -> dict[str, any]:
        """ツールレジストリの情報を取得"""
        return self.tool_registry.get_tool_info()

    async def route_query_async(
        self, message: str, user_id: str = "default_user", session_id: str = "default_session"
    ) -> str:
        """統合相談パイプラインを使用したクエリルーティング（非同期版）

        Args:
            message: ユーザーからのメッセージ
            user_id: ユーザーID
            session_id: セッションID

        Returns:
            str: エージェントからの応答
        """
        try:
            self.logger.info(f"統合相談パイプライン開始: message_length={len(message)}")

            # 統合相談パイプラインを使用
            pipeline = self.get_pipeline("comprehensive")
            pipeline_runner = self._runners.get("comprehensive")

            if not pipeline_runner:
                # Runnerが存在しない場合は作成
                pipeline_runner = Runner(agent=pipeline, app_name=self._app_name, session_service=self._session_service)
                self._runners["comprehensive"] = pipeline_runner

            self.logger.info("統合相談パイプライン取得完了")

            # メッセージをContent形式に変換
            from google.genai.types import Part

            content = Content(role="user", parts=[Part(text=message)])

            # セッションが存在しない場合は作成
            try:
                await self._session_service.get_session(self._app_name, user_id, session_id)
            except Exception:
                # セッションが存在しない場合は作成
                await self._session_service.create_session(
                    app_name=self._app_name, user_id=user_id, session_id=session_id
                )

            # パイプライン実行（非同期）
            events = []
            async for event in pipeline_runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                events.append(event)

            # 最後のイベントからレスポンスを取得
            if events:
                last_event = events[-1]
                if hasattr(last_event, "content") and last_event.content:
                    response_content = last_event.content

                    # Contentオブジェクトから文字列を抽出
                    if hasattr(response_content, "parts") and response_content.parts:
                        # Content.partsからテキストを抽出
                        response_text = ""
                        for part in response_content.parts:
                            if hasattr(part, "text") and part.text:
                                response_text += part.text
                    elif isinstance(response_content, str):
                        response_text = response_content
                    else:
                        response_text = str(response_content)

                    self.logger.info(f"統合相談パイプライン応答成功: response_length={len(response_text)}")
                    return response_text
                else:
                    raise Exception("Pipeline response event has no content")
            else:
                raise Exception("No events received from pipeline")

        except Exception as e:
            self.logger.error(f"統合相談パイプラインエラー: {e}")

            # フォールバック: 個別エージェント使用
            try:
                self.logger.info("フォールバック: 個別子育てエージェント使用")
                childcare_runner = self._runners.get("childcare")

                if not childcare_runner:
                    raise Exception("Childcare runner not available")

                # メッセージをContent形式に変換
                from google.genai.types import Part

                content = Content(role="user", parts=[Part(text=message)])

                # セッションが存在しない場合は作成（フォールバック用）
                try:
                    await self._session_service.get_session(self._app_name, user_id, session_id)
                except Exception:
                    # セッションが存在しない場合は作成
                    await self._session_service.create_session(
                        app_name=self._app_name, user_id=user_id, session_id=session_id
                    )

                # エージェント実行（非同期）
                events = []
                async for event in childcare_runner.run_async(
                    user_id=user_id, session_id=session_id, new_message=content
                ):
                    events.append(event)

                # 最後のイベントからレスポンスを取得
                if events:
                    last_event = events[-1]
                    if hasattr(last_event, "content") and last_event.content:
                        response_content = last_event.content

                        # Contentオブジェクトから文字列を抽出
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
                    else:
                        return "申し訳ございません。一時的に応答できません。しばらくしてから再度お試しください。"
                else:
                    return "申し訳ございません。一時的に応答できません。しばらくしてから再度お試しください。"

            except Exception as fallback_error:
                self.logger.error(f"フォールバックエラー: {fallback_error}")
                return (
                    f"申し訳ございません。システムエラーが発生しました。\n"
                    f"エラー詳細: {str(e)}\n"
                    f"フォールバックエラー: {str(fallback_error)}\n\n"
                    f"しばらくしてから再度お試しください。"
                )

    def route_query(self, message: str, user_id: str = "default_user", session_id: str = "default_session") -> str:
        """統合相談パイプラインを使用したクエリルーティング（同期版）

        Args:
            message: ユーザーからのメッセージ
            user_id: ユーザーID
            session_id: セッションID

        Returns:
            str: エージェントからの応答
        """
        try:
            # 非同期関数を同期実行
            return asyncio.run(self.route_query_async(message, user_id, session_id))
        except Exception as e:
            self.logger.error(f"同期実行エラー: {e}")
            return f"申し訳ございません。システムエラーが発生しました: {str(e)}"
