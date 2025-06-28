"""Interactive Confirmation UseCase - Human-in-the-Loop確認処理

ビジネスロジック層でのユーザー確認処理・食事管理統合を担当
"""

import logging
from typing import Dict

from src.application.usecases.meal_record_usecase import MealRecordUseCase, CreateMealRecordRequest
from src.domain.entities import MealType
from src.tools.interactive_confirmation_tool import InteractiveConfirmationTool


class InteractiveConfirmationUseCase:
    """Interactive Confirmation UseCase

    責務:
    - ユーザー確認処理のビジネスロジック
    - 食事管理統合処理
    - 後続アクション実行
    """

    def __init__(
        self,
        meal_record_usecase: MealRecordUseCase,
        logger: logging.Logger,
    ):
        """InteractiveConfirmationUseCase初期化

        Args:
            meal_record_usecase: 食事記録UseCase
            logger: DIコンテナから注入されるロガー
        """
        self.meal_record_usecase = meal_record_usecase
        self.logger = logger
        self._interactive_tool = InteractiveConfirmationTool(logger=logger)

    async def process_confirmation_response(
        self,
        confirmation_id: str,
        user_response: str,
        user_id: str,
        session_id: str,
        response_metadata: Dict = None,
    ) -> Dict:
        """ユーザー確認応答の処理

        Args:
            confirmation_id: 確認ID
            user_response: ユーザー応答
            user_id: ユーザーID
            session_id: セッションID
            response_metadata: 応答メタデータ

        Returns:
            Dict: 処理結果とフォローアップアクション
        """
        try:
            self.logger.info(f"🤝 確認応答処理開始: {confirmation_id} -> {user_response}")

            # ユーザー応答を処理
            process_result = await self._interactive_tool.process_user_response(
                confirmation_id=confirmation_id, user_response=user_response, response_metadata=response_metadata or {}
            )

            if not process_result.get("success", False):
                return {
                    "success": False,
                    "error": process_result.get("error", "応答処理エラー"),
                    "followup_action": {"action_type": "error"},
                }

            response_data = process_result["response_data"]
            followup_action = process_result["followup_action"]

            # 🍽️ 食事関連の場合は食事記録登録処理を実行
            if (
                followup_action.get("action_type") == "proceed"
                and response_data.get("is_positive")
                and response_metadata
                and response_metadata.get("context_data", {}).get("is_food_related")
            ):
                try:
                    await self._execute_meal_record_registration(response_metadata["context_data"], user_id)

                    followup_action["message"] = (
                        "✅ 美味しそうなお食事を記録させていただきました！栄養バランスの追跡にお役立てください。"
                    )

                except Exception as meal_error:
                    self.logger.error(f"❌ 食事記録登録エラー: {meal_error}")
                    followup_action["message"] = f"⚠️ 食事の記録中にエラーが発生しました: {meal_error}"

            return {
                "success": True,
                "message": process_result.get("message", "応答を正常に処理しました"),
                "followup_action": followup_action,
                "confirmation_id": confirmation_id,
                "timestamp": response_data.get("processed_at", ""),
                "response_data": response_data,
            }

        except Exception as e:
            self.logger.error(f"❌ 確認応答処理エラー: {e}")
            return {
                "success": False,
                "error": f"確認応答処理中にエラーが発生しました: {str(e)}",
                "followup_action": {"action_type": "error"},
            }

    async def create_confirmation_request(
        self,
        question: str,
        options: list = None,
        context_data: Dict = None,
        confirmation_type: str = "yes_no",
        timeout_seconds: int = 300,
    ) -> Dict:
        """確認リクエストの作成

        Args:
            question: 確認質問
            options: 選択肢
            context_data: コンテキストデータ
            confirmation_type: 確認タイプ
            timeout_seconds: タイムアウト時間（秒）

        Returns:
            Dict: 確認リクエストデータ
        """
        try:
            self.logger.info(f"🤝 確認リクエスト作成: {confirmation_type}")

            result = await self._interactive_tool.ask_user_confirmation(
                question=question,
                options=options,
                context_data=context_data,
                confirmation_type=confirmation_type,
                timeout_seconds=timeout_seconds,
            )

            return result

        except Exception as e:
            self.logger.error(f"❌ 確認リクエスト作成エラー: {e}")
            return {
                "success": False,
                "error": f"確認リクエスト作成中にエラーが発生しました: {str(e)}",
                "confirmation_data": None,
            }

    async def _execute_meal_record_registration(
        self,
        context_data: Dict,
        user_id: str,
    ) -> None:
        """食事記録登録を実行

        Args:
            context_data: 画像解析から取得した食事関連データ
            user_id: ユーザーID

        Raises:
            Exception: 登録処理エラー
        """
        try:
            self.logger.info(
                f"🍽️ 食事記録登録実行開始: {context_data.get('suggested_meal_data', {}).get('meal_name', '不明な食事')}"
            )

            # 食事データを構造化
            suggested_meal_data = context_data.get("suggested_meal_data", {})

            # 子どもIDの決定（デフォルトまたはcontextから取得）
            child_id = context_data.get("child_id", "default_child")

            # 食事タイプをMealTypeに変換
            meal_type_str = suggested_meal_data.get("estimated_meal_time", "snack")
            if meal_type_str not in ["breakfast", "lunch", "dinner", "snack"]:
                meal_type_str = "snack"

            # CreateMealRecordRequest作成
            meal_record_request = CreateMealRecordRequest(
                child_id=child_id,
                meal_name=suggested_meal_data.get("meal_name", "AI検出食事"),
                meal_type=meal_type_str,
                detected_foods=suggested_meal_data.get("detected_foods", []),
                nutrition_info=suggested_meal_data.get("nutrition_balance", {}),
                detection_source="image_ai",
                confidence=suggested_meal_data.get("confidence", 0.8),
                image_path=context_data.get("image_path"),
                notes="画像解析により自動検出された食事記録",
                timestamp=None,  # 現在時刻を使用
            )

            # 食事記録を作成
            creation_result = await self.meal_record_usecase.create_meal_record(meal_record_request)

            if not creation_result.success:
                raise Exception(f"食事記録作成エラー: {creation_result.error}")

            self.logger.info(
                f"✅ 食事記録登録完了: {creation_result.meal_record['id'] if creation_result.meal_record else 'N/A'}"
            )

        except Exception as e:
            self.logger.error(f"❌ 食事記録登録エラー: {e}")
            raise Exception(f"食事の記録に失敗しました: {str(e)}")
