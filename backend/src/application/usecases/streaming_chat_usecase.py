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
        web_search_enabled: bool = False,
        # 画像・マルチモーダル対応追加
        message_type: str = "text",
        has_image: bool = False,
        image_path: str = None,
        multimodal_context: dict = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """マルチエージェント実行と進捗詳細（ビジネスロジック）

        Args:
            agent_manager: エージェントマネージャー
            message: ユーザーメッセージ
            user_id: ユーザーID
            session_id: セッションID
            conversation_history: 会話履歴
            family_info: 家族情報
            web_search_enabled: Web検索フラグ

        Yields:
            Dict[str, Any]: 進捗情報

        """
        try:
            self.logger.info(
                f"🚀 マルチエージェント実行開始: session_id={session_id}, message='{message[:50]}...', web_search_enabled={web_search_enabled}",
            )
            self.logger.info(
                f"🎯 UseCase側Web検索フラグ詳細: type={type(web_search_enabled)}, value={web_search_enabled!r}"
            )
            # 画像・マルチモーダル情報ログ追加
            if has_image:
                self.logger.info(f"🖼️ 画像添付検出: message_type={message_type}, image_path={'あり' if image_path else 'なし'}")

            # ビジネスロジック: 初期状態設定
            progress_state = self._initialize_progress_state()

            # ビジネスロジック: 会話履歴分析
            async for progress in self._analyze_conversation_history(conversation_history):
                yield progress

            # ビジネスロジック: 専門家予測とルーティング
            async for progress in self._predict_and_route_specialist(agent_manager, message, web_search_enabled):
                yield progress

            # ビジネスロジック: エージェント実行開始
            yield {"type": "agent_executing", "message": "💫 Genieが心を込めて分析中...", "data": {}}
            await asyncio.sleep(0.5)

            # ビジネスロジック: エージェント実行
            response, agent_info, routing_path = await self._execute_agent_core(
                agent_manager,
                message,
                user_id,
                session_id,
                conversation_history,
                family_info,
                web_search_enabled,
                # 画像・マルチモーダル対応パラメータを渡す
                message_type,
                has_image,
                image_path,
                multimodal_context,
            )

            # Web検索が有効で検索専門エージェントが実行された場合、progress_stateを更新
            if web_search_enabled and agent_info.get("agent_id") == "search_specialist":
                search_specialist_result = self.agent_info_usecase.get_specialist_info("search_specialist")
                search_specialist_info = search_specialist_result.get(
                    "data",
                    {
                        "name": "検索のジーニー",
                        "description": "最新の子育て情報を検索してお届け",
                    },
                )
                progress_state["actual_specialist_info"] = search_specialist_info
                self.logger.info(
                    f"🔍 Web検索モード: progress_state更新 specialist_name={search_specialist_info['name']}"
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
                agent_info,
                progress_state,
                user_id,
                session_id,
                routing_path,
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
        coordinator_info = coordinator_result.get(
            "data",
            {
                "name": "子育て相談のジーニー",
                "description": "温かく寄り添う総合的な子育てサポート",
            },
        )

        return {
            "coordinator_info": coordinator_info,
            "predicted_specialist": "coordinator",
            "predicted_info": coordinator_info,
            "actual_specialist_info": coordinator_info,
            "specialist_executed": False,
            "displayed_specialists": set(),
            "specialist_messages_sent": set(),
        }

    async def _analyze_conversation_history(
        self,
        conversation_history: list[dict[str, Any]],
    ) -> AsyncGenerator[dict[str, Any], None]:
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

    async def _predict_and_route_specialist(
        self,
        agent_manager: AgentManager,
        message: str,
        web_search_enabled: bool = False,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """専門家予測とルーティング（ビジネスロジック）"""
        # Web検索モード時は専用メッセージを表示
        if web_search_enabled:
            yield {
                "type": "analyzing_request",
                "message": "🔍 Web検索モードでご相談内容を分析しています...",
                "data": {"status": "analyzing", "web_search_enabled": True},
            }
            await asyncio.sleep(0.8)

            # 検索専門エージェントの情報を取得
            search_specialist_result = self.agent_info_usecase.get_specialist_info("search_specialist")
            search_specialist_info = search_specialist_result.get(
                "data",
                {
                    "name": "検索のジーニー",
                    "description": "最新の子育て情報を検索してお届け",
                },
            )

            yield {
                "type": "searching_specialist",
                "message": "🌐 検索専門ジーニーに直接ルーティング中...",
                "data": {
                    "status": "searching",
                    "web_search_enabled": True,
                    "forced_agent": "search_specialist",
                    "specialist_name": search_specialist_info["name"],
                    "specialist_description": search_specialist_info["description"],
                },
            }
            await asyncio.sleep(0.9)
        else:
            # 通常モード：分析・専門家検索の段階的演出
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

    async def _execute_agent_core(
        self,
        agent_manager: AgentManager,
        message: str,
        user_id: str,
        session_id: str,
        conversation_history: list[dict[str, Any]],
        family_info: dict[str, Any],
        web_search_enabled: bool = False,
        # 画像・マルチモーダル対応パラメータ追加
        message_type: str = "text",
        has_image: bool = False,
        image_path: str = None,
        multimodal_context: dict = None,
    ) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """エージェント実行コア処理（ビジネスロジック）"""
        # ADKの通常ルーティング（メッセージ内容に基づく自動判定）を使用
        # Web検索が必要な場合は、フロントエンドで検索指示をメッセージに埋め込み済み
        agent_type = "auto"

        # ADKのSessionServiceが会話履歴を管理するため、session_idが重要
        result = await agent_manager.route_query_async_with_info(
            message,
            user_id,
            session_id,
            agent_type,
            conversation_history,
            family_info,
            # 画像・マルチモーダル対応パラメータを渡す
            has_image,
            message_type,
            image_path,
            multimodal_context,
        )

        response = result["response"]
        agent_info = result.get("agent_info", {})
        routing_path = result.get("routing_path", [])

        return response, agent_info, routing_path

    async def _display_routing_results(
        self,
        routing_path: list[dict[str, Any]],
        progress_state: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """ルーティング結果の詳細表示（ビジネスロジック）"""
        # ルーティング後の詳細表示は無効化（最適な専門ジーニーを検索中で止める）
        # 空のAsyncGeneratorを返すための実装
        if False:  # pragma: no cover
            yield

    async def _enhance_response_with_followup(self, message: str, response: str) -> str:
        """レスポンスにフォローアップ質問を追加（ビジネスロジック）"""
        if "💭" not in response and "続けて相談したい方へ" not in response:
            # ChatSupportUseCaseを使用してフォローアップ質問生成
            followup_result = self.chat_support_usecase.generate_followup_questions(message, response)
            if followup_result.get("success"):
                dynamic_questions = followup_result.get("formatted_message", "")
                return f"{response}\n\n{dynamic_questions}"

        return response

    async def _handle_search_agent_completion(
        self,
        agent_info: dict[str, Any],
        progress_state: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
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
        web_search_enabled: bool = False,
        # 画像・マルチモーダル対応パラメータ追加
        message_type: str = "text",
        has_image: bool = False,
        image_path: str = None,
        multimodal_context: dict = None,
    ) -> AsyncGenerator[str, None]:
        """進捗ストリーミング生成（ビジネスロジック統合版）

        Args:
            agent_manager: エージェントマネージャー
            message: ユーザーメッセージ
            user_id: ユーザーID
            session_id: セッションID
            conversation_history: 会話履歴
            family_info: 家族情報
            web_search_enabled: Web検索フラグ
            message_type: メッセージタイプ ("text", "image", "voice", "multimodal")
            has_image: 画像添付フラグ
            image_path: 画像パス（Base64データまたはファイルパス）
            multimodal_context: マルチモーダルコンテキスト情報

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
                agent_manager,
                message,
                user_id,
                session_id,
                conversation_history,
                family_info,
                web_search_enabled,
                # 画像・マルチモーダル対応パラメータを渡す
                message_type,
                has_image,
                image_path,
                multimodal_context,
            ):
                yield f"data: {json.dumps(progress)}\n\n"
                if progress["type"] == "final_response":
                    final_response = progress["message"]

            # 3. 完了
            yield f"data: {json.dumps({'type': 'complete', 'message': '✅ 相談対応が完了しました', 'data': {'response': final_response}})}\n\n"

        except Exception as e:
            self.logger.error(f"ストリーミングエラー: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'❌ エラーが発生しました: {e!s}', 'data': {}})}\n\n"
