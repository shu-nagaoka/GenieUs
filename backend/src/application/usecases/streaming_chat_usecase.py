"""ストリーミングチャットUseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- 統一戻り値形式
- DI注入ロガー
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from src.agents.agent_manager import AgentManager
from src.application.usecases.agent_info_usecase import AgentInfoUseCase
from src.application.usecases.chat_support_usecase import ChatSupportUseCase


class StreamingChatUseCase:
    """ストリーミングチャットのビジネスロジック
    
    マルチエージェント実行、進捗ストリーミング、エージェントルーティングを管理
    """

    def __init__(
        self,
        chat_support_usecase: ChatSupportUseCase,
        agent_info_usecase: AgentInfoUseCase,
        logger: logging.Logger,
    ) -> None:
        """Args:
        chat_support_usecase: チャットサポートUseCase（DI注入）
        agent_info_usecase: エージェント情報UseCase（DI注入）
        logger: ロガー（DIコンテナから注入）

        """
        self.chat_support_usecase = chat_support_usecase
        self.agent_info_usecase = agent_info_usecase
        self.logger = logger

    async def execute_agent_with_progress(
        self,
        agent_manager: AgentManager,
        message: str,
        user_id: str,
        session_id: str,
        conversation_history: list[dict[str, Any]],
        family_info: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """マルチエージェント実行と進捗詳細（ビジネスロジック）

        Args:
            agent_manager: エージェントマネージャー
            message: ユーザーメッセージ
            user_id: ユーザーID
            session_id: セッションID
            conversation_history: 会話履歴
            family_info: 家族情報

        Yields:
            Dict[str, Any]: 進捗情報

        """
        try:
            self.logger.info(f"🚀 マルチエージェント実行開始: session_id={session_id}, message='{message[:50]}...'")

            # ビジネスロジック: 初期状態設定
            progress_state = self._initialize_progress_state()

            # ビジネスロジック: 会話履歴分析
            async for progress in self._analyze_conversation_history(conversation_history):
                yield progress

            # ビジネスロジック: 専門家予測とルーティング
            async for progress in self._predict_and_route_specialist(agent_manager, message):
                yield progress

            # ビジネスロジック: エージェント実行
            response, agent_info, routing_path = await self._execute_agent_core(
                agent_manager, message, user_id, session_id, conversation_history, family_info,
            )

            # ビジネスロジック: ルーティング結果の詳細表示
            async for progress in self._display_routing_results(routing_path, progress_state):
                yield progress

            # ビジネスロジック: 分析完了通知
            yield {"type": "analysis_complete", "message": "✅ 専門分析が完了しました", "data": {}}
            await asyncio.sleep(0.3)

            # ビジネスロジック: フォローアップ質問追加
            enhanced_response = await self._enhance_response_with_followup(message, response)

            # ビジネスロジック: 検索系エージェント特別処理
            async for progress in self._handle_search_agent_completion(agent_info, progress_state):
                yield progress

            # ビジネスロジック: 最終レスポンス構築
            final_data = self._build_final_response_data(
                agent_info, progress_state, user_id, session_id, routing_path,
            )

            yield {
                "type": "final_response",
                "message": enhanced_response,
                "data": final_data,
            }

        except Exception as e:
            self.logger.error(f"マルチエージェント実行エラー: {e}")
            yield {
                "type": "final_response",
                "message": f"申し訳ございません。分析中にエラーが発生しました: {e!s}",
                "data": {"error": True},
            }

    def _initialize_progress_state(self) -> dict[str, Any]:
        """進捗状態の初期化（ビジネスロジック）"""
        # 専門家情報を取得
        coordinator_result = self.agent_info_usecase.get_specialist_info("coordinator")
        coordinator_info = coordinator_result.get("data", {
            "name": "子育て相談のジーニー",
            "description": "温かく寄り添う総合的な子育てサポート",
        })

        return {
            "coordinator_info": coordinator_info,
            "predicted_specialist": "coordinator",
            "predicted_info": coordinator_info,
            "actual_specialist_info": coordinator_info,
            "specialist_executed": False,
            "displayed_specialists": set(),
            "specialist_messages_sent": set(),
        }

    async def _analyze_conversation_history(self, conversation_history: list[dict[str, Any]]) -> AsyncGenerator[dict[str, Any], None]:
        """会話履歴分析（ビジネスロジック）"""
        yield {"type": "agent_starting", "message": "🚀 マルチエージェント分析を開始します...", "data": {}}
        await asyncio.sleep(0.3)

        # 会話履歴ログ出力
        if conversation_history:
            self.logger.info(f"📚 会話履歴: {len(conversation_history)}件のメッセージ")
            for i, hist_msg in enumerate(conversation_history[-3:]):  # 最新3件をログ出力
                self.logger.info(
                    f"  [{i + 1}] {hist_msg.get('sender', 'unknown')}: {str(hist_msg.get('content', ''))[:100]}...",
                )
        else:
            self.logger.info("📚 会話履歴なし（新規会話）")

    async def _predict_and_route_specialist(self, agent_manager: AgentManager, message: str) -> AsyncGenerator[dict[str, Any], None]:
        """専門家予測とルーティング（ビジネスロジック）"""
        # 事前専門家判定とルーティング表示
        if agent_manager.routing_strategy:
            predicted_specialist, _ = agent_manager.routing_strategy.determine_agent(message)
        else:
            predicted_specialist = "coordinator"

        # 専門家情報取得
        predicted_result = self.agent_info_usecase.get_specialist_info(predicted_specialist)
        predicted_info = predicted_result.get("data", {})

        # 分析・専門家検索の段階的演出
        yield {
            "type": "analyzing_request",
            "message": "🤔 ご相談内容を分析しています...",
            "data": {"status": "analyzing"},
        }
        await asyncio.sleep(0.8)

        yield {
            "type": "searching_specialist",
            "message": "🔍 最適な専門ジーニーを検索中...",
            "data": {"status": "searching"},
        }
        await asyncio.sleep(0.9)

        # 専門家表示処理
        if predicted_specialist != "coordinator":
            yield {
                "type": "specialist_found",
                "message": f"✨ {predicted_info.get('name', '専門ジーニー')}を発見しました！",
                "data": {
                    "predicted_specialist": predicted_specialist,
                    "specialist_name": predicted_info.get("name", ""),
                    "specialist_description": predicted_info.get("description", ""),
                    "confidence": "high",
                },
            }
            await asyncio.sleep(0.4)

            yield {
                "type": "specialist_connecting",
                "message": f"🔄 {predicted_info.get('name', '専門ジーニー')}に接続中...",
                "data": {
                    "specialist_name": predicted_info.get("name", ""),
                    "specialist_description": predicted_info.get("description", ""),
                },
            }
            await asyncio.sleep(0.3)
        else:
            # コーディネーター判定の場合
            coordinator_result = self.agent_info_usecase.get_specialist_info("coordinator")
            coordinator_info = coordinator_result.get("data", {})
            yield {
                "type": "agent_selecting",
                "message": f"🎯 {coordinator_info.get('name', 'コーディネーター')}で総合的にサポートします",
                "data": {
                    "agent_type": "coordinator",
                    "specialist_name": coordinator_info.get("name", ""),
                    "specialist_description": coordinator_info.get("description", ""),
                },
            }
            await asyncio.sleep(0.3)

    async def _execute_agent_core(
        self,
        agent_manager: AgentManager,
        message: str,
        user_id: str,
        session_id: str,
        conversation_history: list[dict[str, Any]],
        family_info: dict[str, Any],
    ) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """エージェント実行コア処理（ビジネスロジック）"""
        # ADKのSessionServiceが会話履歴を管理するため、session_idが重要
        result = await agent_manager.route_query_async_with_info(
            message, user_id, session_id, "auto", conversation_history, family_info,
        )

        response = result["response"]
        agent_info = result.get("agent_info", {})
        routing_path = result.get("routing_path", [])

        return response, agent_info, routing_path

    async def _display_routing_results(self, routing_path: list[dict[str, Any]], progress_state: dict[str, Any]) -> AsyncGenerator[dict[str, Any], None]:
        """ルーティング結果の詳細表示（ビジネスロジック）"""
        if not routing_path:
            return

        for step in routing_path:
            if step["step"] == "specialist_routing":
                specialist_agent = step["agent"]

                # 専門家情報取得
                specialist_result = self.agent_info_usecase.get_specialist_info(specialist_agent)
                actual_specialist_info = specialist_result.get("data", {})

                # 重複防止チェック
                calling_key = f"specialist_calling_{specialist_agent}"
                ready_key = f"specialist_ready_{specialist_agent}"

                if calling_key not in progress_state["specialist_messages_sent"]:
                    progress_state["specialist_messages_sent"].add(calling_key)
                    progress_state["specialist_executed"] = True
                    progress_state["actual_specialist_info"] = actual_specialist_info

                    yield {
                        "type": "specialist_calling",
                        "message": f"🧞‍♀️ {actual_specialist_info.get('name', '専門ジーニー')}を呼び出し中...",
                        "data": {
                            "specialist_agent": specialist_agent,
                            "specialist_name": actual_specialist_info.get("name", ""),
                            "specialist_description": actual_specialist_info.get("description", ""),
                            "routing_step": step["step"],
                        },
                    }
                    await asyncio.sleep(0.5)

                    if ready_key not in progress_state["specialist_messages_sent"]:
                        progress_state["specialist_messages_sent"].add(ready_key)
                        yield {
                            "type": "specialist_ready",
                            "message": f"✨ {actual_specialist_info.get('name', '専門ジーニー')}が回答準備完了",
                            "data": {
                                "specialist_agent": specialist_agent,
                                "specialist_name": actual_specialist_info.get("name", ""),
                                "specialist_description": actual_specialist_info.get("description", ""),
                                "tools": actual_specialist_info.get("tools", []),
                            },
                        }
                        await asyncio.sleep(0.3)

    async def _enhance_response_with_followup(self, message: str, response: str) -> str:
        """レスポンスにフォローアップ質問を追加（ビジネスロジック）"""
        if "💭" not in response and "続けて相談したい方へ" not in response:
            # ChatSupportUseCaseを使用してフォローアップ質問生成
            followup_result = self.chat_support_usecase.generate_followup_questions(message, response)
            if followup_result.get("success"):
                dynamic_questions = followup_result.get("formatted_message", "")
                return f"{response}\n\n{dynamic_questions}"

        return response

    async def _handle_search_agent_completion(self, agent_info: dict[str, Any], progress_state: dict[str, Any]) -> AsyncGenerator[dict[str, Any], None]:
        """検索系エージェント完了処理（ビジネスロジック）"""
        current_agent = agent_info.get("agent_id", "coordinator")
        if current_agent in ["search_specialist", "outing_event_specialist"]:
            yield {
                "type": "search_completed",
                "message": "✅ 最新情報の検索が完了しました",
                "data": {
                    "agent_type": current_agent,
                    "specialist_name": progress_state["actual_specialist_info"].get("name", ""),
                    "search_type": "web_search",
                },
            }
            await asyncio.sleep(0.3)

    def _build_final_response_data(
        self,
        agent_info: dict[str, Any],
        progress_state: dict[str, Any],
        user_id: str,
        session_id: str,
        routing_path: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """最終レスポンスデータ構築（ビジネスロジック）"""
        current_agent = agent_info.get("agent_id", "coordinator")

        return {
            "agent_type": current_agent,
            "specialist_name": progress_state["actual_specialist_info"].get("name", ""),
            "user_id": user_id,
            "session_id": session_id,
            "agent_info": agent_info,
            "routing_path": routing_path,
            "is_search_based": current_agent in ["search_specialist", "outing_event_specialist"],
        }

    async def create_progress_stream(
        self,
        agent_manager: AgentManager,
        message: str,
        user_id: str,
        session_id: str,
        conversation_history: list[dict[str, Any]],
        family_info: dict[str, Any],
    ) -> AsyncGenerator[str, None]:
        """進捗ストリーミング生成（ビジネスロジック統合版）

        Args:
            agent_manager: エージェントマネージャー
            message: ユーザーメッセージ
            user_id: ユーザーID
            session_id: セッションID
            conversation_history: 会話履歴
            family_info: 家族情報

        Yields:
            str: ストリーミングデータ（JSON形式）

        """
        try:
            # 1. 開始
            yield f"data: {json.dumps({'type': 'start', 'message': '🚀 AI分析を開始します...', 'data': {}})}\n\n"
            await asyncio.sleep(0.3)

            # 2. 進捗表示を含むAgent実行
            final_response = ""
            async for progress in self.execute_agent_with_progress(
                agent_manager, message, user_id, session_id, conversation_history, family_info,
            ):
                yield f"data: {json.dumps(progress)}\n\n"
                if progress["type"] == "final_response":
                    final_response = progress["message"]

            # 3. 完了
            yield f"data: {json.dumps({'type': 'complete', 'message': '✅ 相談対応が完了しました', 'data': {'response': final_response}})}\n\n"

        except Exception as e:
            self.logger.error(f"ストリーミングエラー: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ エラーが発生しました: {e!s}', 'data': {}})}\n\n"
