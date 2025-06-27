"""AgentManager V2 - 軽量化された統合管理システム

3つのコンポーネントを統合して責務を明確に分離:
- AgentRegistry: エージェント初期化とRunner管理
- MessageProcessor: メッセージ処理とコンテキスト管理
- RoutingExecutor: ルーティング実行とフォールバック処理
"""

import asyncio
import logging

from src.agents.agent_registry import AgentRegistry
from src.agents.message_processor import MessageProcessor
from src.agents.routing_executor import RoutingExecutor
from src.agents.routing_strategy import RoutingStrategy


class AgentManager:
    """軽量化されたAgentManager - 統合インターフェース
    
    3つのコンポーネントを統合して単一のインターフェースを提供
    """

    def __init__(
        self,
        tools: dict,
        logger: logging.Logger,
        settings,
        routing_strategy: RoutingStrategy | None = None,
    ):
        """AgentManager初期化
        
        Args:
            tools: エージェントが使用するツール群
            logger: DIコンテナから注入されるロガー
            settings: アプリケーション設定
            routing_strategy: ルーティング戦略

        """
        self.logger = logger
        self.settings = settings
        self.routing_strategy = routing_strategy

        # コンポーネント初期化
        self._registry = AgentRegistry(tools, logger)
        self._message_processor = MessageProcessor(logger)
        self._routing_executor = RoutingExecutor(logger, routing_strategy, self._message_processor)

        # 互換性のためのエイリアス
        self._agents = self._registry._agents
        self._runners = self._registry._runners
        self._session_service = self._registry._session_service

    def initialize_all_components(self) -> None:
        """全コンポーネント初期化"""
        self._registry.initialize_all_agents()

    async def route_query_async(
        self,
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session",
        agent_type: str = "auto",
        conversation_history: list | None = None,
        family_info: dict | None = None,
    ) -> str:
        """マルチエージェント対応クエリ実行（非同期）"""
        try:
            # メッセージ整形
            enhanced_message = self._message_processor.create_message_with_context(
                message, conversation_history, family_info,
            )

            # ルーティング実行
            response, agent_info, routing_path = await self._routing_executor.execute_with_routing(
                message=message,
                user_id=user_id,
                session_id=session_id,
                runners=self._registry.get_all_runners(),
                session_service=self._registry.get_session_service(),
                enhanced_message=enhanced_message,
                conversation_history=conversation_history,
                family_info=family_info,
                agent_type=agent_type,
            )

            # フォローアップ質問生成
            if agent_info.get("agent_id") not in ["sequential", "parallel"]:
                # フォローアップランナー取得
                followup_runner = None
                if "followup_question_generator" in self._registry._runners:
                    followup_runner = self._registry.get_runner("followup_question_generator")

                followup_questions = await self._message_processor.generate_followup_questions(
                    original_message=message,
                    specialist_response=response,
                    followup_runner=followup_runner,
                    session_service=self._registry.get_session_service(),
                )

                if followup_questions:
                    return f"{response}\n\n{followup_questions}"

            return response

        except Exception as e:
            self.logger.error(f"エージェント実行エラー: {e}")
            return f"申し訳ございません。システムエラーが発生しました: {e!s}"

    async def route_query_async_with_info(
        self,
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session",
        agent_type: str = "auto",
        conversation_history: list | None = None,
        family_info: dict | None = None,
    ) -> dict:
        """ルーティング情報付きマルチエージェント対応クエリ実行"""
        try:
            # メッセージ整形
            enhanced_message = self._message_processor.create_message_with_context(
                message, conversation_history, family_info,
            )

            # ルーティング実行
            response, agent_info, routing_path = await self._routing_executor.execute_with_routing(
                message=message,
                user_id=user_id,
                session_id=session_id,
                runners=self._registry.get_all_runners(),
                session_service=self._registry.get_session_service(),
                enhanced_message=enhanced_message,
                conversation_history=conversation_history,
                family_info=family_info,
                agent_type=agent_type,
            )

            # フォローアップ質問生成
            if agent_info.get("agent_id") not in ["sequential", "parallel"]:
                followup_runner = None
                if "followup_question_generator" in self._registry._runners:
                    followup_runner = self._registry.get_runner("followup_question_generator")

                followup_questions = await self._message_processor.generate_followup_questions(
                    original_message=message,
                    specialist_response=response,
                    followup_runner=followup_runner,
                    session_service=self._registry.get_session_service(),
                )

                if followup_questions:
                    response = f"{response}\n\n{followup_questions}"

            return {
                "response": response,
                "agent_info": agent_info,
                "routing_path": routing_path,
            }

        except Exception as e:
            self.logger.error(f"エージェント実行エラー: {e}")
            return {
                "response": f"申し訳ございません。システムエラーが発生しました: {e!s}",
                "agent_info": {},
                "routing_path": [],
            }

    def route_query(
        self,
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session",
    ) -> str:
        """クエリ実行（同期）"""
        return asyncio.run(self.route_query_async(message, user_id, session_id))

    # ========== 互換性メソッド ==========

    def get_agent(self, agent_type: str = "coordinator"):
        """エージェント取得"""
        return self._registry.get_agent(agent_type)

    def get_all_agents(self) -> dict:
        """全エージェント取得"""
        return self._registry.get_all_agents()

    def get_agent_info(self) -> dict:
        """エージェント情報取得"""
        return self._registry.get_agent_info()

    def get_available_agent_types(self) -> list[str]:
        """利用可能なエージェントタイプ一覧"""
        return self._registry.get_available_agent_types()

    @property
    def _runner(self):
        """互換性のための_runner属性"""
        return self._registry.default_runner
