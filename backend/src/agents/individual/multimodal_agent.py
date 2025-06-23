import logging
from google.adk import Agent
from google.adk.tools import FunctionTool
from src.agents.shared.env_config import load_vertex_ai_config


def create_multimodal_agent(
    image_analysis_tool: FunctionTool, voice_analysis_tool: FunctionTool, logger: logging.Logger
) -> Agent:
    """マルチモーダル分析エージェント作成（ロガーDI統合版）"""
    logger.info("マルチモーダル分析エージェント作成開始")

    try:
        load_vertex_ai_config(logger)
        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="MultimodalAnalyst",
            instruction="""
            あなたは画像と音声の両方を分析できる子育て記録専門AIです。
            専門領域:
            - 子どもの画像分析（表情、行動、成長記録）
            - 音声テキスト分析（育児記録、親の状況）
            - マルチモーダル情報の統合分析
            - 子育て状況の包括的理解

            対応方針:
            1. 提供された画像または音声を適切なツールで分析
            2. 分析結果を子育ての文脈で解釈
            3. 年齢・発達段階を考慮した洞察を提供
            4. 必要に応じて他の専門エージェントへの相談を推奨
            5. 安全性に関わる懸念がある場合は医療機関への相談を推奨

            分析の種類:
            - 画像分析: 子どもの表情、行動、成長の様子、育児環境
            - 音声分析: 育児記録、親の感情状態、子どもの状況
            - 総合分析: 画像と音声の組み合わせによる包括的理解

            常に優しく、専門的で実践的な分析を提供してください。
            親の不安を和らげ、子育ての喜びを発見できるよう支援してください。
            """.strip(),
            tools=[image_analysis_tool, voice_analysis_tool],
        )

        logger.info("マルチモーダル分析エージェント作成完了")
        return agent

    except Exception as e:
        logger.error(f"マルチモーダルエージェント作成エラー: {e}")
        raise
