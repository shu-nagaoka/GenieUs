"""食事プラン管理アダプター（インメモリ実装）

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- DI注入パターン
- Infrastructure層での技術的実装のみ
"""
import logging
from datetime import datetime
from typing import Any

from src.domain.entities import MealPlan


class InMemoryMealPlanManager:
    """インメモリ食事プラン管理アダプター
    
    技術的なデータ永続化操作のみを担当
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # ユーザーごとの食事プラン格納（user_id -> Dict[plan_id, MealPlan]）
        self._meal_plans: dict[str, dict[str, MealPlan]] = {}

    async def save_meal_plan(self, user_id: str, plan_data: dict[str, Any]) -> str:
        """食事プランを保存"""
        self.logger.info(
            "食事プラン保存開始",
            extra={
                "user_id": user_id,
                "title": plan_data.get("title", ""),
            },
        )

        try:
            # エンティティ作成
            meal_plan = MealPlan.from_dict(user_id, plan_data)

            # ユーザー領域初期化（必要な場合）
            if user_id not in self._meal_plans:
                self._meal_plans[user_id] = {}

            # プラン保存
            self._meal_plans[user_id][meal_plan.id] = meal_plan

            self.logger.info(
                "食事プラン保存完了",
                extra={
                    "user_id": user_id,
                    "plan_id": meal_plan.id,
                    "title": meal_plan.title,
                },
            )

            return meal_plan.id

        except Exception as e:
            self.logger.error(
                "食事プラン保存エラー",
                extra={
                    "user_id": user_id,
                    "error": str(e),
                    "plan_data": plan_data,
                },
            )
            raise

    async def get_meal_plan_by_id(self, user_id: str, plan_id: str) -> MealPlan | None:
        """IDで食事プランを取得"""
        self.logger.debug(
            "食事プラン取得",
            extra={
                "user_id": user_id,
                "plan_id": plan_id,
            },
        )

        user_plans = self._meal_plans.get(user_id, {})
        return user_plans.get(plan_id)

    async def get_meal_plans_by_user(self, user_id: str) -> list[MealPlan]:
        """ユーザーの全食事プランを取得"""
        self.logger.debug(
            "ユーザー食事プラン一覧取得",
            extra={"user_id": user_id},
        )

        user_plans = self._meal_plans.get(user_id, {})
        plans = list(user_plans.values())

        # 作成日時でソート（新しい順）
        plans.sort(key=lambda p: p.created_at, reverse=True)

        return plans

    async def get_meal_plans_by_week(self, user_id: str, week_start: str) -> list[MealPlan]:
        """指定週の食事プランを取得"""
        self.logger.debug(
            "週指定食事プラン取得",
            extra={
                "user_id": user_id,
                "week_start": week_start,
            },
        )

        user_plans = self._meal_plans.get(user_id, {})
        matching_plans = []

        for plan in user_plans.values():
            if plan.week_start == week_start:
                matching_plans.append(plan)

        # 作成日時でソート（新しい順）
        matching_plans.sort(key=lambda p: p.created_at, reverse=True)

        return matching_plans

    async def update_meal_plan(self, user_id: str, plan_id: str, plan_data: dict[str, Any]) -> bool:
        """食事プランを更新"""
        self.logger.info(
            "食事プラン更新開始",
            extra={
                "user_id": user_id,
                "plan_id": plan_id,
            },
        )

        try:
            user_plans = self._meal_plans.get(user_id, {})

            if plan_id not in user_plans:
                self.logger.warning(
                    "更新対象食事プラン未発見",
                    extra={
                        "user_id": user_id,
                        "plan_id": plan_id,
                    },
                )
                return False

            existing_plan = user_plans[plan_id]

            # 更新データの適用
            if "title" in plan_data:
                existing_plan.title = plan_data["title"]
            if "description" in plan_data:
                existing_plan.description = plan_data["description"]
            if "meals" in plan_data:
                # meals データの完全置換
                new_plan_data = existing_plan.to_dict()
                new_plan_data["meals"] = plan_data["meals"]
                updated_plan = MealPlan.from_dict(user_id, new_plan_data)
                updated_plan.id = plan_id  # IDを保持
                self._meal_plans[user_id][plan_id] = updated_plan
            if "nutrition_goals" in plan_data:
                # 栄養目標の更新処理
                new_plan_data = existing_plan.to_dict()
                new_plan_data["nutrition_goals"] = plan_data["nutrition_goals"]
                updated_plan = MealPlan.from_dict(user_id, new_plan_data)
                updated_plan.id = plan_id
                self._meal_plans[user_id][plan_id] = updated_plan
            if "notes" in plan_data:
                existing_plan.notes = plan_data["notes"]

            # 更新日時を更新
            existing_plan.updated_at = datetime.now()

            self.logger.info(
                "食事プラン更新完了",
                extra={
                    "user_id": user_id,
                    "plan_id": plan_id,
                },
            )

            return True

        except Exception as e:
            self.logger.error(
                "食事プラン更新エラー",
                extra={
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "error": str(e),
                },
            )
            raise

    async def delete_meal_plan(self, user_id: str, plan_id: str) -> bool:
        """食事プランを削除"""
        self.logger.info(
            "食事プラン削除開始",
            extra={
                "user_id": user_id,
                "plan_id": plan_id,
            },
        )

        user_plans = self._meal_plans.get(user_id, {})

        if plan_id not in user_plans:
            self.logger.warning(
                "削除対象食事プラン未発見",
                extra={
                    "user_id": user_id,
                    "plan_id": plan_id,
                },
            )
            return False

        del user_plans[plan_id]

        self.logger.info(
            "食事プラン削除完了",
            extra={
                "user_id": user_id,
                "plan_id": plan_id,
            },
        )

        return True

    async def search_meal_plans(
        self,
        user_id: str,
        search_query: str | None = None,
        created_by: str | None = None,
    ) -> list[MealPlan]:
        """食事プランを検索"""
        self.logger.debug(
            "食事プラン検索",
            extra={
                "user_id": user_id,
                "search_query": search_query,
                "created_by": created_by,
            },
        )

        user_plans = self._meal_plans.get(user_id, {})
        matching_plans = []

        for plan in user_plans.values():
            # created_by フィルター
            if created_by and plan.created_by.value != created_by:
                continue

            # 検索クエリフィルター
            if search_query:
                query_lower = search_query.lower()
                if (query_lower not in plan.title.lower() and
                    query_lower not in plan.description.lower()):
                    continue

            matching_plans.append(plan)

        # 作成日時でソート（新しい順）
        matching_plans.sort(key=lambda p: p.created_at, reverse=True)

        return matching_plans
