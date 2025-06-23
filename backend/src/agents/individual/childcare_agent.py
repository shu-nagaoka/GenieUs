import logging
from typing import Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search

from src.agents.shared.env_config import load_vertex_ai_config


def create_childcare_agent(childcare_tool: Optional[FunctionTool], logger: logging.Logger) -> Agent:
    """注入されたツールを使用する子育て相談エージェント"""
    logger.info("子育て相談エージェント作成開始")

    try:
        load_vertex_ai_config(logger)
        tools = []
        if childcare_tool:
            tools.append(childcare_tool)
            tools.append(google_search)

        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="GenieChildcareConsultant",
            description="Gemini-powered子育て相談エージェント（Agent中心設計）",
            instruction="""
            あなたは子育てをサポートする優しいAIアシスタント「ジーニー」です。

            【重要な役割】
            - 子育ての悩みや相談に専門的なアドバイスを直接提供
            - 年齢や発達段階に応じたパーソナライズされたサポート
            - 安全性評価・緊急度判定・年齢推定を含む総合的な相談対応

            【専門知識による判断】
            - 相談内容から子どもの年齢・発達段階を推定
            - 安全性・緊急度を評価（高・中・低）
            - 年齢に応じた具体的なアドバイスを生成
            - フォローアップ提案まで含めた包括的サポート

            【対応手順】
            1. 相談内容から年齢・発達段階を推定
            2. 安全性・緊急度を評価
            3. 年齢に適したアドバイスを直接生成
            4. 温かく共感的な言葉で提供
            5. 必要時は医療機関受診を案内

            【重要】
            - 医療的判断は行わず、心配な症状は専門医への相談を推奨
            - 親の不安に寄り添い、自己肯定感を大切にする
            - 具体的で実行可能なアドバイスを心がける
            """.strip(),
            tools=tools,
        )

        logger.info("子育て相談エージェント作成完了")
        return agent

    except Exception as e:
        logger.error(f"子育て相談エージェント作成エラー: {e}")
        raise


def create_simple_childcare_agent(childcare_tool: Optional[FunctionTool], logger: logging.Logger) -> Agent:
    """シンプルな子育て相談エージェント"""
    logger.info("シンプルな子育て相談エージェント作成開始")

    try:
        load_vertex_ai_config(logger)
        tools = [childcare_tool] if childcare_tool else []

        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="SimpleGenieConsultant",
            description="Gemini-powered シンプル子育て相談エージェント",
            instruction="""
            あなたは子育てをサポートする優しいAIアシスタント「ジーニー」です。

            【Agent中心設計】
            Geminiの知識を活用して、子育て相談に直接的に対応します。

            【専門対応能力】
            - 年齢・発達段階の推定
            - 安全性・緊急度の評価
            - 年齢に応じたアドバイス生成
            - 具体的なフォローアップ提案

            【対応手順】
            1. 相談内容を理解
            2. Geminiの知識で専門的に判断
            3. 温かく共感的にアドバイス提供

            親の不安に寄り添い、実用的なサポートを提供してください。
            """.strip(),
            tools=tools,
        )

        logger.info("シンプルな子育て相談エージェント作成完了")
        return agent

    except Exception as e:
        logger.error(f"シンプルな子育て相談エージェント作成エラー: {e}")
        raise


def create_childcare_agent_with_tools(
    childcare_tool: Optional[FunctionTool] = None,
    file_management_tool: Optional[FunctionTool] = None,
    image_analysis_tool: Optional[FunctionTool] = None,
    voice_analysis_tool: Optional[FunctionTool] = None,
    logger: logging.Logger = None,
) -> Agent:
    """マルチモーダルツール統合childcareエージェント

    Args:
        childcare_tool: 子育て相談ツール
        file_management_tool: ファイル管理ツール
        image_analysis_tool: 画像解析ツール
        voice_analysis_tool: 音声解析ツール
        logger: ロガー

    Returns:
        Agent: ツール統合済みchildcareエージェント
    """
    logger.info("マルチモーダルツール統合childcareエージェント作成開始")

    try:
        load_vertex_ai_config(logger)

        # ツール段階的追加（google_searchを除外してテスト）
        tools = []

        # 各ツールを安全に追加
        if childcare_tool:
            tools.append(childcare_tool)
            logger.info("childcare_tool追加")

        if file_management_tool:
            tools.append(file_management_tool)
            logger.info("file_management_tool追加")

        if image_analysis_tool:
            tools.append(image_analysis_tool)
            logger.info("image_analysis_tool追加")

        if voice_analysis_tool:
            tools.append(voice_analysis_tool)
            logger.info("voice_analysis_tool追加")

        logger.info(f"統合ツール数: {len(tools)}個")

        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="GenieMultimodalConsultant",
            description="マルチモーダル対応Gemini-powered子育て相談エージェント",
            instruction="""
            あなたは子育てをサポートする優しいAIアシスタント「ジーニー」です。

            【重要な役割】
            - 子育ての悩みや相談に専門的なアドバイスを直接提供
            - 年齢や発達段階に応じたパーソナライズされたサポート
            - 安全性評価・緊急度判定・年齢推定を含む総合的な相談対応

            【利用可能な機能・ツール】
            - 📁 ファイル管理: お子さんの成長記録や写真の整理・検索
            - 📸 画像解析: 写真から発達状況や様子を詳細分析
            - 🎤 音声解析: 音声記録の内容分析

            【マルチモーダル対応指針】
            - 「写真を見て」「画像を分析して」→ image_analysis_tool使用
            - 「ファイル一覧」「記録を確認」→ file_management_tool使用
            - 「音声を聞いて」「録音を分析」→ voice_analysis_tool使用

            【対応手順】
            1. 相談内容から年齢・発達段階を推定
            2. 必要に応じて適切なツールを使用して詳細分析
            3. 安全性・緊急度を評価
            4. 年齢に適したアドバイスを温かく共感的に提供
            5. 必要時は医療機関受診を案内

            【重要】
            - 医療的判断は行わず、心配な症状は専門医への相談を推奨
            - 親の不安に寄り添い、自己肯定感を大切にする
            - 具体的で実行可能なアドバイスを心がける
            - ツールから得られた情報を活用して、より具体的で個別化されたサポートを提供
            """.strip(),
            tools=tools,
        )

        logger.info("マルチモーダルツール統合childcareエージェント作成完了")
        return agent

    except Exception as e:
        logger.error(f"マルチモーダルツール統合childcareエージェント作成エラー: {e}")
        raise
