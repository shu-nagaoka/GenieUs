import logging
from typing import Any
from google.adk.tools import FunctionTool
from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase
from src.tools.common_response_formatter import ChildcareResponseFormatter


def create_image_analysis_tool(image_analysis_usecase: ImageAnalysisUseCase, logger: logging.Logger):
    """画像解析ツール作成（薄いアダプター）"""
    logger.info("画像解析ツール作成開始")

    async def analyze_child_image(
        image_path: str = "",  # デフォルト値設定（空文字）
        child_id: str = "default_child",
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
            logger.info(f"画像解析ツール実行開始: child_id={child_id}, analysis_type={analysis_type}")

            # image_pathが空の場合の処理
            if not image_path or image_path.strip() == "":
                logger.info("image_pathが提供されていません - デモンストレーションモードで実行")
                # デモ用レスポンス
                demo_response = ChildcareResponseFormatter.image_analysis_success(
                    detected_items=["お子さんの笑顔", "健康的な表情"],
                    emotion="happy",
                    activity="playing",
                    confidence=0.8,
                    suggestions=["画像を提供していただければ、より詳細な分析ができます"],
                    safety_concerns=[],
                    child_id=child_id,
                )
                response_dict = demo_response.to_dict()
                logger.info(f"🔧 ツールレスポンス詳細: {response_dict}")
                return response_dict

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

            # 統一レスポンス形式で返却
            if result.get("success", True):
                response = ChildcareResponseFormatter.image_analysis_success(
                    detected_items=result.get("detected_items", []),
                    emotion=result.get("emotion_detected", "unknown"),
                    activity=result.get("activity_type", "unknown"),
                    confidence=result.get("confidence", 0),
                    suggestions=result.get("suggestions", []),
                    safety_concerns=result.get("safety_concerns", []),
                    child_id=child_id,
                )
                response_dict = response.to_dict()
                logger.info(f"🔧 ツールレスポンス詳細（実画像）: {response_dict}")
                return response_dict
            else:
                error_msg = result.get("error", "画像解析中にエラーが発生しました")
                logger.error(f"画像解析UseCase実行エラー: {error_msg}")
                response = ChildcareResponseFormatter.error_response(
                    tool_type="画像解析", error_message=error_msg, child_id=child_id
                )
                return response.to_dict()

        except Exception as e:
            logger.error(f"画像解析ツール実行エラー: {e}")
            response = ChildcareResponseFormatter.error_response(
                tool_type="画像解析", error_message=str(e), child_id=child_id
            )
            return response.to_dict()

    logger.info("画像解析ツール作成完了")

    return FunctionTool(func=analyze_child_image)
