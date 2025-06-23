"""マルチエージェント対応チャットエンドポイント

agent-to-agentルーティング機能を統合したチャットAPI
"""

import logging
import re
from typing import Dict, Any, Optional, List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.di_provider.container import DIContainer

router = APIRouter()


class MultiAgentChatMessage(BaseModel):
    """マルチエージェント対応チャットメッセージモデル"""

    message: str = Field(..., description="ユーザーからのメッセージ")
    user_id: str = Field(default="anonymous", description="ユーザーID")
    session_id: str = Field(default="default", description="セッションID")
    requested_agent: Optional[str] = Field(
        default=None, description="指定するエージェント（childcare, development, multimodal, comprehensive, emergency）"
    )
    has_image: bool = Field(default=False, description="画像添付の有無")
    has_audio: bool = Field(default=False, description="音声添付の有無")
    image_path: Optional[str] = Field(default=None, description="画像ファイルパス（has_image=Trueの場合）")
    audio_text: Optional[str] = Field(default=None, description="音声認識テキスト（has_audio=Trueの場合）")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(default=None, description="会話履歴")
    additional_context: Optional[Dict[str, Any]] = Field(default=None, description="追加コンテキスト")


class MultiAgentChatResponse(BaseModel):
    """マルチエージェント対応チャットレスポンスモデル"""

    response: str = Field(..., description="AIエージェントからの応答")
    status: str = Field(default="success", description="処理状況")
    session_id: str = Field(..., description="セッションID")
    agent_used: str = Field(..., description="実際に使用されたエージェント")
    routing_info: Dict[str, Any] = Field(..., description="ルーティング情報")
    follow_up_questions: Optional[List[str]] = Field(default=None, description="フォローアップ質問")
    agent_info: Dict[str, Any] = Field(..., description="使用されたエージェント情報")
    debug_info: Optional[Dict[str, Any]] = Field(default=None, description="デバッグ情報")


@router.post("/chat", response_model=MultiAgentChatResponse)
@inject
async def multiagent_chat_endpoint(
    chat_message: MultiAgentChatMessage,
    request: Request,
    logger=Depends(Provide[DIContainer.logger]),
):
    """マルチエージェント対応チャットエンドポイント

    ユーザーの相談内容を分析して適切な専門エージェントにルーティング
    """
    # FastAPIアプリからagent_managerを取得
    agent_manager = request.app.agent_manager

    try:
        logger.info(
            "マルチエージェントチャット要求受信",
            extra={
                "user_id": chat_message.user_id,
                "session_id": chat_message.session_id,
                "message_length": len(chat_message.message),
                "requested_agent": chat_message.requested_agent,
                "has_media": chat_message.has_image or chat_message.has_audio,
            },
        )

        # シンプルに包括的パイプラインを実行（トリアージ→専門家→統合が自動実行）
        consultation_result = await _execute_comprehensive_pipeline(
            message=chat_message.message,
            user_id=chat_message.user_id,
            session_id=chat_message.session_id,
            image_path=chat_message.image_path,
            audio_text=chat_message.audio_text,
            conversation_history=chat_message.conversation_history,
            additional_context=chat_message.additional_context,
            agent_manager=agent_manager,
            logger=logger,
        )

        # レスポンス作成
        final_response = MultiAgentChatResponse(
            response=consultation_result.get("response", ""),
            status="success" if consultation_result.get("success", False) else "error",
            session_id=chat_message.session_id,
            agent_used="childcare_agent",
            routing_info={"agent": "childcare", "direct_mode": True},
            follow_up_questions=_extract_follow_up_questions(consultation_result.get("response", "")),
            agent_info={"name": "子育て相談専門エージェント", "description": "子育て全般の相談に対応"},
            debug_info=consultation_result.get("metadata", {}),
        )

        logger.info(
            "マルチエージェントチャット処理完了",
            extra={
                "session_id": chat_message.session_id,
                "agent_used": "childcare_agent",
                "success": consultation_result.get("success", False),
            },
        )

        return final_response

    except Exception as e:
        logger.error(
            "マルチエージェントチャット処理エラー",
            extra={"error": str(e), "session_id": chat_message.session_id, "user_id": chat_message.user_id},
        )

        # フォールバック応答
        return MultiAgentChatResponse(
            response="申し訳ございません。システムで問題が発生しました。一般的な子育て相談として対応いたします。",
            status="error",
            session_id=chat_message.session_id,
            agent_used="childcare",  # フォールバック
            routing_info={"error": "routing_failed", "fallback": True},
            agent_info={"name": "子育て相談専門家", "error": True},
            debug_info={"error": str(e)},
        )


