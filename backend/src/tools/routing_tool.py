import logging
from typing import Any, Dict, Optional
from src.agents.individual.router_agent import analyze_routing_context


def create_routing_function(
    agent_manager,
    logger: logging.Logger,
) -> callable:
    """ルーティングツール関数を作成するファクトリー（ロガーDI統合版）

    Args:
        agent_manager: AgentManagerインスタンス
        logger: ログ出力用（DIコンテナから注入）

    Returns:
        callable: ADK用ツール関数
    """

    def routing_function(
        message: str,
        user_id: str = "default_user",
        session_id: str = "default_session",
        has_image: bool = False,
        has_audio: bool = False,
        requested_agent: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """相談内容を分析して適切なエージェントにルーティング

        Args:
            message: ユーザーからの相談内容
            user_id: ユーザーID
            session_id: セッションID
            has_image: 画像添付の有無
            has_audio: 音声添付の有無
            requested_agent: ユーザーが指定したエージェント（任意）
            additional_context: 追加のコンテキスト情報

        Returns:
            Dict[str, Any]: ルーティング結果とエージェント案内
        """
        try:
            logger.info(f"ルーティング開始: user_id={user_id}, session_id={session_id}")

            # コンテキスト分析
            routing_context = analyze_routing_context(
                message=message, has_image=has_image, has_audio=has_audio, user_context=additional_context
            )

            # ルーティング判定
            recommended_agent = _determine_best_agent(
                message=message, context=routing_context, requested_agent=requested_agent
            )

            # エージェント情報の取得
            agent_info = _get_agent_info(recommended_agent)

            # 判定理由の説明
            reasoning = _explain_routing_decision(
                recommended_agent=recommended_agent, context=routing_context, requested_agent=requested_agent
            )

            # ユーザー向けの案内メッセージ作成
            guidance_message = _create_guidance_message(
                recommended_agent=recommended_agent,
                agent_info=agent_info,
                reasoning=reasoning,
                has_media=routing_context.get("has_media", False),
            )

            logger.info(f"ルーティング完了: {recommended_agent} を推奨")

            return {
                "success": True,
                "response": guidance_message,
                "metadata": {
                    "recommended_agent": recommended_agent,
                    "reasoning": reasoning,
                    "urgency_level": _assess_urgency(routing_context),
                    "complexity_level": _assess_complexity(routing_context),
                    "has_media": routing_context.get("has_media", False),
                    "session_id": session_id,
                },
            }

        except Exception as e:
            logger.error(f"ルーティングツールエラー: {e}")
            return {
                "success": False,
                "response": "申し訳ございません。相談内容の分析中に問題が発生しました。一般的な子育て相談として対応いたします。",
                "metadata": {
                    "recommended_agent": "childcare",  # デフォルトにフォールバック
                    "error": "routing_failed",
                    "error_details": str(e),
                    "session_id": session_id,
                },
            }

    return routing_function


def _determine_best_agent(message: str, context: Dict[str, Any], requested_agent: Optional[str] = None) -> str:
    """最適なエージェントを判定"""

    # ユーザーが明示的にエージェントを指定した場合
    if requested_agent and requested_agent in ["childcare", "development", "multimodal", "comprehensive", "emergency"]:
        return requested_agent

    # 緊急性の判定（最優先）
    urgency_indicators = context.get("urgency_indicators", [])
    if urgency_indicators:
        return "emergency"

    # メディア添付の判定
    if context.get("has_media", False):
        return "multimodal"

    # 複雑性の判定
    complexity_indicators = context.get("complexity_indicators", [])
    domain_indicators = context.get("domain_indicators", {})

    # 複数ドメインにまたがる場合
    active_domains = sum(1 for count in domain_indicators.values() if count > 0)
    if active_domains >= 2 or len(complexity_indicators) >= 2:
        return "comprehensive"

    # 専門性の判定
    development_score = domain_indicators.get("development", 0)
    childcare_score = domain_indicators.get("childcare", 0)

    if development_score > childcare_score and development_score > 0:
        return "development"

    # デフォルトは一般的な子育て相談
    return "childcare"


def _get_agent_info(agent_type: str) -> Dict[str, str]:
    """エージェント情報を取得"""
    agent_info_map = {
        "childcare": {
            "name": "子育て相談専門家",
            "specialty": "一般的な育児相談、しつけ、日常の悩み",
            "description": "基本的な子育ての疑問や悩みにお答えします",
        },
        "development": {
            "name": "発育・発達専門家",
            "specialty": "成長段階、発達評価、マイルストーン",
            "description": "お子さんの発達に関する専門的なアドバイスを提供します",
        },
        "multimodal": {
            "name": "画像・音声分析専門家",
            "specialty": "写真・録音の分析、視覚・聴覚情報の解釈",
            "description": "画像や音声を分析して専門的な洞察を提供します",
        },
        "comprehensive": {
            "name": "包括相談専門家",
            "specialty": "複数領域の統合相談、総合的判断",
            "description": "複雑な問題を多角的に分析して総合的な支援を行います",
        },
        "emergency": {
            "name": "緊急対応専門家",
            "specialty": "安全・健康に関わる緊急相談",
            "description": "緊急性のある問題に迅速に対応し、適切な対処法をご案内します",
        },
    }

    return agent_info_map.get(
        agent_type,
        {
            "name": "子育て相談専門家",
            "specialty": "一般的な育児相談",
            "description": "お子さんの育児についてサポートします",
        },
    )


def _explain_routing_decision(
    recommended_agent: str, context: Dict[str, Any], requested_agent: Optional[str] = None
) -> str:
    """ルーティング判定理由を説明"""

    if requested_agent == recommended_agent:
        return f"ご指定の通り{_get_agent_info(recommended_agent)['name']}が最適です"

    urgency_indicators = context.get("urgency_indicators", [])
    if urgency_indicators:
        return f"安全に関わるキーワード（{', '.join(urgency_indicators[:2])}）を検出したため"

    if context.get("has_media", False):
        media_types = context.get("media_types", [])
        return f"{'画像' if 'image' in media_types else ''}{'・' if len(media_types) > 1 else ''}{'音声' if 'audio' in media_types else ''}の分析が必要なため"

    complexity_indicators = context.get("complexity_indicators", [])
    domain_indicators = context.get("domain_indicators", {})
    active_domains = sum(1 for count in domain_indicators.values() if count > 0)

    if active_domains >= 2:
        return "複数の専門領域にわたる相談内容のため"

    if domain_indicators.get("development", 0) > 0:
        return "発達・成長に関する専門的な内容のため"

    return "一般的な子育て相談として最適な対応をするため"


def _create_guidance_message(
    recommended_agent: str, agent_info: Dict[str, str], reasoning: str, has_media: bool = False
) -> str:
    """ユーザー向けの案内メッセージを作成"""

    message_parts = []

    # 基本的な案内
    message_parts.append(f"📋 **相談内容を分析いたします**")
    message_parts.append(f"")
    message_parts.append(f"🎯 **推奨する専門家**: {agent_info['name']}")
    message_parts.append(f"📚 **専門分野**: {agent_info['specialty']}")
    message_parts.append(f"💡 **選択理由**: {reasoning}")
    message_parts.append(f"")
    message_parts.append(f"✨ **期待できるサポート**: {agent_info['description']}")

    # メディアがある場合の特別案内
    if has_media:
        message_parts.append(f"")
        message_parts.append(f"📎 添付いただいた画像・音声も含めて総合的に分析いたします")

    # 次のステップの案内
    message_parts.append(f"")
    message_parts.append(f"👨‍⚕️ 専門家が詳しくお話を伺いますので、お気軽にご相談ください")

    return "\\n".join(message_parts)


def _assess_urgency(context: Dict[str, Any]) -> str:
    """緊急度を評価"""
    urgency_indicators = context.get("urgency_indicators", [])

    if len(urgency_indicators) >= 3:
        return "high"
    elif len(urgency_indicators) >= 1:
        return "medium"
    else:
        return "low"


def _assess_complexity(context: Dict[str, Any]) -> str:
    """複雑度を評価"""
    complexity_indicators = context.get("complexity_indicators", [])
    domain_indicators = context.get("domain_indicators", {})
    active_domains = sum(1 for count in domain_indicators.values() if count > 0)

    if active_domains >= 3 or len(complexity_indicators) >= 3:
        return "high"
    elif active_domains >= 2 or len(complexity_indicators) >= 1:
        return "medium"
    else:
        return "low"


def create_routing_tool(
    agent_manager,  # 型ヒントは循環参照を避けるため省略
    logger: logging.Logger,
):
    """ルーティングツール関数作成（ロガーDI統合版）

    Args:
        agent_manager: AgentManagerインスタンス
        logger: ログ出力用（DIコンテナから注入）

    Returns:
        function: ADKで使用可能なルーティング関数（ADK v1.2.1 FunctionToolバグ回避）
    """
    routing_func = create_routing_function(agent_manager, logger)
    return routing_func
