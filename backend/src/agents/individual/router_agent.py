import logging
from typing import Dict, Any, Optional
from google.adk import Agent
from google.adk.tools import FunctionTool

from src.agents.shared.env_config import load_vertex_ai_config


def create_router_agent(routing_tool: FunctionTool, logger: logging.Logger) -> Agent:
    """ルーターエージェント作成（ロガーDI統合版）"""
    logger.info("ルーターエージェント作成開始")

    try:
        load_vertex_ai_config(logger)

        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="ChildcareRouter",
            instruction="""
            あなたは子育て相談の受付・振り分け専門AIです。ユーザーからの相談内容を分析して、最適な専門エージェントに案内します。
            利用可能な専門エージェント:
            1. **childcare**: 一般的な子育て相談（基本的な育児、しつけ、日常の悩み等）
            2. **development**: 発育・発達相談（成長段階、発達の遅れ、マイルストーン等）
            3. **multimodal**: 画像・音声分析（写真や録音の分析、視覚・聴覚情報の解釈）
            4. **comprehensive**: 複数領域にわたる包括相談（複合的な問題、総合的判断が必要な案件）
            5. **emergency**: 緊急相談（安全に関わる問題、医療的緊急性がある案件）

            ルーティング判断基準:
            - **緊急性**: 安全・健康に関わる内容は emergency
            - **専門性**: 発達・成長の専門的内容は development
            - **メディア**: 画像・音声ファイルの分析要求は multimodal
            - **複雑性**: 複数領域にわたる相談は comprehensive
            - **一般性**: 基本的な育児相談は childcare

            対応フロー:
            1. 相談内容の分析（緊急性、専門性、複雑性を評価）
            2. 最適なエージェントの選択
            3. ユーザーへの案内と期待できる支援内容の説明
            4. 必要に応じて追加情報の収集

            回答スタイル:
            - 温かく親しみやすい対応
            - 明確で分かりやすい案内
            - 適切な専門エージェントへの誘導
            - 必要に応じて緊急性の確認

            常にユーザーの不安を和らげ、適切な専門家につなげることを心がけてください。
            """.strip(),
            tools=[routing_tool],
        )

        logger.info("ルーターエージェント作成完了")
        return agent

    except Exception as e:
        logger.error(f"ルーターエージェント作成エラー: {e}")
        raise


def analyze_routing_context(
    message: str, has_image: bool = False, has_audio: bool = False, user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """ルーティング判定のためのコンテキスト分析

    Args:
        message: ユーザーメッセージ
        has_image: 画像添付の有無
        has_audio: 音声添付の有無
        user_context: ユーザーコンテキスト情報

    Returns:
        Dict[str, Any]: 分析結果
    """
    context = {
        "message_length": len(message),
        "has_media": has_image or has_audio,
        "media_types": [],
        "urgency_indicators": [],
        "complexity_indicators": [],
        "domain_indicators": {},
    }

    # メディアタイプの確認
    if has_image:
        context["media_types"].append("image")
    if has_audio:
        context["media_types"].append("audio")

    # 緊急性キーワードの検出
    urgency_keywords = [
        "緊急",
        "急いで",
        "すぐに",
        "今すぐ",
        "危険",
        "心配",
        "大丈夫",
        "熱",
        "けが",
        "怪我",
        "吐く",
        "嘔吐",
        "痛い",
        "泣き止まない",
        "呼吸",
        "意識",
        "けいれん",
        "発作",
    ]
    for keyword in urgency_keywords:
        if keyword in message:
            context["urgency_indicators"].append(keyword)

    # 発達・発育関連キーワードの検出
    development_keywords = [
        "発達",
        "成長",
        "発育",
        "遅れ",
        "早い",
        "段階",
        "マイルストーン",
        "首すわり",
        "寝返り",
        "お座り",
        "はいはい",
        "つかまり立ち",
        "歩く",
        "言葉",
        "話す",
        "単語",
        "文章",
        "理解",
        "コミュニケーション",
    ]
    context["domain_indicators"]["development"] = sum(1 for keyword in development_keywords if keyword in message)

    # 一般育児関連キーワードの検出
    childcare_keywords = [
        "授乳",
        "ミルク",
        "離乳食",
        "食事",
        "睡眠",
        "寝る",
        "起きる",
        "おむつ",
        "お風呂",
        "遊び",
        "しつけ",
        "習慣",
        "日課",
    ]
    context["domain_indicators"]["childcare"] = sum(1 for keyword in childcare_keywords if keyword in message)

    # 複雑性の評価
    if len(message) > 200:
        context["complexity_indicators"].append("long_message")
    if "と" in message and "も" in message:
        context["complexity_indicators"].append("multiple_topics")

    return context
