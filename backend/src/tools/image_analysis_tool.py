"""画像解析Tool - UseCase層の薄いラッパー"""

import logging
from typing import Any

# Google ADK v1.2.1のFunctionToolバグにより、関数を直接返す方式を採用

from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase


def create_image_analysis_tool(image_analysis_usecase: ImageAnalysisUseCase, logger: logging.Logger):
    """画像解析ツール作成（薄いアダプター）

    Args:
        image_analysis_usecase: 画像解析UseCase
        logger: ロガー（DIコンテナから注入）

    Returns:
        FunctionTool: ADK用画像解析ツール

    """
    logger.info("画像解析ツール作成開始")

    async def analyze_child_image(
        image_path: str,
        child_id: str,
        analysis_type: str = "general",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """子どもの画像を分析してデータを抽出

        Args:
            image_path: 画像ファイルのパス
            child_id: 子どものID
            analysis_type: 分析タイプ（general, feeding, development等）
            **kwargs: 追加のコンテキスト情報

        Returns:
            Dict[str, Any]: 分析結果

        """
        try:
            logger.info(
                f"画像解析ツール実行開始: child_id={child_id}, analysis_type={analysis_type}, image_path長={len(image_path)}",
            )
            logger.info(f"image_path先頭100文字: {image_path[:100]}...")

            # コンテキスト情報の構築
            analysis_context = {
                "analysis_type": analysis_type,
                **kwargs,  # user_id, session_id等の追加情報
            }

            # UseCase層の呼び出し
            result = await image_analysis_usecase.analyze_child_image(
                image_path=image_path,
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
                        "confidence": result.get("confidence", 0),
                        "has_safety_concerns": result.get("has_safety_concerns", False),
                    },
                }
            else:
                error_msg = result.get("error", "画像解析中にエラーが発生しました")
                logger.error(f"画像解析UseCase実行エラー: {error_msg}")
                return {
                    "success": False,
                    "response": f"申し訳ございません。{error_msg}",
                    "metadata": {"child_id": child_id, "analysis_type": analysis_type},
                }

        except Exception as e:
            logger.error(f"画像解析ツール実行エラー: {e}")
            return {
                "success": False,
                "response": "申し訳ございません。画像解析中に問題が発生しました。",
                "metadata": {"child_id": child_id, "error": str(e)},
            }

    def _create_natural_language_response(analysis_result: dict[str, Any]) -> str:
        """分析結果を自然言語レスポンスに変換"""
        detected_items = analysis_result.get("detected_items", [])
        emotion = analysis_result.get("emotion_detected", "不明")
        activity = analysis_result.get("activity_type", "不明")
        confidence = analysis_result.get("confidence", 0)
        suggestions = analysis_result.get("suggestions", [])
        safety_concerns = analysis_result.get("safety_concerns", [])

        response_parts = []

        # 基本的な分析結果
        if detected_items:
            items_text = "、".join(detected_items[:3])  # 最大3項目
            response_parts.append(f"画像から以下が検出されました: {items_text}")

        # 感情・活動の報告
        if emotion != "unknown":
            response_parts.append(f"お子さんの様子: {emotion}")

        if activity != "unknown":
            response_parts.append(f"活動内容: {activity}")

        # 信頼度の表示
        confidence_text = "高い" if confidence > 0.7 else "中程度" if confidence > 0.4 else "低い"
        response_parts.append(f"分析の信頼度: {confidence_text}")

        # 安全性の懸念
        if safety_concerns:
            response_parts.append(f"⚠️ 安全性に関する注意点: {safety_concerns[0]}")

        # アドバイス
        if suggestions:
            response_parts.append(f"💡 アドバイス: {suggestions[0]}")

        return "\n".join(response_parts)

    logger.info("画像解析ツール作成完了")
    
    # FunctionToolオブジェクトを正しく返す
    from google.adk.tools import FunctionTool
    return FunctionTool(func=analyze_child_image)
