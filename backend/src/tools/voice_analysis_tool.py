"""音声分析Tool - UseCase層の薄いラッパー"""

import logging
from typing import Any

from google.adk.tools import FunctionTool

from src.application.usecases.voice_analysis_usecase import VoiceAnalysisUseCase


def create_voice_analysis_tool(voice_analysis_usecase: VoiceAnalysisUseCase, logger: logging.Logger) -> FunctionTool:
    """音声分析ツール作成（薄いアダプター）

    Args:
        voice_analysis_usecase: 音声分析UseCase
        logger: ロガー（DIコンテナから注入）

    Returns:
        FunctionTool: ADK用音声分析ツール

    """
    logger.info("音声分析ツール作成開始")

    async def analyze_child_voice(
        voice_text: str,
        child_id: str = "default_child",
        analysis_type: str = "general",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """子どもの音声テキストを分析してデータを抽出

        Args:
            voice_text: 音声認識されたテキスト
            child_id: 子どものID（デフォルト: "default_child"）
            analysis_type: 分析タイプ（general, feeding, sleep等）
            **kwargs: 追加のコンテキスト情報

        Returns:
            Dict[str, Any]: 分析結果

        """
        try:
            logger.info(
                f"音声分析ツール実行開始: child_id={child_id}, analysis_type={analysis_type}, text_length={len(voice_text)}",
            )

            # コンテキスト情報の構築
            analysis_context = {
                "analysis_type": analysis_type,
                **kwargs,  # user_id, session_id等の追加情報
            }

            # UseCase層の呼び出し
            result = await voice_analysis_usecase.analyze_child_voice(
                voice_text=voice_text,
                child_id=child_id,
                analysis_context=analysis_context,
            )

            # ADK用レスポンス変換（自然言語形式）
            if result.get("success", True):
                return {
                    "success": True,
                    "response": _create_natural_language_response(result),
                    "analysis_data": result,
                    "metadata": {
                        "child_id": child_id,
                        "analysis_type": analysis_type,
                        "confidence": result.get("overall_confidence", 0),
                        "events_count": len(result.get("events", [])),
                        "emotional_tone": result.get("emotional_tone", "unknown"),
                    },
                }
            else:
                error_msg = result.get("error", "音声解析中にエラーが発生しました")
                logger.error(f"音声分析UseCase実行エラー: {error_msg}")
                return {
                    "success": False,
                    "response": f"申し訳ございません。{error_msg}",
                    "metadata": {"child_id": child_id, "analysis_type": analysis_type},
                }

        except Exception as e:
            logger.error(f"音声分析ツール実行エラー: {e}")
            return {
                "success": False,
                "response": "申し訳ございません。音声解析中に問題が発生しました。",
                "metadata": {"child_id": child_id, "error": str(e)},
            }

    def _create_natural_language_response(analysis_result: dict[str, Any]) -> str:
        """分析結果を自然言語レスポンスに変換"""
        events = analysis_result.get("events", [])
        confidence = analysis_result.get("overall_confidence", 0)
        insights = analysis_result.get("insights", [])
        emotional_tone = analysis_result.get("emotional_tone", "unknown")

        response_parts = []

        # 基本的な分析結果
        if events:
            response_parts.append(f"音声から{len(events)}件の育児記録を検出しました:")
            for i, event in enumerate(events[:3]):  # 最大3件表示
                event_type = event.get("type", "記録")
                description = event.get("description", "詳細情報")
                event_confidence = event.get("confidence", 0)
                confidence_text = (
                    "高精度" if event_confidence > 0.7 else "中精度" if event_confidence > 0.4 else "参考程度"
                )
                response_parts.append(f"  {i + 1}. {event_type}: {description} ({confidence_text})")
        else:
            response_parts.append("音声から具体的な育児記録は検出されませんでした")

        # 感情トーンの報告
        tone_text = {
            "positive": "ポジティブ",
            "neutral": "落ち着いている",
            "concerned": "心配気味",
            "unknown": "不明",
        }.get(emotional_tone, "不明")
        response_parts.append(f"🎭 音声の感情トーン: {tone_text}")

        # 全体信頼度の表示
        confidence_text = "高い" if confidence > 0.7 else "中程度" if confidence > 0.4 else "低い"
        response_parts.append(f"📊 分析の信頼度: {confidence_text}")

        # インサイト
        if insights:
            response_parts.append(f"💡 分析結果: {insights[0]}")

        return "\\n".join(response_parts)

    logger.info("音声分析ツール作成完了")
    return FunctionTool(
        func=analyze_child_voice,
    )
