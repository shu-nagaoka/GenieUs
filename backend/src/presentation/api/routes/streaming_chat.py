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


def generate_dynamic_followup_questions(original_message: str, specialist_response: str) -> str:
    """回答内容に基づく動的フォローアップクエスチョン生成"""
    try:
        # 簡単なキーワードベースの質問生成
        message_lower = original_message.lower()
        response_lower = specialist_response.lower()

        questions = []

        # 離乳食関連
        if any(word in message_lower or word in response_lower for word in ["離乳食", "食事", "栄養"]):
            questions = [
                "アレルギーが心配な時はどうすれば？",
                "食べない日が続く時の対処法は？",
                "手作りと市販品どちらがいい？",
            ]
        # 睡眠・夜泣き関連
        elif any(word in message_lower or word in response_lower for word in ["夜泣き", "睡眠", "寝かしつけ"]):
            questions = ["何時間くらいで改善しますか？", "昼寝の時間も関係ありますか？", "パパでも同じ方法で大丈夫？"]
        # 発達関連
        elif any(word in message_lower or word in response_lower for word in ["発達", "成長", "言葉"]):
            questions = [
                "他の子と比べて遅れていませんか？",
                "家庭でできることはありますか？",
                "専門機関に相談するタイミングは？",
            ]
        # 健康関連
        elif any(word in message_lower or word in response_lower for word in ["体調", "健康", "熱", "病気"]):
            questions = ["病院に行く目安はありますか？", "家庭でできる対処法は？", "予防するにはどうすれば？"]
        # 行動・しつけ関連
        elif any(word in message_lower or word in response_lower for word in ["しつけ", "行動", "イヤイヤ"]):
            questions = ["どのくらいの期間続きますか？", "効果的な声かけ方法は？", "やってはいけないことは？"]
        # 遊び・学習関連
        elif any(word in message_lower or word in response_lower for word in ["遊び", "学習", "知育"]):
            questions = ["年齢に合った遊び方は？", "一人遊びができない時は？", "おもちゃの選び方のコツは？"]
        # デフォルト
        else:
            questions = [
                "他の親御さんはどう対処してますか？",
                "年齢によって方法は変わりますか？",
                "注意すべきサインはありますか？",
            ]

        formatted_questions = []
        for question in questions:
            formatted_questions.append(f"💭 {question}")

        return "**【続けて相談したい方へ】**\n" + "\n".join(formatted_questions)

    except Exception as e:
        return "**【続けて相談したい方へ】**\n💭 具体的なやり方を教えて\n💭 うまくいかない時はどうする？\n💭 注意すべきポイントは？"


