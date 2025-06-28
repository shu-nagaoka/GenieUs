"""食事プラン管理ツール - Genius Agents統合

Agentsが食事プランの作成・編集・削除・提案を行えるツール
"""

import logging
from typing import Any

from google.ai.generativelanguage_v1beta.types import FunctionDeclaration, Schema, Type

from src.application.usecases.meal_plan_management_usecase import (
    CreateMealPlanRequest,
    MealPlanManagementUseCase,
    UpdateMealPlanRequest,
)


class MealPlanTool:
    """食事プラン管理ツール

    Genius Agentsが食事プランの作成、編集、削除、検索を行うためのツール
    """

    def __init__(
        self,
        meal_plan_usecase: MealPlanManagementUseCase,
        logger: logging.Logger,
    ):
        self.meal_plan_usecase = meal_plan_usecase
        self.logger = logger

    def get_function_declarations(self) -> list[FunctionDeclaration]:
        """食事プラン管理用のFunctionDeclarationを取得"""
        return [
            # 食事プラン作成
            FunctionDeclaration(
                name="create_meal_plan",
                description="新しい食事プランを作成します。栄養バランスを考慮した1週間のメニューを提案・作成できます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "child_id": Schema(type=Type.STRING, description="お子さんのID（任意）"),
                        "week_start": Schema(type=Type.STRING, description="週の開始日（YYYY-MM-DD形式）"),
                        "title": Schema(type=Type.STRING, description="食事プランのタイトル"),
                        "description": Schema(type=Type.STRING, description="食事プランの説明"),
                        "nutrition_goals": Schema(
                            type=Type.OBJECT,
                            description="1日の栄養目標",
                            properties={
                                "daily_calories": Schema(type=Type.NUMBER, description="1日のカロリー目標"),
                                "daily_protein": Schema(type=Type.NUMBER, description="1日のタンパク質目標(g)"),
                                "daily_carbs": Schema(type=Type.NUMBER, description="1日の炭水化物目標(g)"),
                                "daily_fat": Schema(type=Type.NUMBER, description="1日の脂質目標(g)"),
                            },
                        ),
                        "notes": Schema(type=Type.STRING, description="メモ・注意点"),
                    },
                    required=["user_id", "week_start", "title", "description"],
                ),
            ),
            # 食事プラン取得
            FunctionDeclaration(
                name="get_meal_plans",
                description="ユーザーの食事プラン一覧を取得します。既存のプランを確認できます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                    },
                    required=["user_id"],
                ),
            ),
            # 食事プラン更新
            FunctionDeclaration(
                name="update_meal_plan",
                description="既存の食事プランを更新します。メニューの追加・変更・栄養バランス調整ができます。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "plan_id": Schema(type=Type.STRING, description="更新する食事プランのID"),
                        "title": Schema(type=Type.STRING, description="新しいタイトル（任意）"),
                        "description": Schema(type=Type.STRING, description="新しい説明（任意）"),
                        "meals": Schema(
                            type=Type.OBJECT,
                            description="1週間分の食事メニュー（任意）",
                        ),
                        "nutrition_goals": Schema(
                            type=Type.OBJECT,
                            description="栄養目標の更新（任意）",
                        ),
                        "notes": Schema(type=Type.STRING, description="メモの更新（任意）"),
                    },
                    required=["user_id", "plan_id"],
                ),
            ),
            # 食事プラン削除
            FunctionDeclaration(
                name="delete_meal_plan",
                description="不要になった食事プランを削除します。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "plan_id": Schema(type=Type.STRING, description="削除する食事プランのID"),
                    },
                    required=["user_id", "plan_id"],
                ),
            ),
            # AI食事プラン提案
            FunctionDeclaration(
                name="suggest_meal_plan",
                description="お子さんの年齢・好み・アレルギー情報に基づいて、最適な食事プランを提案します。",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "user_id": Schema(type=Type.STRING, description="ユーザーID"),
                        "child_age_months": Schema(type=Type.NUMBER, description="お子さんの月齢"),
                        "preferences": Schema(
                            type=Type.ARRAY,
                            description="好きな食材・料理",
                            items=Schema(type=Type.STRING),
                        ),
                        "dislikes": Schema(
                            type=Type.ARRAY,
                            description="苦手な食材・料理",
                            items=Schema(type=Type.STRING),
                        ),
                        "allergies": Schema(
                            type=Type.ARRAY,
                            description="アレルギー食材",
                            items=Schema(type=Type.STRING),
                        ),
                        "dietary_restrictions": Schema(
                            type=Type.ARRAY,
                            description="食事制限",
                            items=Schema(type=Type.STRING),
                        ),
                    },
                    required=["user_id", "child_age_months"],
                ),
            ),
        ]

    async def execute_function(self, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """食事プラン管理関数を実行"""
        try:
            self.logger.info(f"食事プランツール実行: {function_name} with args: {arguments}")

            if function_name == "create_meal_plan":
                return await self._create_meal_plan(arguments)
            elif function_name == "get_meal_plans":
                return await self._get_meal_plans(arguments)
            elif function_name == "update_meal_plan":
                return await self._update_meal_plan(arguments)
            elif function_name == "delete_meal_plan":
                return await self._delete_meal_plan(arguments)
            elif function_name == "suggest_meal_plan":
                return await self._suggest_meal_plan(arguments)
            else:
                raise ValueError(f"未知の関数: {function_name}")

        except Exception as e:
            error_msg = f"食事プランツールエラー ({function_name}): {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "details": str(e),
            }

    async def _create_meal_plan(self, args: dict[str, Any]) -> dict[str, Any]:
        """食事プラン作成"""
        request = CreateMealPlanRequest(
            user_id=args["user_id"],
            child_id=args.get("child_id"),
            week_start=args["week_start"],
            title=args["title"],
            description=args["description"],
            created_by="genie",  # AI作成として記録
            meals={},  # 初期は空、後から追加
            nutrition_goals=args.get("nutrition_goals"),
            notes=args.get("notes"),
        )

        response = await self.meal_plan_usecase.create_meal_plan(request)

        if response.success:
            return {
                "success": True,
                "message": "食事プランを作成しました",
                "plan_id": response.plan_id,
                "meal_plan": response.meal_plan.to_dict() if response.meal_plan else None,
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "食事プランの作成に失敗しました",
            }

    async def _get_meal_plans(self, args: dict[str, Any]) -> dict[str, Any]:
        """食事プラン一覧取得"""
        response = await self.meal_plan_usecase.get_user_meal_plans(args["user_id"])

        if response.success:
            meal_plans_data = []
            for plan in response.meal_plans:
                meal_plans_data.append(plan.to_dict())

            return {
                "success": True,
                "meal_plans": meal_plans_data,
                "total_count": response.total_count,
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "食事プラン一覧の取得に失敗しました",
            }

    async def _update_meal_plan(self, args: dict[str, Any]) -> dict[str, Any]:
        """食事プラン更新"""
        request = UpdateMealPlanRequest(
            user_id=args["user_id"],
            plan_id=args["plan_id"],
            title=args.get("title"),
            description=args.get("description"),
            meals=args.get("meals"),
            nutrition_goals=args.get("nutrition_goals"),
            notes=args.get("notes"),
        )

        response = await self.meal_plan_usecase.update_meal_plan(request)

        if response.success:
            return {
                "success": True,
                "message": "食事プランを更新しました",
                "meal_plan": response.meal_plan.to_dict() if response.meal_plan else None,
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "食事プランの更新に失敗しました",
            }

    async def _delete_meal_plan(self, args: dict[str, Any]) -> dict[str, Any]:
        """食事プラン削除"""
        response = await self.meal_plan_usecase.delete_meal_plan(
            args["user_id"],
            args["plan_id"],
        )

        if response.success:
            return {
                "success": True,
                "message": "食事プランを削除しました",
            }
        else:
            return {
                "success": False,
                "error": response.error_message or "食事プランの削除に失敗しました",
            }

    async def _suggest_meal_plan(self, args: dict[str, Any]) -> dict[str, Any]:
        """AI食事プラン提案"""
        child_age_months = args["child_age_months"]
        preferences = args.get("preferences", [])
        dislikes = args.get("dislikes", [])
        allergies = args.get("allergies", [])
        dietary_restrictions = args.get("dietary_restrictions", [])

        # 月齢に応じた食事提案ロジック
        if child_age_months < 6:
            suggestion = {
                "recommendation": "まだ離乳食開始前です。母乳・ミルクのみで十分です。",
                "next_steps": "生後5-6ヶ月頃から離乳食の準備を始めましょう。",
            }
        elif child_age_months < 9:
            suggestion = {
                "recommendation": "離乳食初期・中期です。ペースト状の食事から始めましょう。",
                "meal_suggestions": {
                    "breakfast": "10倍粥、野菜ペースト",
                    "lunch": "白身魚ペースト、にんじんペースト",
                    "dinner": "豆腐ペースト、かぼちゃペースト",
                },
                "avoid_foods": ["蜂蜜", "生もの", "卵白", "牛乳"] + allergies,
            }
        elif child_age_months < 18:
            suggestion = {
                "recommendation": "離乳食後期・完了期です。手づかみ食べも始めましょう。",
                "meal_suggestions": {
                    "breakfast": "軟飯、味噌汁、果物",
                    "lunch": "ハンバーグ、野菜炒め、軟飯",
                    "dinner": "魚の煮付け、野菜の煮物、軟飯",
                },
                "hand_foods": ["おにぎり", "蒸しパン", "茹で野菜スティック"],
                "avoid_foods": ["蜂蜜", "生もの", "硬いもの"] + allergies,
            }
        else:
            suggestion = {
                "recommendation": "幼児食です。大人とほぼ同じものが食べられます。",
                "meal_suggestions": {
                    "breakfast": "ご飯、味噌汁、卵料理、野菜",
                    "lunch": "主菜、副菜、ご飯、汁物",
                    "dinner": "主菜、副菜2品、ご飯、汁物",
                },
                "avoid_foods": ["生もの", "硬いナッツ類"] + allergies,
            }

        # アレルギー対応の注意喚起
        if allergies:
            suggestion["allergy_warning"] = f"アレルギー食材（{', '.join(allergies)}）を避けた食事を提案しています。"

        # 好み・苦手の考慮
        if preferences:
            suggestion["preferences_note"] = f"好きな食材（{', '.join(preferences)}）を積極的に取り入れましょう。"

        if dislikes:
            suggestion["dislikes_note"] = f"苦手な食材（{', '.join(dislikes)}）は他の食材で栄養を補いましょう。"

        return {
            "success": True,
            "child_age_months": child_age_months,
            "suggestion": suggestion,
            "message": "月齢に応じた食事プランを提案しました",
        }
