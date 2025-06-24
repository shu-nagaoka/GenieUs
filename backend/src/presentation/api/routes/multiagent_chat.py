"""シンプルチャットエンドポイント

子育て相談AI - ADKネイティブ実装
"""

import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter()


class ChatMessage(BaseModel):
    """チャットメッセージモデル"""

    message: str = Field(..., description="ユーザーからのメッセージ")
    user_id: str = Field(default="anonymous", description="ユーザーID")
    session_id: str = Field(default="default", description="セッションID")


class ChatResponse(BaseModel):
    """チャットレスポンスモデル"""

    response: str = Field(..., description="AIエージェントからの応答")
    status: str = Field(default="success", description="処理状況")
    session_id: str = Field(..., description="セッションID")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_message: ChatMessage,
    request: Request,
):
    """シンプルチャットエンドポイント

    子育て相談AI（ADKネイティブ）
    """
    # 注入された必要なコンポーネントを取得
    logger = request.app.logger
    agent_manager = request.app.agent_manager

    try:
        logger.info(f"チャット要求受信: user_id={chat_message.user_id}, session_id={chat_message.session_id}")

        # 利用可能ツール確認
        all_tools = agent_manager.tools
        tool_names = [name for name, tool in all_tools.items() if tool is not None]
        logger.info(f"🔧 利用可能ツール: {tool_names}")

        # AgentManagerで直接実行
        response_text = await agent_manager.route_query_async(
            message=chat_message.message, user_id=chat_message.user_id, session_id=chat_message.session_id
        )

        logger.info(f"✅ レスポンス生成完了: 文字数={len(response_text)}")

        return ChatResponse(response=response_text, status="success", session_id=chat_message.session_id)

    except Exception as e:
        logger.error(f"チャット処理エラー: {e}")

        return ChatResponse(
            response="申し訳ございません。システムで問題が発生しました。",
            status="error",
            session_id=chat_message.session_id,
        )