def get_specialist_info(agent_type: str) -> dict:
    """エージェントタイプから専門家情報を取得"""
    specialist_map = {
        # 基本エージェント（ツール利用系）
        "image_specialist": {
            "name": "画像解析のジーニー",
            "description": "お子さんの写真から表情や成長を優しく分析",
            "tools": ["analyze_child_image", "image_processing"],
        },
        "voice_specialist": {
            "name": "音声解析のジーニー",
            "description": "泣き声や話し声から気持ちを理解",
            "tools": ["analyze_child_voice", "voice_processing"],
        },
        "record_specialist": {
            "name": "記録分析のジーニー",
            "description": "成長記録から大切なパターンを発見",
            "tools": ["manage_child_records", "data_analysis"],
        },
        "file_specialist": {
            "name": "ファイル管理のジーニー",
            "description": "大切な思い出を安全に保存・整理",
            "tools": ["manage_child_files", "file_organization"],
        },
        # 15専門エージェント
        "coordinator": {
            "name": "子育て相談のジーニー",
            "description": "温かく寄り添う総合的な子育てサポート",
            "tools": ["childcare_consultation", "general_advice"],
        },
        "nutrition_specialist": {
            "name": "栄養・食事のジーニー",
            "description": "離乳食や食事の悩みに温かく寄り添い",
            "tools": ["nutrition_advice", "meal_planning"],
        },
        "sleep_specialist": {
            "name": "睡眠のジーニー",
            "description": "夜泣きや寝かしつけの悩みを優しく解決",
            "tools": ["sleep_analysis", "bedtime_guidance"],
        },
        "development_specialist": {
            "name": "発達支援のジーニー",
            "description": "お子さんの発達を温かく見守りサポート",
            "tools": ["development_assessment", "growth_support"],
        },
        "health_specialist": {
            "name": "健康管理のジーニー",
            "description": "体調や健康の心配事に寄り添い",
            "tools": ["health_monitoring", "medical_guidance"],
        },
        "behavior_specialist": {
            "name": "行動・しつけのジーニー",
            "description": "イヤイヤ期や生活習慣を優しくサポート",
            "tools": ["behavior_analysis", "parenting_tips"],
        },
        "play_learning_specialist": {
            "name": "遊び・学習のジーニー",
            "description": "年齢に合った遊びと学習を提案",
            "tools": ["educational_activities", "play_suggestions"],
        },
        "safety_specialist": {
            "name": "安全・事故防止のジーニー",
            "description": "家庭での安全対策と事故防止をサポート",
            "tools": ["safety_assessment", "accident_prevention"],
        },
        "mental_care_specialist": {
            "name": "心理・メンタルケアのジーニー",
            "description": "親子の心のケアと支援",
            "tools": ["mental_support", "stress_management"],
        },
        "work_life_specialist": {
            "name": "仕事両立のジーニー",
            "description": "仕事と育児の両立を温かくサポート",
            "tools": ["work_life_balance", "childcare_planning"],
        },
        "special_support_specialist": {
            "name": "特別支援・療育のジーニー",
            "description": "特別な支援が必要なお子さんと家族をサポート",
            "tools": ["special_education", "therapeutic_support"],
        },
        "family_relationship_specialist": {
            "name": "家族関係のジーニー",
            "description": "家族の絆を深め、関係性の悩みを温かくサポート",
            "tools": ["family_support", "relationship_guidance"],
        },
        "search_specialist": {
            "name": "検索のジーニー",
            "description": "最新の子育て情報を検索してお届け",
            "tools": ["web_search", "information_gathering"],
        },
        "administration_specialist": {
            "name": "窓口・申請のジーニー",
            "description": "自治体手続きや申請をスムーズにサポート",
            "tools": ["application_support", "administrative_guidance"],
        },
        "outing_event_specialist": {
            "name": "おでかけ・イベントのジーニー",
            "description": "楽しいお出かけ先やイベント情報をご提案",
            "tools": ["web_search", "event_planning", "outing_recommendations"],
        },
        # マルチエージェント
        "sequential": {
            "name": "連携分析のジーニー",
            "description": "複数の専門家が順番に詳しく分析",
            "tools": ["sequential_analysis", "multi_step_processing"],
        },
        "parallel": {
            "name": "総合分析のジーニー",
            "description": "複数の専門家が同時に多角的に分析",
            "tools": ["parallel_analysis", "comprehensive_evaluation"],
        },
    }

    return specialist_map.get(
        agent_type,
        {
            "name": "子育てサポートのジーニー",
            "description": "温かく寄り添う子育てサポート",
            "tools": ["general_support"],
        },
    )


class StreamingChatMessage(BaseModel):
    """ストリーミングチャットメッセージ"""

    message: str
    user_id: str = "frontend_user"
    session_id: str = "default_session"
    conversation_history: list = []
    family_info: dict = None