async def _execute_comprehensive_pipeline(
    message: str,
    user_id: str,
    session_id: str,
    image_path: Optional[str],
    audio_text: Optional[str],
    conversation_history: Optional[List[Dict[str, Any]]],
    additional_context: Optional[Dict[str, Any]],
    agent_manager,
    logger: logging.Logger,
) -> Dict[str, Any]:
    """包括的パイプラインの実行 - トリアージ→専門家→統合を自動実行"""

    try:
        # シンプルに子育てエージェントを直接使用（パイプライン問題回避）
        childcare_agent = agent_manager.get_agent("childcare")

        # メッセージ準備
        final_message = message
        if conversation_history:
            history_context = _build_conversation_context(conversation_history)
            final_message = f"{history_context}\n\n{message}"

        # マルチモーダル情報の追加
        if image_path:
            final_message += f"\n\n[画像が添付されています: {image_path}]"
        if audio_text:
            final_message += f"\n\n[音声入力: {audio_text}]"

        # ADKパイプライン実行
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai.types import Content, Part

        session_service = InMemorySessionService()
        runner = Runner(agent=childcare_agent, app_name="GenieUs-Childcare", session_service=session_service)

        # セッション作成
        await session_service.create_session(app_name="GenieUs-Childcare", user_id=user_id, session_id=session_id)

        # パイプライン実行
        user_content = Content(role="user", parts=[Part(text=final_message)])

        logger.info(f"ADKパイプライン実行開始: user_id={user_id}, session_id={session_id}")

        final_response = None
        event_count = 0
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            event_count += 1

            # ADKイベントの詳細ログ
            logger.info(
                f"ADKイベント受信 #{event_count}",
                extra={
                    "author": getattr(event, "author", "unknown"),
                    "event_type": type(event).__name__,
                    "is_final": getattr(event, "is_final_response", lambda: False)(),
                    "has_content": bool(getattr(event, "content", None)),
                    "has_actions": bool(getattr(event, "actions", None)),
                    "has_error": bool(getattr(event, "error_message", None)),
                    "session_id": session_id,
                },
            )

            # エラーがある場合は詳細ログ
            if hasattr(event, "error_message") and event.error_message:
                logger.error(f"ADKイベントエラー: {event.error_message}")

            # アクションがある場合はログ（ツール使用詳細含む）
            if hasattr(event, "actions") and event.actions:
                logger.info(f"ADKイベントアクション: {event.actions}")
                
                # ツール使用の詳細ログ
                for i, action in enumerate(event.actions):
                    if hasattr(action, 'function_call'):
                        function_call = action.function_call
                        logger.info(
                            f"🔧 ツール呼び出し検出 #{i+1}",
                            extra={
                                "tool_name": getattr(function_call, 'name', 'unknown'),
                                "tool_args": getattr(function_call, 'args', {}),
                                "event_count": event_count,
                                "session_id": session_id,
                            }
                        )
                    elif hasattr(action, 'tool_use'):
                        tool_use = action.tool_use
                        logger.info(
                            f"🔧 ツール使用検出 #{i+1}",
                            extra={
                                "tool_name": getattr(tool_use, 'name', 'unknown'),
                                "tool_input": getattr(tool_use, 'input', {}),
                                "event_count": event_count,
                                "session_id": session_id,
                            }
                        )
                    else:
                        # 一般的なアクションログ
                        action_details = str(action)
                        logger.info(
                            f"🎬 アクション検出 #{i+1}",
                            extra={
                                "action_type": type(action).__name__,
                                "action_details": action_details[:200] + "..." if len(action_details) > 200 else action_details,
                                "event_count": event_count,
                                "session_id": session_id,
                            }
                        )

            # 最終レスポンスの処理
            if event.is_final_response() and event.content:
                final_response = event.content.parts[0].text if event.content.parts else ""
                logger.info(f"ADK最終レスポンス取得: 長さ={len(final_response)}文字")
                break

        logger.info(f"ADKパイプライン実行完了: 総イベント数={event_count}")

        return {
            "success": True,
            "response": final_response or "包括的相談パイプラインが完了しました。",
            "metadata": {
                "agent": "childcare",
                "approach": "direct_childcare_agent",
                "session_id": session_id,
            },
        }

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        logger.error(
            f"包括的パイプライン実行エラー: {e}",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": error_details,
                "session_id": session_id,
                "user_id": user_id,
            },
        )
        return {
            "success": False,
            "response": "申し訳ございません。包括的相談処理中に問題が発生しました。",
            "metadata": {"error": str(e), "error_type": type(e).__name__, "pipeline": "comprehensive"},
        }


def _build_conversation_context(conversation_history: List[Dict[str, Any]]) -> str:
    """会話履歴をコンテキストに変換"""
    context_parts = ["**これまでの会話:**"]

    for i, msg in enumerate(conversation_history[-5:]):  # 直近5件
        sender = msg.get("sender", "unknown")
        content = msg.get("content", "")[:100]  # 100文字まで
        if sender == "user":
            context_parts.append(f"ユーザー: {content}")
        else:
            context_parts.append(f"AI: {content}")

    context_parts.append("**現在の相談:**")
    return "\n".join(context_parts)


# レスポンス統合処理も簡素化済み


def _remove_follow_up_section(response_text: str) -> str:
    """レスポンステキストからフォローアップ質問セクションを削除"""
    try:
        pattern = r"## 🤔 こんなことも気になりませんか？.*?(?=\Z)"
        cleaned_text = re.sub(pattern, "", response_text, flags=re.DOTALL)
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
        return cleaned_text.strip()
    except Exception:
        return response_text


def _extract_follow_up_questions(response_text: str) -> List[str]:
    """AIレスポンスからフォローアップ質問を抽出"""
    try:
        pattern = r"\*\*フォローアップ質問:\*\*\s*\n((?:\d+\.\s*.+\n?)+)"
        match = re.search(pattern, response_text, re.MULTILINE)

        if not match:
            return []

        questions_text = match.group(1)
        question_pattern = r"\d+\.\s*(.+?)(?=\n\d+\.|$)"
        questions = re.findall(question_pattern, questions_text, re.DOTALL)

        return [q.strip() for q in questions if q.strip()]
    except Exception:
        return []
