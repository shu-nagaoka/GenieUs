"""Meal Management Integration Tool - 食事管理統合ツール

画像分析結果をもとにHuman-in-the-Loop確認を実行し、
食事管理システムへの登録を行うツール
"""

import logging
from typing import Any, Dict

from google.adk.tools import FunctionTool
from src.application.usecases.interactive_confirmation_usecase import InteractiveConfirmationUseCase


def create_meal_management_integration_tool(
    interactive_confirmation_usecase: InteractiveConfirmationUseCase,
    logger: logging.Logger,
):
    """食事管理統合ツール作成（薄いアダプター）"""
    logger.info("食事管理統合ツール作成開始")

    async def register_meal_with_confirmation(
        suggested_meal_data: dict,
        registration_recommendation: str = "この食事を記録しますか？",
        user_id: str = "frontend_user",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """食事データの確認と登録

        Args:
            suggested_meal_data: 提案された食事データ
            registration_recommendation: 登録推奨メッセージ
            user_id: ユーザーID
            **kwargs: 追加のコンテキスト情報

        Returns:
            Dict[str, Any]: 確認リクエスト結果
        """
        try:
            logger.info(f"🍽️ 食事登録確認開始: {suggested_meal_data.get('meal_name', '不明な食事')}")

            # コンテキストデータを構築
            context_data = {
                "is_food_related": True,
                "suggested_meal_data": suggested_meal_data,
                "registration_recommendation": registration_recommendation,
                "user_id": user_id,
                **kwargs,
            }

            # Interactive Confirmation リクエストを作成
            confirmation_result = await interactive_confirmation_usecase.create_confirmation_request(
                question=registration_recommendation,
                options=["はい", "いいえ"],
                context_data=context_data,
                confirmation_type="yes_no",
                timeout_seconds=300,
            )

            if not confirmation_result.get("success", False):
                logger.error(f"❌ 確認リクエスト作成エラー: {confirmation_result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": f"確認リクエスト作成に失敗しました: {confirmation_result.get('error', 'Unknown error')}",
                    "requires_user_response": False,
                }

            # 確認データにコンテキストを追加
            confirmation_data = confirmation_result.get("confirmation_data", {})
            confirmation_data["context_data"] = context_data

            result = {
                "success": True,
                "message": confirmation_result.get("message", "食事登録の確認を表示しました"),
                "confirmation_data": confirmation_data,
                "requires_user_response": True,
                "response_format": confirmation_result.get("response_format", {}),
                "context_data": context_data,
            }

            logger.info(f"✅ 食事登録確認生成完了: {confirmation_data.get('confirmation_id', 'N/A')}")
            return result

        except Exception as e:
            logger.error(f"❌ 食事登録確認エラー: {e}")
            return {
                "success": False,
                "error": f"食事登録確認処理中にエラーが発生しました: {str(e)}",
                "requires_user_response": False,
            }

    logger.info("食事管理統合ツール作成完了")
    return FunctionTool(func=register_meal_with_confirmation)
