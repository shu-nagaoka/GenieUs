"""フォールバック用シンプル並列エージェント

ADKのParallelAgentが問題がある場合の代替実装

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from src.agents.agent_manager import AgentManager


@dataclass
class FallbackParallelRequest:
    """フォールバックパラレル処理リクエスト"""

    user_message: str
    selected_agents: list[str]
    user_id: str
    session_id: str


@dataclass
class FallbackAgentResponse:
    """フォールバックエージェントレスポンス"""

    agent_id: str
    agent_name: str
    response: str
    success: bool


@dataclass
class FallbackParallelResponse:
    """フォールバックパラレルレスポンス"""

    responses: list[FallbackAgentResponse]
    success: bool
    error_message: str | None = None


class FallbackParallelAgent:
    """個別エージェント直接実行によるフォールバック並列処理"""

    def __init__(self, agent_manager: AgentManager, logger: logging.Logger):
        """初期化

        Args:
            agent_manager: エージェント管理システム
            logger: DIコンテナから注入されるロガー
        """
        self.agent_manager = agent_manager
        self.logger = logger

    async def execute_parallel(self, request: FallbackParallelRequest) -> FallbackParallelResponse:
        """個別エージェント並列実行

        Args:
            request: フォールバックパラレル処理リクエスト

        Returns:
            FallbackParallelResponse: 実行結果
        """
        try:
            self.logger.info(f"🚀 フォールバック並列実行: {len(request.selected_agents)}エージェント")

            # 並列タスク作成
            tasks = []
            for agent_id in request.selected_agents:
                task = self._execute_single_agent(
                    agent_id=agent_id,
                    message=request.user_message,
                    user_id=request.user_id,
                    session_id=f"{request.session_id}_{agent_id}",
                )
                tasks.append(task)

            # 並列実行
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 結果処理
            responses = []
            agent_info = self.agent_manager._registry.get_agent_info()

            for i, result in enumerate(results):
                agent_id = request.selected_agents[i]
                display_name = agent_info.get(agent_id, {}).get("display_name", agent_id)

                if isinstance(result, Exception):
                    self.logger.error(f"❌ {agent_id} 実行エラー: {result}")
                    responses.append(
                        FallbackAgentResponse(
                            agent_id=agent_id,
                            agent_name=display_name,
                            response=f"エラー: {str(result)}",
                            success=False,
                        )
                    )
                else:
                    responses.append(
                        FallbackAgentResponse(
                            agent_id=agent_id,
                            agent_name=display_name,
                            response=result,
                            success=True,
                        )
                    )

            success_count = sum(1 for resp in responses if resp.success)
            self.logger.info(f"✅ フォールバック並列実行完了: {success_count}/{len(responses)}件成功")

            return FallbackParallelResponse(responses=responses, success=success_count > 0)

        except Exception as e:
            self.logger.error(f"❌ フォールバック並列実行エラー: {e}")

            return FallbackParallelResponse(responses=[], success=False, error_message=str(e))

    async def _execute_single_agent(self, agent_id: str, message: str, user_id: str, session_id: str) -> str:
        """単一エージェント実行

        Args:
            agent_id: エージェントID
            message: ユーザーメッセージ
            user_id: ユーザーID
            session_id: セッションID

        Returns:
            str: エージェントレスポンス
        """
        try:
            # AgentManagerの既存ルーティング機能を使用
            response = await self.agent_manager.route_query_async(
                message=message, user_id=user_id, session_id=session_id, agent_type=agent_id
            )

            return response

        except Exception as e:
            raise RuntimeError(f"{agent_id}実行エラー: {e}")
