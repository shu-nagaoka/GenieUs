"""食事記録UseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from src.application.interface.protocols.meal_record_repository import MealRecordRepositoryProtocol
from src.domain.entities import MealRecord, MealType, FoodDetectionSource


@dataclass
class CreateMealRecordRequest:
    """食事記録作成リクエスト"""

    child_id: str
    meal_name: str
    meal_type: str
    detected_foods: list[str] | None = None
    nutrition_info: dict[str, Any] | None = None
    detection_source: str = "manual"
    confidence: float = 1.0
    image_path: str | None = None
    notes: str | None = None
    timestamp: datetime | None = None


@dataclass
class UpdateMealRecordRequest:
    """食事記録更新リクエスト"""

    meal_record_id: str
    meal_name: str | None = None
    meal_type: str | None = None
    detected_foods: list[str] | None = None
    nutrition_info: dict[str, Any] | None = None
    notes: str | None = None


@dataclass
class SearchMealRecordsRequest:
    """食事記録検索リクエスト"""

    child_id: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    meal_type: str | None = None
    limit: int = 50
    offset: int = 0


@dataclass
class MealRecordResponse:
    """食事記録レスポンス"""

    success: bool
    meal_record: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class MealRecordListResponse:
    """食事記録一覧レスポンス"""

    success: bool
    meal_records: list[dict[str, Any]] | None = None
    total_count: int = 0
    error: str | None = None


@dataclass
class NutritionSummaryResponse:
    """栄養サマリーレスポンス"""

    success: bool
    summary: dict[str, Any] | None = None
    error: str | None = None


class MealRecordUseCase:
    """食事記録UseCase

    責務:
    - 個別食事記録のCRUD操作
    - 栄養情報の集計・分析
    - 検索・フィルタリング機能
    """

    def __init__(
        self,
        meal_record_repository: MealRecordRepositoryProtocol,
        logger: logging.Logger,
    ):
        """MealRecordUseCase初期化

        Args:
            meal_record_repository: 食事記録リポジトリ
            logger: DIコンテナから注入されるロガー
        """
        self.meal_record_repository = meal_record_repository
        self.logger = logger

    async def create_meal_record(self, request: CreateMealRecordRequest) -> MealRecordResponse:
        """食事記録作成

        Args:
            request: 食事記録作成リクエスト

        Returns:
            MealRecordResponse: 作成結果
        """
        try:
            self.logger.info(f"🍽️ 食事記録作成開始: {request.meal_name}")

            # バリデーション
            if not request.child_id.strip():
                return MealRecordResponse(success=False, error="child_id is required")

            if not request.meal_name.strip():
                return MealRecordResponse(success=False, error="meal_name is required")

            # MealRecord エンティティ作成
            meal_record = MealRecord(
                child_id=request.child_id,
                meal_name=request.meal_name,
                meal_type=MealType(request.meal_type),
                detected_foods=request.detected_foods or [],
                nutrition_info=request.nutrition_info or {},
                detection_source=FoodDetectionSource(request.detection_source),
                confidence=request.confidence,
                image_path=request.image_path,
                notes=request.notes,
                timestamp=request.timestamp or datetime.now(),
            )

            # リポジトリに保存
            saved_record = await self.meal_record_repository.create(meal_record)

            self.logger.info(f"✅ 食事記録作成完了: {saved_record.id}")
            return MealRecordResponse(success=True, meal_record=saved_record.to_dict())

        except ValueError as e:
            self.logger.error(f"❌ 食事記録バリデーションエラー: {e}")
            return MealRecordResponse(success=False, error=f"Invalid input: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ 食事記録作成エラー: {e}")
            return MealRecordResponse(success=False, error=f"Failed to create meal record: {str(e)}")

    async def get_meal_record(self, meal_record_id: str) -> MealRecordResponse:
        """食事記録取得

        Args:
            meal_record_id: 食事記録ID

        Returns:
            MealRecordResponse: 取得結果
        """
        try:
            self.logger.info(f"🔍 食事記録取得: {meal_record_id}")

            meal_record = await self.meal_record_repository.get_by_id(meal_record_id)

            if not meal_record:
                return MealRecordResponse(success=False, error="Meal record not found")

            return MealRecordResponse(success=True, meal_record=meal_record.to_dict())

        except Exception as e:
            self.logger.error(f"❌ 食事記録取得エラー: {e}")
            return MealRecordResponse(success=False, error=f"Failed to get meal record: {str(e)}")

    async def update_meal_record(self, request: UpdateMealRecordRequest) -> MealRecordResponse:
        """食事記録更新

        Args:
            request: 食事記録更新リクエスト

        Returns:
            MealRecordResponse: 更新結果
        """
        try:
            self.logger.info(f"📝 食事記録更新: {request.meal_record_id}")

            # 既存記録取得
            meal_record = await self.meal_record_repository.get_by_id(request.meal_record_id)
            if not meal_record:
                return MealRecordResponse(success=False, error="Meal record not found")

            # 更新データ適用
            if request.meal_name is not None:
                meal_record.meal_name = request.meal_name
            if request.meal_type is not None:
                meal_record.meal_type = MealType(request.meal_type)
            if request.detected_foods is not None:
                meal_record.detected_foods = request.detected_foods
            if request.nutrition_info is not None:
                meal_record.update_nutrition_info(request.nutrition_info)
            if request.notes is not None:
                meal_record.add_note(request.notes)

            # 更新時刻設定
            meal_record.updated_at = datetime.now()

            # リポジトリに保存
            updated_record = await self.meal_record_repository.update(meal_record)

            self.logger.info(f"✅ 食事記録更新完了: {updated_record.id}")
            return MealRecordResponse(success=True, meal_record=updated_record.to_dict())

        except ValueError as e:
            self.logger.error(f"❌ 食事記録更新バリデーションエラー: {e}")
            return MealRecordResponse(success=False, error=f"Invalid input: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ 食事記録更新エラー: {e}")
            return MealRecordResponse(success=False, error=f"Failed to update meal record: {str(e)}")

    async def delete_meal_record(self, meal_record_id: str) -> MealRecordResponse:
        """食事記録削除

        Args:
            meal_record_id: 食事記録ID

        Returns:
            MealRecordResponse: 削除結果
        """
        try:
            self.logger.info(f"🗑️ 食事記録削除: {meal_record_id}")

            success = await self.meal_record_repository.delete(meal_record_id)

            if not success:
                return MealRecordResponse(success=False, error="Meal record not found or failed to delete")

            self.logger.info(f"✅ 食事記録削除完了: {meal_record_id}")
            return MealRecordResponse(success=True)

        except Exception as e:
            self.logger.error(f"❌ 食事記録削除エラー: {e}")
            return MealRecordResponse(success=False, error=f"Failed to delete meal record: {str(e)}")

    async def search_meal_records(self, request: SearchMealRecordsRequest) -> MealRecordListResponse:
        """食事記録検索

        Args:
            request: 検索リクエスト

        Returns:
            MealRecordListResponse: 検索結果
        """
        try:
            self.logger.info(f"🔍 食事記録検索: child_id={request.child_id}")

            meal_records = await self.meal_record_repository.search(
                child_id=request.child_id,
                start_date=request.start_date,
                end_date=request.end_date,
                meal_type=MealType(request.meal_type) if request.meal_type else None,
                limit=request.limit,
                offset=request.offset,
            )

            total_count = await self.meal_record_repository.count(
                child_id=request.child_id,
                start_date=request.start_date,
                end_date=request.end_date,
                meal_type=MealType(request.meal_type) if request.meal_type else None,
            )

            return MealRecordListResponse(
                success=True, meal_records=[record.to_dict() for record in meal_records], total_count=total_count
            )

        except Exception as e:
            self.logger.error(f"❌ 食事記録検索エラー: {e}")
            return MealRecordListResponse(success=False, error=f"Failed to search meal records: {str(e)}")

    async def get_nutrition_summary(
        self, child_id: str, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> NutritionSummaryResponse:
        """栄養サマリー取得

        Args:
            child_id: 子どもID
            start_date: 開始日時
            end_date: 終了日時

        Returns:
            NutritionSummaryResponse: 栄養サマリー
        """
        try:
            self.logger.info(f"📊 栄養サマリー取得: child_id={child_id}")

            # デフォルト期間設定（過去7日間）
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=7)

            # 期間内の食事記録取得
            meal_records = await self.meal_record_repository.search(
                child_id=child_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000,  # 大きな値で全件取得
            )

            # 栄養サマリー計算
            summary = self._calculate_nutrition_summary(meal_records, start_date, end_date)

            self.logger.info(f"✅ 栄養サマリー計算完了: {len(meal_records)}件の記録")
            return NutritionSummaryResponse(success=True, summary=summary)

        except Exception as e:
            self.logger.error(f"❌ 栄養サマリー取得エラー: {e}")
            return NutritionSummaryResponse(success=False, error=f"Failed to get nutrition summary: {str(e)}")

    def _calculate_nutrition_summary(
        self, meal_records: list[MealRecord], start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """栄養サマリー計算

        Args:
            meal_records: 食事記録リスト
            start_date: 開始日時
            end_date: 終了日時

        Returns:
            dict: 栄養サマリー
        """
        total_records = len(meal_records)
        total_ai_records = sum(1 for record in meal_records if record.is_ai_detected)

        # 食事タイプ別集計
        meal_type_counts = {}
        for meal_type in MealType:
            meal_type_counts[meal_type.value] = sum(1 for record in meal_records if record.meal_type == meal_type)

        # 栄養バランススコア平均
        nutrition_scores = [record.total_nutrition_score for record in meal_records if record.total_nutrition_score > 0]
        avg_nutrition_score = sum(nutrition_scores) / len(nutrition_scores) if nutrition_scores else 0.0

        # よく食べる食材
        all_foods = []
        for record in meal_records:
            all_foods.extend(record.detected_foods)

        food_counts = {}
        for food in all_foods:
            food_counts[food] = food_counts.get(food, 0) + 1

        top_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # 期間情報
        period_days = (end_date - start_date).days + 1

        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "days": period_days},
            "total_records": total_records,
            "ai_detected_records": total_ai_records,
            "manual_records": total_records - total_ai_records,
            "records_per_day": round(total_records / period_days, 2) if period_days > 0 else 0,
            "meal_type_distribution": meal_type_counts,
            "avg_nutrition_score": round(avg_nutrition_score, 2),
            "top_foods": [{"food": food, "count": count} for food, count in top_foods],
            "nutrition_trends": {
                "total_nutrition_records": len(nutrition_scores),
                "avg_daily_nutrition": round(avg_nutrition_score, 2),
            },
        }