async def create_progress_stream(
    agent_manager,
    message: str,
    user_id: str,
    session_id: str,
    conversation_history: list,
    family_info: dict,
    logger: logging.Logger,
) -> AsyncGenerator[str, None]:
    """進捗ストリーミング生成"""

    try:
        # 1. 開始
        yield f"data: {json.dumps({'type': 'start', 'message': '🚀 AI分析を開始します...', 'data': {}})}\n\n"
        await asyncio.sleep(0.3)

        # 2. 進捗表示を含むAgent実行
        final_response = ""
        async for progress in execute_agent_with_progress(
            agent_manager, message, user_id, session_id, conversation_history, family_info, logger
        ):
            yield f"data: {json.dumps(progress)}\n\n"
            if progress["type"] == "final_response":
                final_response = progress["message"]

        # 3. 完了
        yield f"data: {json.dumps({'type': 'complete', 'message': '✅ 相談対応が完了しました', 'data': {'response': final_response}})}\n\n"

    except Exception as e:
        logger.error(f"ストリーミングエラー: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'❌ エラーが発生しました: {str(e)}', 'data': {}})}\n\n"


async def execute_agent_with_progress(
    agent_manager,
    message: str,
    user_id: str,
    session_id: str,
    conversation_history: list,
    family_info: dict,
    logger: logging.Logger,
) -> AsyncGenerator[dict, None]:
    """マルチエージェント実行と進捗詳細"""

    try:
        # Initialize variables early to ensure proper scope
        coordinator_info = get_specialist_info("coordinator")
        predicted_specialist = "coordinator"
        predicted_info = coordinator_info
        actual_specialist_info = coordinator_info
        specialist_executed = False

        # 重複防止用の状態管理
        displayed_specialists = set()  # 既に表示した専門家を追跡
        specialist_messages_sent = set()  # 送信済みメッセージタイプを追跡

        # 1. 開始メッセージ
        yield {"type": "agent_starting", "message": "🚀 マルチエージェント分析を開始します...", "data": {}}
        await asyncio.sleep(0.3)

        # 2. 会話履歴ログ出力
        if conversation_history:
            logger.info(f"📚 会話履歴: {len(conversation_history)}件のメッセージ")
            for i, hist_msg in enumerate(conversation_history[-3:]):  # 最新3件をログ出力
                logger.info(
                    f"  [{i + 1}] {hist_msg.get('sender', 'unknown')}: {str(hist_msg.get('content', ''))[:100]}..."
                )
        else:
            logger.info("📚 会話履歴なし（新規会話）")

        # 3. 事前専門家判定とルーティング表示
        # まず、どの専門家が適切かを判定
        predicted_specialist = agent_manager._determine_specialist_agent(message.lower())
        predicted_info = get_specialist_info(predicted_specialist)

        # 分析・専門家検索の段階的演出
        # まずは相談内容を分析中
        yield {
            "type": "analyzing_request",
            "message": "🤔 ご相談内容を分析しています...",
            "data": {"status": "analyzing"},
        }
        await asyncio.sleep(0.8)

        # 最適な専門ジーニーを探している演出
        yield {
            "type": "searching_specialist",
            "message": "🔍 最適な専門ジーニーを検索中...",
            "data": {"status": "searching"},
        }
        await asyncio.sleep(0.9)

        # 専門家が明確に判定できた場合は、その専門家を早期表示
        if predicted_specialist != "coordinator":
            # 重複防止: この専門家をまだ表示していない場合のみ
            if predicted_specialist not in displayed_specialists:
                displayed_specialists.add(predicted_specialist)
                specialist_messages_sent.add("specialist_found")

                yield {
                    "type": "specialist_found",
                    "message": f"✨ {predicted_info['name']}を発見しました！",
                    "data": {
                        "predicted_specialist": predicted_specialist,
                        "specialist_name": predicted_info["name"],
                        "specialist_description": predicted_info["description"],
                        "confidence": "high",
                    },
                }
                await asyncio.sleep(0.4)

                specialist_messages_sent.add("specialist_connecting")
                yield {
                    "type": "specialist_connecting",
                    "message": f"🔄 {predicted_info['name']}に接続中...",
                    "data": {
                        "specialist_name": predicted_info["name"],
                        "specialist_description": predicted_info["description"],
                    },
                }
                await asyncio.sleep(0.3)
        else:
            # コーディネーター判定の場合
            coordinator_info = get_specialist_info("coordinator")
            yield {
                "type": "agent_selecting",
                "message": f"🎯 {coordinator_info['name']}で総合的にサポートします",
                "data": {
                    "agent_type": "coordinator",
                    "specialist_name": coordinator_info["name"],
                    "specialist_description": coordinator_info["description"],
                },
            }
            await asyncio.sleep(0.3)

        # 4. 専門家分析開始
        logger.info(f"🚀 マルチエージェント実行開始: session_id={session_id}, message='{message[:50]}...'")

        # 予測された専門家または協調者の実行メッセージ
        if predicted_specialist != "coordinator":
            # 検索系エージェントかどうかを判定
            is_search_agent = predicted_specialist in ["search_specialist", "outing_event_specialist"]

            if is_search_agent:
                # 検索系エージェントの場合
                yield {
                    "type": "agent_executing",
                    "message": f"🔄 {predicted_info['name']}が相談内容を分析中...",
                    "data": {
                        "agent_type": predicted_specialist,
                        "specialist_name": predicted_info["name"],
                        "specialist_description": predicted_info["description"],
                        "tools": predicted_info["tools"],
                        "is_search_agent": True,
                    },
                }
                await asyncio.sleep(0.5)

                # 検索開始メッセージ
                yield {
                    "type": "search_starting",
                    "message": f"🔍 最新情報を検索しています...",
                    "data": {
                        "agent_type": predicted_specialist,
                        "specialist_name": predicted_info["name"],
                        "search_type": "web_search",
                    },
                }
            else:
                # 通常の専門家エージェント
                yield {
                    "type": "agent_executing",
                    "message": f"🔄 {predicted_info['name']}が相談内容を分析中...",
                    "data": {
                        "agent_type": predicted_specialist,
                        "specialist_name": predicted_info["name"],
                        "specialist_description": predicted_info["description"],
                        "tools": predicted_info["tools"],
                    },
                }
        else:
            coordinator_info = get_specialist_info("coordinator")
            yield {
                "type": "agent_executing",
                "message": f"🔄 {coordinator_info['name']}が相談内容を分析中...",
                "data": {
                    "agent_type": "coordinator",
                    "specialist_name": coordinator_info["name"],
                    "tools": coordinator_info["tools"],
                },
            }

        # ADKのSessionServiceが会話履歴を管理するため、session_idが重要
        # ルーティング情報とフォローアップクエスチョン付きで実行
        result = await agent_manager.route_query_async_with_info(
            message, user_id, session_id, "auto", conversation_history, family_info
        )
        response = result["response"]
        agent_info = result.get("agent_info", {})
        routing_path = result.get("routing_path", [])

        # 5. ルーティング情報の詳細表示とルーティング先専門家呼び出し
        # 重複防止: routing_pathから専門家ルーティングが発生した場合のみ表示

        if routing_path:
            for step in routing_path:
                if step["step"] == "specialist_routing":
                    specialist_agent = step["agent"]
                    actual_specialist_info = get_specialist_info(specialist_agent)

                    # 重複防止: この専門家の呼び出しメッセージをまだ送信していない場合のみ
                    calling_key = f"specialist_calling_{specialist_agent}"
                    ready_key = f"specialist_ready_{specialist_agent}"

                    if calling_key not in specialist_messages_sent:
                        specialist_messages_sent.add(calling_key)
                        specialist_executed = True

                        yield {
                            "type": "specialist_calling",
                            "message": f"🧞‍♀️ {actual_specialist_info['name']}を呼び出し中...",
                            "data": {
                                "specialist_agent": specialist_agent,
                                "specialist_name": actual_specialist_info["name"],
                                "specialist_description": actual_specialist_info["description"],
                                "routing_step": step["step"],
                            },
                        }
                        await asyncio.sleep(0.5)

                        # 専門家登場の表示
                        if ready_key not in specialist_messages_sent:
                            specialist_messages_sent.add(ready_key)
                            yield {
                                "type": "specialist_ready",
                                "message": f"✨ {actual_specialist_info['name']}が回答準備完了",
                                "data": {
                                    "specialist_agent": specialist_agent,
                                    "specialist_name": actual_specialist_info["name"],
                                    "specialist_description": actual_specialist_info["description"],
                                    "tools": actual_specialist_info["tools"],
                                },
                            }
                            await asyncio.sleep(0.3)

        # 専門家が実行されなかった場合の処理（重複防止）
        if not specialist_executed and predicted_specialist != "coordinator":
            # 予測された専門家の詳細分析メッセージをまだ送信していない場合のみ
            automatic_routing_key = f"automatic_routing_{predicted_specialist}"

            if automatic_routing_key not in specialist_messages_sent:
                specialist_messages_sent.add(automatic_routing_key)

                yield {
                    "type": "specialist_calling",
                    "message": f"🧞‍♀️ {predicted_info['name']}の詳細分析を実行中...",
                    "data": {
                        "specialist_agent": predicted_specialist,
                        "specialist_name": predicted_info["name"],
                        "specialist_description": predicted_info["description"],
                        "routing_step": "automatic_routing",
                    },
                }
                await asyncio.sleep(0.5)

                actual_specialist_info = predicted_info
                specialist_executed = True

        # 6. 分析完了
        yield {"type": "analysis_complete", "message": "✅ 専門分析が完了しました", "data": {}}
        await asyncio.sleep(0.3)

        # 7. フォローアップクエスチョンを追加（フロントエンドで抽出・独立表示用）
        if "💭" not in response and "続けて相談したい方へ" not in response:
            dynamic_questions = generate_dynamic_followup_questions(message, response)
            response += f"\n\n{dynamic_questions}"

        # 検索系エージェントの場合は検索完了メッセージを追加
        current_agent = agent_info.get("agent_id", "coordinator")
        if current_agent in ["search_specialist", "outing_event_specialist"]:
            yield {
                "type": "search_completed",
                "message": f"✅ 最新情報の検索が完了しました",
                "data": {
                    "agent_type": current_agent,
                    "specialist_name": actual_specialist_info["name"],
                    "search_type": "web_search",
                },
            }
            await asyncio.sleep(0.3)

        # 8. 最終レスポンス（ルーティング情報とエージェント情報付き）
        yield {
            "type": "final_response",
            "message": response,
            "data": {
                "agent_type": agent_info.get("agent_id", "coordinator"),
                "specialist_name": actual_specialist_info["name"],
                "user_id": user_id,
                "session_id": session_id,
                "agent_info": agent_info,
                "routing_path": routing_path,
                "is_search_based": current_agent in ["search_specialist", "outing_event_specialist"],
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
