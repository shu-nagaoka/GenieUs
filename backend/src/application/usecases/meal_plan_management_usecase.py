"""食事プラン管理UseCase

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- 段階的エラーハンドリング
"""
import logging
from dataclasses import dataclass
from typing import Any

from src.application.interface.protocols.meal_plan_manager import MealPlanManagerProtocol
from src.domain.entities import MealPlan


@dataclass
class CreateMealPlanRequest:
    """食事プラン作成リクエスト"""

    user_id: str
    child_id: str | None
    week_start: str
    title: str
    description: str
    created_by: str
    meals: dict[str, Any]
    nutrition_goals: dict[str, Any] | None = None
    notes: str | None = None


@dataclass
class UpdateMealPlanRequest:
    """食事プラン更新リクエスト"""

    user_id: str
    plan_id: str
    title: str | None = None
    description: str | None = None
    meals: dict[str, Any] | None = None
    nutrition_goals: dict[str, Any] | None = None
    notes: str | None = None


@dataclass
class SearchMealPlansRequest:
    """食事プラン検索リクエスト"""

    user_id: str
    search_query: str | None = None
    created_by: str | None = None
    week_start: str | None = None


@dataclass
class MealPlanResponse:
    """食事プラン操作レスポンス"""

    success: bool
    plan_id: str | None = None
    meal_plan: MealPlan | None = None
    error_message: str | None = None


@dataclass
class MealPlanListResponse:
    """食事プランリストレスポンス"""

    success: bool
    meal_plans: list[MealPlan]
    total_count: int
    error_message: str | None = None


