"""ストリーミングチャット API

リアルタイム進捗表示付きチャットエンドポイント
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


def get_specialist_info(agent_type: str) -> dict:
    """エージェントタイプから専門家情報を取得"""
    specialist_map = {
        "image_specialist": {
            "name": "画像解析のジーニー",
            "description": "お子さんの写真から表情や成長を優しく分析",
            "tools": ["analyze_child_image", "image_processing"]
        },
        "voice_specialist": {
            "name": "音声解析のジーニー",
            "description": "泣き声や話し声から気持ちを理解",
            "tools": ["analyze_child_voice", "voice_processing"]
        },
        "record_specialist": {
            "name": "記録分析のジーニー",
            "description": "成長記録から大切なパターンを発見",
            "tools": ["manage_child_records", "data_analysis"]
        },
        "file_specialist": {
            "name": "ファイル管理のジーニー",
            "description": "大切な思い出を安全に保存・整理",
            "tools": ["manage_child_files", "file_organization"]
        },
        "nutrition_specialist": {
            "name": "栄養・食事のジーニー",
            "description": "離乳食や食事の悩みに温かく寄り添い",
            "tools": ["nutrition_advice", "meal_planning"]
        },
        "coordinator": {
            "name": "子育て相談のジーニー",
            "description": "温かく寄り添う総合的な子育てサポート",
            "tools": ["childcare_consultation", "general_advice"]
        },
        "sequential": {
            "name": "連携分析のジーニー",
            "description": "複数の専門家が順番に詳しく分析",
            "tools": ["sequential_analysis", "multi_step_processing"]
        },
        "parallel": {
            "name": "総合分析のジーニー",
            "description": "複数の専門家が同時に多角的に分析",
            "tools": ["parallel_analysis", "comprehensive_evaluation"]
        }
    }
    
    return specialist_map.get(agent_type, {
        "name": "子育てサポートのジーニー",
        "description": "温かく寄り添う子育てサポート",
        "tools": ["general_support"]
    })


class StreamingChatMessage(BaseModel):
    """ストリーミングチャットメッセージ"""

    message: str
    user_id: str = "frontend_user"
    session_id: str = "default_session"
    conversation_history: list = []
    family_info: dict = None


async def create_progress_stream(
    agent_manager, message: str, user_id: str, session_id: str, conversation_history: list, family_info: dict, logger: logging.Logger
) -> AsyncGenerator[str, None]:
    """進捗ストリーミング生成"""

    try:
        # 1. 開始
        yield f"data: {json.dumps({'type': 'start', 'message': '🚀 AI分析を開始します...', 'data': {}})}\n\n"
        await asyncio.sleep(0.3)

        # 2. 進捗表示を含むAgent実行
        final_response = ""
        async for progress in execute_agent_with_progress(agent_manager, message, user_id, session_id, conversation_history, family_info, logger):
            yield f"data: {json.dumps(progress)}\n\n"
            if progress["type"] == "final_response":
                final_response = progress["message"]

        # 3. 完了
        yield f"data: {json.dumps({'type': 'complete', 'message': '✅ 相談対応が完了しました', 'data': {'response': final_response}})}\n\n"

    except Exception as e:
        logger.error(f"ストリーミングエラー: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'❌ エラーが発生しました: {str(e)}', 'data': {}})}\n\n"


async def execute_agent_with_progress(
    agent_manager, message: str, user_id: str, session_id: str, conversation_history: list, family_info: dict, logger: logging.Logger
) -> AsyncGenerator[dict, None]:
    """マルチエージェント実行と進捗詳細"""

    try:
        # 1. 開始メッセージ
        yield {"type": "agent_starting", "message": "🚀 マルチエージェント分析を開始します...", "data": {}}
        await asyncio.sleep(0.3)

        # 2. 会話履歴ログ出力
        if conversation_history:
            logger.info(f"📚 会話履歴: {len(conversation_history)}件のメッセージ")
            for i, hist_msg in enumerate(conversation_history[-3:]):  # 最新3件をログ出力
                logger.info(f"  [{i+1}] {hist_msg.get('sender', 'unknown')}: {str(hist_msg.get('content', ''))[:100]}...")
        else:
            logger.info("📚 会話履歴なし（新規会話）")

        # 3. エージェント選択とタイプ判定
        agent_type = agent_manager._determine_agent_type(message)
        specialist_info = get_specialist_info(agent_type)
        
        yield {
            "type": "agent_selecting", 
            "message": f"🎯 {specialist_info['name']}を選択中...", 
            "data": {
                "agent_type": agent_type,
                "specialist_name": specialist_info['name'],
                "specialist_description": specialist_info['description']
            }
        }
        await asyncio.sleep(0.3)

        # 4. マルチエージェント実行
        logger.info(f"🚀 マルチエージェント実行開始: session_id={session_id}, message='{message[:50]}...'")
        yield {
            "type": "agent_executing", 
            "message": f"🔄 {specialist_info['name']}が分析中...", 
            "data": {
                "agent_type": agent_type,
                "specialist_name": specialist_info['name'],
                "tools": specialist_info['tools']
            }
        }

        # ADKのSessionServiceが会話履歴を管理するため、session_idが重要
        response = await agent_manager.route_query_async(message, user_id, session_id, "auto", conversation_history, family_info)

        # 4. 分析完了
        yield {"type": "analysis_complete", "message": "✅ 専門分析が完了しました", "data": {}}
        await asyncio.sleep(0.3)

        # 5. 最終レスポンス
        yield {
            "type": "final_response",
            "message": response,
            "data": {
                "agent_type": agent_type, 
                "specialist_name": specialist_info['name'],
                "user_id": user_id, 
                "session_id": session_id
            },
        }

    except Exception as e:
        logger.error(f"マルチエージェント実行エラー: {e}")
        yield {
            "type": "final_response",
            "message": f"申し訳ございません。分析中にエラーが発生しました: {str(e)}",
            "data": {"error": True},
        }


@router.post("/streaming-chat")
async def streaming_chat_endpoint(
    chat_message: StreamingChatMessage,
    request: Request,
):
    """ストリーミングチャットエンドポイント"""
    logger = request.app.logger
    agent_manager = request.app.agent_manager

    logger.info(f"ストリーミングチャット開始: user_id={chat_message.user_id}, message='{chat_message.message[:50]}...'")

    async def event_stream():
        async for data in create_progress_stream(
            agent_manager,
            chat_message.message,
            chat_message.user_id,
            chat_message.session_id,
            chat_message.conversation_history,
            chat_message.family_info,
            logger,
        ):
            yield data

    return StreamingResponse(event_stream(), media_type="text/plain")
