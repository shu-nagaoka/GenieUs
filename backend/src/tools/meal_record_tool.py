"""食事記録管理ツール - ADK FunctionTool統合

エージェントが食事記録の作成・編集・削除・検索を行えるツール
画像解析やHuman-in-the-Loopと統合した食事記録機能
"""

import logging
from datetime import datetime
from typing import Any

from google.adk.tools import FunctionTool

from src.application.usecases.meal_record_usecase import (
    CreateMealRecordRequest,
    MealRecordUseCase,
    SearchMealRecordsRequest,
    UpdateMealRecordRequest,
)
from src.domain.entities import FoodDetectionSource, MealType


def create_meal_record_tool(meal_record_usecase: MealRecordUseCase, logger: logging.Logger):
    """食事記録管理ツール作成（薄いアダプター）"""
    logger.info("食事記録管理ツール作成開始")

    async def manage_meal_records(
        action: str = "create",
        child_id: str = "default_child",
        meal_name: str = "",
        meal_type: str = "snack",
        detected_foods: list[str] = None,
        nutrition_info: dict = None,
        detection_source: str = "image_ai",
        confidence: float = 0.8,
        image_path: str = "",
        notes: str = "画像解析により自動検出された食事記録",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """食事記録の管理（作成・検索・更新・削除）

        Args:
            action: 実行アクション (create/search/update/delete)
            child_id: 子どものID
            meal_name: 食事名
            meal_type: 食事タイプ (breakfast/lunch/dinner/snack)
            detected_foods: 検出された食材リスト
            nutrition_info: 栄養情報
            detection_source: 検出ソース (manual/image_ai/voice_ai)
            confidence: AI検出信頼度
            image_path: 画像パス
            notes: メモ
            **kwargs: 追加のコンテキスト情報

        Returns:
            Dict[str, Any]: 実行結果
        """
        try:
            logger.info(f"🍽️ 食事記録管理ツール実行: {action} - {meal_name}")

            # デフォルト値設定
            if detected_foods is None:
                detected_foods = []
            if nutrition_info is None:
                nutrition_info = {}

            if action == "create":
                return await _create_meal_record(
                    meal_record_usecase,
                    logger,
                    child_id,
                    meal_name,
                    meal_type,
                    detected_foods,
                    nutrition_info,
                    detection_source,
                    confidence,
                    image_path,
                    notes,
                )
            elif action == "search":
                return await _search_meal_records(meal_record_usecase, logger, child_id, **kwargs)
            elif action == "update":
                return await _update_meal_record(meal_record_usecase, logger, **kwargs)
            elif action == "delete":
                return await _delete_meal_record(meal_record_usecase, logger, **kwargs)
            else:
                error_msg = f"Unknown action: {action}"
                logger.error(f"❌ {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"食事記録管理ツール実行エラー: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    logger.info("食事記録管理ツール作成完了")
    return FunctionTool(func=manage_meal_records)


async def _create_meal_record(
    meal_record_usecase: MealRecordUseCase,
    logger: logging.Logger,
    child_id: str,
    meal_name: str,
    meal_type: str,
    detected_foods: list[str],
    nutrition_info: dict,
    detection_source: str,
    confidence: float,
    image_path: str,
    notes: str,
) -> dict[str, Any]:
    """食事記録作成"""
    try:
        logger.info(f"🍽️ 食事記録作成開始: {meal_name}")

        # Enum値の変換
        try:
            meal_type_enum = MealType(meal_type)
        except ValueError:
            meal_type_enum = MealType.SNACK  # デフォルト

        try:
            detection_source_enum = FoodDetectionSource(detection_source)
        except ValueError:
            detection_source_enum = FoodDetectionSource.IMAGE_AI  # デフォルト

        # UseCase実行
        request = CreateMealRecordRequest(
            child_id=child_id,
            meal_name=meal_name,
            meal_type=meal_type_enum,
            detected_foods=detected_foods,
            nutrition_info=nutrition_info,
            detection_source=detection_source_enum,
            confidence=confidence,
            image_path=image_path if image_path else None,
            notes=notes,
            timestamp=None,  # 現在時刻を使用
        )

        result = await meal_record_usecase.create_meal_record(request)

        if not result.success:
            logger.error(f"❌ 食事記録作成失敗: {result.error}")
            return {"success": False, "error": result.error}

        logger.info(f"✅ 食事記録作成成功: {result.meal_record['id'] if result.meal_record else 'N/A'}")
        return {
            "success": True,
            "meal_record_id": result.meal_record["id"] if result.meal_record else None,
            "message": f"食事記録「{meal_name}」を作成しました",
            "meal_record": result.meal_record,
        }

    except Exception as e:
        logger.error(f"❌ 食事記録作成エラー: {e}")
        return {"success": False, "error": f"食事記録の作成に失敗しました: {str(e)}"}


async def _search_meal_records(
    meal_record_usecase: MealRecordUseCase, logger: logging.Logger, child_id: str, **kwargs
) -> dict[str, Any]:
    """食事記録検索"""
    try:
        logger.info(f"🔍 食事記録検索開始: child_id={child_id}")

        # 日付変換
        start_date = None
        end_date = None
        if kwargs.get("start_date"):
            try:
                start_date = datetime.fromisoformat(kwargs["start_date"])
            except ValueError:
                pass

        if kwargs.get("end_date"):
            try:
                end_date = datetime.fromisoformat(kwargs["end_date"])
            except ValueError:
                pass

        # 食事タイプ変換
        meal_type = None
        if kwargs.get("meal_type"):
            try:
                meal_type = MealType(kwargs["meal_type"])
            except ValueError:
                pass

        # UseCase実行
        request = SearchMealRecordsRequest(
            child_id=child_id,
            start_date=start_date,
            end_date=end_date,
            meal_type=meal_type,
            limit=int(kwargs.get("limit", 50)),
            offset=int(kwargs.get("offset", 0)),
        )

        result = await meal_record_usecase.search_meal_records(request)

        if not result.success:
            logger.error(f"❌ 食事記録検索失敗: {result.error}")
            return {"success": False, "error": result.error}

        logger.info(f"✅ 食事記録検索成功: {result.total_count}件")
        return {
            "success": True,
            "total_count": result.total_count,
            "meal_records": result.meal_records,
        }

    except Exception as e:
        logger.error(f"❌ 食事記録検索エラー: {e}")
        return {"success": False, "error": f"食事記録の検索に失敗しました: {str(e)}"}


async def _update_meal_record(
    meal_record_usecase: MealRecordUseCase, logger: logging.Logger, **kwargs
) -> dict[str, Any]:
    """食事記録更新"""
    try:
        meal_record_id = kwargs.get("meal_record_id")
        if not meal_record_id:
            return {"success": False, "error": "meal_record_id が必要です"}

        logger.info(f"📝 食事記録更新開始: {meal_record_id}")

        # 食事タイプ変換
        meal_type = None
        if kwargs.get("meal_type"):
            try:
                meal_type = MealType(kwargs["meal_type"])
            except ValueError:
                pass

        # UseCase実行
        request = UpdateMealRecordRequest(
            meal_record_id=meal_record_id,
            meal_name=kwargs.get("meal_name"),
            meal_type=meal_type,
            detected_foods=kwargs.get("detected_foods"),
            nutrition_info=kwargs.get("nutrition_info"),
            notes=kwargs.get("notes"),
        )

        result = await meal_record_usecase.update_meal_record(request)

        if not result.success:
            logger.error(f"❌ 食事記録更新失敗: {result.error}")
            return {"success": False, "error": result.error}

        logger.info(f"✅ 食事記録更新成功: {meal_record_id}")
        return {
            "success": True,
            "message": "食事記録を更新しました",
            "meal_record": result.meal_record,
        }

    except Exception as e:
        logger.error(f"❌ 食事記録更新エラー: {e}")
        return {"success": False, "error": f"食事記録の更新に失敗しました: {str(e)}"}


async def _delete_meal_record(
    meal_record_usecase: MealRecordUseCase, logger: logging.Logger, **kwargs
) -> dict[str, Any]:
    """食事記録削除"""
    try:
        meal_record_id = kwargs.get("meal_record_id")
        if not meal_record_id:
            return {"success": False, "error": "meal_record_id が必要です"}

        logger.info(f"🗑️ 食事記録削除開始: {meal_record_id}")

        result = await meal_record_usecase.delete_meal_record(meal_record_id)

        if not result.success:
            logger.error(f"❌ 食事記録削除失敗: {result.error}")
            return {"success": False, "error": result.error}

        logger.info(f"✅ 食事記録削除成功: {meal_record_id}")
        return {"success": True, "message": "食事記録を削除しました"}

    except Exception as e:
        logger.error(f"❌ 食事記録削除エラー: {e}")
        return {"success": False, "error": f"食事記録の削除に失敗しました: {str(e)}"}