class MealPlanManagementUseCase:
    """食事プラン管理UseCase
    
    Agent中心アーキテクチャに準拠した技術的UseCase
    """

    def __init__(
        self,
        meal_plan_manager: MealPlanManagerProtocol,
        logger: logging.Logger,
    ):
        self.meal_plan_manager = meal_plan_manager
        self.logger = logger

    async def create_meal_plan(self, request: CreateMealPlanRequest) -> MealPlanResponse:
        """食事プランを作成"""
        self.logger.info(
            "食事プラン作成開始",
            extra={
                "user_id": request.user_id,
                "title": request.title,
                "week_start": request.week_start,
            },
        )

        try:
            # プランデータの準備
            plan_data = {
                "child_id": request.child_id,
                "week_start": request.week_start,
                "title": request.title,
                "description": request.description,
                "created_by": request.created_by,
                "meals": request.meals,
                "nutrition_goals": request.nutrition_goals,
                "notes": request.notes,
            }

            # プライマリ処理: プラン保存
            plan_id = await self.meal_plan_manager.save_meal_plan(request.user_id, plan_data)

            # 作成されたプランを取得
            meal_plan = await self.meal_plan_manager.get_meal_plan_by_id(request.user_id, plan_id)

            self.logger.info(
                "食事プラン作成完了",
                extra={
                    "user_id": request.user_id,
                    "plan_id": plan_id,
                    "title": request.title,
                },
            )

            return MealPlanResponse(
                success=True,
                plan_id=plan_id,
                meal_plan=meal_plan,
            )

        except ValueError as e:
            # バリデーションエラー
            self.logger.warning(
                "食事プラン作成バリデーションエラー",
                extra={
                    "user_id": request.user_id,
                    "error": str(e),
                },
            )
            return MealPlanResponse(
                success=False,
                error_message=f"入力データが無効です: {e!s}",
            )

        except Exception as e:
            # フォールバック処理
            self.logger.error(
                "食事プラン作成エラー",
                extra={
                    "user_id": request.user_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            return MealPlanResponse(
                success=False,
                error_message="食事プランの作成中にエラーが発生しました。",
            )

    async def get_meal_plan(self, user_id: str, plan_id: str) -> MealPlanResponse:
        """食事プランを取得"""
        self.logger.info(
            "食事プラン取得開始",
            extra={
                "user_id": user_id,
                "plan_id": plan_id,
            },
        )

        try:
            meal_plan = await self.meal_plan_manager.get_meal_plan_by_id(user_id, plan_id)

            if meal_plan is None:
                self.logger.warning(
                    "食事プラン未発見",
                    extra={
                        "user_id": user_id,
                        "plan_id": plan_id,
                    },
                )
                return MealPlanResponse(
                    success=False,
                    error_message="指定された食事プランが見つかりません。",
                )

            self.logger.info(
                "食事プラン取得完了",
                extra={
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "title": meal_plan.title,
                },
            )

            return MealPlanResponse(
                success=True,
                plan_id=plan_id,
                meal_plan=meal_plan,
            )

        except Exception as e:
            self.logger.error(
                "食事プラン取得エラー",
                extra={
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "error": str(e),
                },
            )
            return MealPlanResponse(
                success=False,
                error_message="食事プランの取得中にエラーが発生しました。",
            )

    async def update_meal_plan(self, request: UpdateMealPlanRequest) -> MealPlanResponse:
        """食事プランを更新"""
        self.logger.info(
            "食事プラン更新開始",
            extra={
                "user_id": request.user_id,
                "plan_id": request.plan_id,
            },
        )

        try:
            # 更新データの準備（Noneでない値のみ）
            update_data = {}
            if request.title is not None:
                update_data["title"] = request.title
            if request.description is not None:
                update_data["description"] = request.description
            if request.meals is not None:
                update_data["meals"] = request.meals
            if request.nutrition_goals is not None:
                update_data["nutrition_goals"] = request.nutrition_goals
            if request.notes is not None:
                update_data["notes"] = request.notes

            # プライマリ処理: プラン更新
            success = await self.meal_plan_manager.update_meal_plan(
                request.user_id,
                request.plan_id,
                update_data,
            )

            if not success:
                return MealPlanResponse(
                    success=False,
                    error_message="食事プランの更新に失敗しました。",
                )

            # 更新されたプランを取得
            meal_plan = await self.meal_plan_manager.get_meal_plan_by_id(
                request.user_id,
                request.plan_id,
            )

            self.logger.info(
                "食事プラン更新完了",
                extra={
                    "user_id": request.user_id,
                    "plan_id": request.plan_id,
                },
            )

            return MealPlanResponse(
                success=True,
                plan_id=request.plan_id,
                meal_plan=meal_plan,
            )

        except Exception as e:
            self.logger.error(
                "食事プラン更新エラー",
                extra={
                    "user_id": request.user_id,
                    "plan_id": request.plan_id,
                    "error": str(e),
                },
            )
            return MealPlanResponse(
                success=False,
                error_message="食事プランの更新中にエラーが発生しました。",
            )

    async def delete_meal_plan(self, user_id: str, plan_id: str) -> MealPlanResponse:
        """食事プランを削除"""
        self.logger.info(
            "食事プラン削除開始",
            extra={
                "user_id": user_id,
                "plan_id": plan_id,
            },
        )

        try:
            success = await self.meal_plan_manager.delete_meal_plan(user_id, plan_id)

            if not success:
                return MealPlanResponse(
                    success=False,
                    error_message="食事プランの削除に失敗しました。",
                )

            self.logger.info(
                "食事プラン削除完了",
                extra={
                    "user_id": user_id,
                    "plan_id": plan_id,
                },
            )

            return MealPlanResponse(success=True)

        except Exception as e:
            self.logger.error(
                "食事プラン削除エラー",
                extra={
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "error": str(e),
                },
            )
            return MealPlanResponse(
                success=False,
                error_message="食事プランの削除中にエラーが発生しました。",
            )

    async def search_meal_plans(self, request: SearchMealPlansRequest) -> MealPlanListResponse:
        """食事プランを検索"""
        self.logger.info(
            "食事プラン検索開始",
            extra={
                "user_id": request.user_id,
                "search_query": request.search_query,
                "created_by": request.created_by,
            },
        )

        try:
            # プライマリ処理: 検索実行
            if request.week_start:
                # 週指定検索
                meal_plans = await self.meal_plan_manager.get_meal_plans_by_week(
                    request.user_id,
                    request.week_start,
                )
            else:
                # 一般検索
                meal_plans = await self.meal_plan_manager.search_meal_plans(
                    request.user_id,
                    request.search_query,
                    request.created_by,
                )

            self.logger.info(
                "食事プラン検索完了",
                extra={
                    "user_id": request.user_id,
                    "result_count": len(meal_plans),
                },
            )

            return MealPlanListResponse(
                success=True,
                meal_plans=meal_plans,
                total_count=len(meal_plans),
            )

        except Exception as e:
            self.logger.error(
                "食事プラン検索エラー",
                extra={
                    "user_id": request.user_id,
                    "error": str(e),
                },
            )
            return MealPlanListResponse(
                success=False,
                meal_plans=[],
                total_count=0,
                error_message="食事プランの検索中にエラーが発生しました。",
            )

    async def get_user_meal_plans(self, user_id: str) -> MealPlanListResponse:
        """ユーザーの全食事プランを取得"""
        self.logger.info(
            "ユーザー食事プラン一覧取得開始",
            extra={"user_id": user_id},
        )

        try:
            meal_plans = await self.meal_plan_manager.get_meal_plans_by_user(user_id)

            self.logger.info(
                "ユーザー食事プラン一覧取得完了",
                extra={
                    "user_id": user_id,
                    "plan_count": len(meal_plans),
                },
            )

            return MealPlanListResponse(
                success=True,
                meal_plans=meal_plans,
                total_count=len(meal_plans),
            )

        except Exception as e:
            self.logger.error(
                "ユーザー食事プラン一覧取得エラー",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                },
            )
            return MealPlanListResponse(
                success=False,
                meal_plans=[],
                total_count=0,
                error_message="食事プラン一覧の取得中にエラーが発生しました。",
            )
