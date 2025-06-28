"""食事記録API

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- Composition Root + Depends統合
- 段階的エラーハンドリング
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.application.usecases.meal_record_usecase import (
    CreateMealRecordRequest,
    MealRecordUseCase,
    SearchMealRecordsRequest,
    UpdateMealRecordRequest,
)
from src.presentation.api.dependencies import get_meal_record_usecase, get_logger


router = APIRouter(prefix="/meal-records", tags=["meal-records"])


# リクエスト・レスポンスモデル
class CreateMealRecordRequestModel(BaseModel):
    """食事記録作成リクエストモデル"""

    child_id: str = Field(..., description="子どもID")
    meal_name: str = Field(..., description="食事名")
    meal_type: str = Field(..., description="食事タイプ (breakfast/lunch/dinner/snack)")
    detected_foods: list[str] | None = Field(None, description="検出された食材リスト")
    nutrition_info: dict[str, Any] | None = Field(None, description="栄養情報")
    detection_source: str = Field("manual", description="検出ソース (manual/image_ai/voice_ai)")
    confidence: float = Field(1.0, description="AI検出信頼度", ge=0.0, le=1.0)
    image_path: str | None = Field(None, description="画像パス")
    notes: str | None = Field(None, description="メモ")
    timestamp: str | None = Field(None, description="食事時刻 (ISO形式)")


class UpdateMealRecordRequestModel(BaseModel):
    """食事記録更新リクエストモデル"""

    meal_name: str | None = Field(None, description="食事名")
    meal_type: str | None = Field(None, description="食事タイプ")
    detected_foods: list[str] | None = Field(None, description="検出された食材リスト")
    nutrition_info: dict[str, Any] | None = Field(None, description="栄養情報")
    notes: str | None = Field(None, description="メモ")


class MealRecordResponseModel(BaseModel):
    """食事記録レスポンスモデル"""

    success: bool
    meal_record: dict[str, Any] | None = None
    error: str | None = None


class MealRecordListResponseModel(BaseModel):
    """食事記録一覧レスポンスモデル"""

    success: bool
    meal_records: list[dict[str, Any]] | None = None
    total_count: int = 0
    error: str | None = None


class NutritionSummaryResponseModel(BaseModel):
    """栄養サマリーレスポンスモデル"""

    success: bool
    summary: dict[str, Any] | None = None
    error: str | None = None


@router.post("/", response_model=MealRecordResponseModel)
async def create_meal_record(
    request_data: CreateMealRecordRequestModel,
    meal_record_usecase: MealRecordUseCase = Depends(get_meal_record_usecase),
    logger: logging.Logger = Depends(get_logger),
) -> MealRecordResponseModel:
    """食事記録作成

    Args:
        request_data: 食事記録作成リクエスト
        meal_record_usecase: DIから注入される食事記録UseCase
        logger: DIから注入されるロガー

    Returns:
        MealRecordResponseModel: 作成結果

    Raises:
        HTTPException: バリデーションエラー・作成失敗時
    """
    try:
        logger.info(f"🍽️ 食事記録作成API: {request_data.meal_name}")

        # タイムスタンプ変換
        timestamp = None
        if request_data.timestamp:
            try:
                timestamp = datetime.fromisoformat(request_data.timestamp.replace("Z", "+00:00"))
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {request_data.timestamp}")

        # UseCase呼び出し
        usecase_request = CreateMealRecordRequest(
            child_id=request_data.child_id,
            meal_name=request_data.meal_name,
            meal_type=request_data.meal_type,
            detected_foods=request_data.detected_foods,
            nutrition_info=request_data.nutrition_info,
            detection_source=request_data.detection_source,
            confidence=request_data.confidence,
            image_path=request_data.image_path,
            notes=request_data.notes,
            timestamp=timestamp,
        )

        result = await meal_record_usecase.create_meal_record(usecase_request)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)

        logger.info(f"✅ 食事記録作成API完了: {result.meal_record['id'] if result.meal_record else 'N/A'}")
        return MealRecordResponseModel(success=True, meal_record=result.meal_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 食事記録作成API内部エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{meal_record_id}", response_model=MealRecordResponseModel)
async def get_meal_record(
    meal_record_id: str,
    meal_record_usecase: MealRecordUseCase = Depends(get_meal_record_usecase),
    logger: logging.Logger = Depends(get_logger),
) -> MealRecordResponseModel:
    """食事記録取得

    Args:
        meal_record_id: 食事記録ID
        meal_record_usecase: DIから注入される食事記録UseCase
        logger: DIから注入されるロガー

    Returns:
        MealRecordResponseModel: 取得結果

    Raises:
        HTTPException: 記録が見つからない場合
    """
    try:
        logger.debug(f"🔍 食事記録取得API: {meal_record_id}")

        result = await meal_record_usecase.get_meal_record(meal_record_id)

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(status_code=404, detail=result.error)
            else:
                raise HTTPException(status_code=400, detail=result.error)

        return MealRecordResponseModel(success=True, meal_record=result.meal_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 食事記録取得API内部エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{meal_record_id}", response_model=MealRecordResponseModel)
async def update_meal_record(
    meal_record_id: str,
    request_data: UpdateMealRecordRequestModel,
    meal_record_usecase: MealRecordUseCase = Depends(get_meal_record_usecase),
    logger: logging.Logger = Depends(get_logger),
) -> MealRecordResponseModel:
    """食事記録更新

    Args:
        meal_record_id: 食事記録ID
        request_data: 更新リクエスト
        meal_record_usecase: DIから注入される食事記録UseCase
        logger: DIから注入されるロガー

    Returns:
        MealRecordResponseModel: 更新結果

    Raises:
        HTTPException: 記録が見つからない・更新失敗時
    """
    try:
        logger.info(f"📝 食事記録更新API: {meal_record_id}")

        # UseCase呼び出し
        usecase_request = UpdateMealRecordRequest(
            meal_record_id=meal_record_id,
            meal_name=request_data.meal_name,
            meal_type=request_data.meal_type,
            detected_foods=request_data.detected_foods,
            nutrition_info=request_data.nutrition_info,
            notes=request_data.notes,
        )

        result = await meal_record_usecase.update_meal_record(usecase_request)

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(status_code=404, detail=result.error)
            else:
                raise HTTPException(status_code=400, detail=result.error)

        logger.info(f"✅ 食事記録更新API完了: {meal_record_id}")
        return MealRecordResponseModel(success=True, meal_record=result.meal_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 食事記録更新API内部エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{meal_record_id}", response_model=MealRecordResponseModel)
async def delete_meal_record(
    meal_record_id: str,
    meal_record_usecase: MealRecordUseCase = Depends(get_meal_record_usecase),
    logger: logging.Logger = Depends(get_logger),
) -> MealRecordResponseModel:
    """食事記録削除

    Args:
        meal_record_id: 食事記録ID
        meal_record_usecase: DIから注入される食事記録UseCase
        logger: DIから注入されるロガー

    Returns:
        MealRecordResponseModel: 削除結果

    Raises:
        HTTPException: 記録が見つからない・削除失敗時
    """
    try:
        logger.info(f"🗑️ 食事記録削除API: {meal_record_id}")

        result = await meal_record_usecase.delete_meal_record(meal_record_id)

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(status_code=404, detail=result.error)
            else:
                raise HTTPException(status_code=400, detail=result.error)

        logger.info(f"✅ 食事記録削除API完了: {meal_record_id}")
        return MealRecordResponseModel(success=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 食事記録削除API内部エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=MealRecordListResponseModel)
async def search_meal_records(
    child_id: str = Query(..., description="子どもID"),
    start_date: str | None = Query(None, description="開始日時 (ISO形式)"),
    end_date: str | None = Query(None, description="終了日時 (ISO形式)"),
    meal_type: str | None = Query(None, description="食事タイプ"),
    limit: int = Query(50, description="取得件数上限", ge=1, le=1000),
    offset: int = Query(0, description="オフセット", ge=0),
    meal_record_usecase: MealRecordUseCase = Depends(get_meal_record_usecase),
    logger: logging.Logger = Depends(get_logger),
) -> MealRecordListResponseModel:
    """食事記録検索

    Args:
        child_id: 子どもID
        start_date: 開始日時
        end_date: 終了日時
        meal_type: 食事タイプ
        limit: 取得件数上限
        offset: オフセット
        meal_record_usecase: DIから注入される食事記録UseCase
        logger: DIから注入されるロガー

    Returns:
        MealRecordListResponseModel: 検索結果

    Raises:
        HTTPException: バリデーションエラー・検索失敗時
    """
    try:
        logger.debug(f"🔍 食事記録検索API: child_id={child_id}")

        # 日時変換
        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}")

        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}")

        # UseCase呼び出し
        usecase_request = SearchMealRecordsRequest(
            child_id=child_id,
            start_date=start_datetime,
            end_date=end_datetime,
            meal_type=meal_type,
            limit=limit,
            offset=offset,
        )

        result = await meal_record_usecase.search_meal_records(usecase_request)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)

        logger.debug(f"✅ 食事記録検索API完了: {result.total_count}件")
        return MealRecordListResponseModel(
            success=True, meal_records=result.meal_records, total_count=result.total_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 食事記録検索API内部エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/nutrition-summary/{child_id}", response_model=NutritionSummaryResponseModel)
async def get_nutrition_summary(
    child_id: str,
    start_date: str | None = Query(None, description="開始日時 (ISO形式)"),
    end_date: str | None = Query(None, description="終了日時 (ISO形式)"),
    meal_record_usecase: MealRecordUseCase = Depends(get_meal_record_usecase),
    logger: logging.Logger = Depends(get_logger),
) -> NutritionSummaryResponseModel:
    """栄養サマリー取得

    Args:
        child_id: 子どもID
        start_date: 開始日時
        end_date: 終了日時
        meal_record_usecase: DIから注入される食事記録UseCase
        logger: DIから注入されるロガー

    Returns:
        NutritionSummaryResponseModel: 栄養サマリー

    Raises:
        HTTPException: バリデーションエラー・取得失敗時
    """
    try:
        logger.info(f"📊 栄養サマリー取得API: child_id={child_id}")

        # 日時変換
        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}")

        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}")

        # UseCase呼び出し
        result = await meal_record_usecase.get_nutrition_summary(
            child_id=child_id, start_date=start_datetime, end_date=end_datetime
        )

        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)

        logger.info(f"✅ 栄養サマリー取得API完了: child_id={child_id}")
        return NutritionSummaryResponseModel(success=True, summary=result.summary)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 栄養サマリー取得API内部エラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
