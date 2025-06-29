"""食事プラン管理ツール - ADK FunctionTool版

ADKと統合された食事プラン管理機能
"""

import logging
from typing import Any

from google.adk.tools import FunctionTool
from src.application.usecases.meal_plan_management_usecase import (
    CreateMealPlanRequest,
    MealPlanManagementUseCase,
    SearchMealPlansRequest,
    UpdateMealPlanRequest,
)


def create_meal_plan_tool(meal_plan_usecase: MealPlanManagementUseCase, logger: logging.Logger) -> FunctionTool:
    """ADK FunctionTool形式の食事プラン管理ツールを作成"""

    async def manage_meal_plans(
        action: str,
        user_id: str,
        child_id: str = None,
        week_start: str = None,
        title: str = None,
        description: str = None,
        meals: dict = None,
        nutrition_goals: dict = None,
        notes: str = None,
        plan_id: str = None,
        start_date: str = None,
        end_date: str = None,
        **kwargs
    ) -> dict[str, Any]:
        """食事プラン管理機能の統合エントリーポイント
        
        Args:
            action: 実行するアクション ("create", "get", "update", "delete", "search")
            user_id: ユーザーID
            child_id: お子さんのID (create/update時)
            week_start: 週の開始日 YYYY-MM-DD形式 (create時)
            title: プランのタイトル (create/update時)
            description: プランの説明 (create/update時)
            meals: 食事データ (create/update時)
            nutrition_goals: 栄養目標 (create/update時)
            notes: メモ (create/update時)
            plan_id: プランID (get/update/delete時)
            start_date: 検索開始日 (search時)
            end_date: 検索終了日 (search時)
        """
        try:
            logger.info(f"🍽️ 食事プラン管理ツール実行: {action} (user_id: {user_id})")
            
            if action == "create":
                return await _create_meal_plan(
                    meal_plan_usecase, logger, user_id, child_id, week_start,
                    title, description, meals, nutrition_goals, notes
                )
            elif action == "get":
                return await _get_meal_plan(
                    meal_plan_usecase, logger, user_id, plan_id
                )
            elif action == "update":
                return await _update_meal_plan(
                    meal_plan_usecase, logger, user_id, plan_id, title,
                    description, meals, nutrition_goals, notes
                )
            elif action == "delete":
                return await _delete_meal_plan(
                    meal_plan_usecase, logger, user_id, plan_id
                )
            elif action == "search":
                return await _search_meal_plans(
                    meal_plan_usecase, logger, user_id, start_date, end_date
                )
            else:
                raise ValueError(f"未対応のアクション: {action}")
                
        except Exception as e:
            error_msg = f"食事プラン管理エラー ({action}): {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "details": str(e)
            }

    # FunctionToolとして返す
    return FunctionTool(
        func=manage_meal_plans,
    )


async def _create_meal_plan(
    meal_plan_usecase: MealPlanManagementUseCase,
    logger: logging.Logger,
    user_id: str,
    child_id: str,
    week_start: str,
    title: str,
    description: str,
    meals: dict,
    nutrition_goals: dict,
    notes: str
) -> dict[str, Any]:
    """食事プラン作成"""
    if not title or not week_start:
        return {
            "success": False,
            "error": "タイトルと週開始日は必須です"
        }
    
    if not meals:
        meals = {}
    
    request = CreateMealPlanRequest(
        user_id=user_id,
        child_id=child_id,
        week_start=week_start,
        title=title,
        description=description or "",
        created_by="genie",  # AI作成として記録
        meals=meals,
        nutrition_goals=nutrition_goals,
        notes=notes
    )
    
    response = await meal_plan_usecase.create_meal_plan(request)
    
    if response.success:
        return {
            "success": True,
            "message": "食事プランを作成しました",
            "plan_id": response.meal_plan.id if response.meal_plan else None,
            "plan": response.meal_plan.to_dict() if response.meal_plan else None
        }
    else:
        return {
            "success": False,
            "error": response.error_message or "食事プランの作成に失敗しました"
        }


async def _get_meal_plan(
    meal_plan_usecase: MealPlanManagementUseCase,
    logger: logging.Logger,
    user_id: str,
    plan_id: str
) -> dict[str, Any]:
    """特定の食事プラン取得"""
    if not plan_id:
        return {
            "success": False,
            "error": "プランIDは必須です"
        }
    
    response = await meal_plan_usecase.get_meal_plan(user_id, plan_id)
    
    if response.success:
        return {
            "success": True,
            "plan": response.meal_plan.to_dict() if response.meal_plan else None
        }
    else:
        return {
            "success": False,
            "error": response.error_message or "食事プランの取得に失敗しました"
        }


async def _update_meal_plan(
    meal_plan_usecase: MealPlanManagementUseCase,
    logger: logging.Logger,
    user_id: str,
    plan_id: str,
    title: str,
    description: str,
    meals: dict,
    nutrition_goals: dict,
    notes: str
) -> dict[str, Any]:
    """食事プラン更新"""
    if not plan_id:
        return {
            "success": False,
            "error": "プランIDは必須です"
        }
    
    request = UpdateMealPlanRequest(
        user_id=user_id,
        plan_id=plan_id,
        title=title,
        description=description,
        meals=meals,
        nutrition_goals=nutrition_goals,
        notes=notes
    )
    
    response = await meal_plan_usecase.update_meal_plan(request)
    
    if response.success:
        return {
            "success": True,
            "message": "食事プランを更新しました",
            "plan": response.meal_plan.to_dict() if response.meal_plan else None
        }
    else:
        return {
            "success": False,
            "error": response.error_message or "食事プランの更新に失敗しました"
        }


async def _delete_meal_plan(
    meal_plan_usecase: MealPlanManagementUseCase,
    logger: logging.Logger,
    user_id: str,
    plan_id: str
) -> dict[str, Any]:
    """食事プラン削除"""
    if not plan_id:
        return {
            "success": False,
            "error": "プランIDは必須です"
        }
    
    response = await meal_plan_usecase.delete_meal_plan(user_id, plan_id)
    
    if response.success:
        return {
            "success": True,
            "message": "食事プランを削除しました"
        }
    else:
        return {
            "success": False,
            "error": response.error_message or "食事プランの削除に失敗しました"
        }


async def _search_meal_plans(
    meal_plan_usecase: MealPlanManagementUseCase,
    logger: logging.Logger,
    user_id: str,
    start_date: str,
    end_date: str
) -> dict[str, Any]:
    """食事プラン検索"""
    request = SearchMealPlansRequest(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    response = await meal_plan_usecase.search_meal_plans(request)
    
    if response.success:
        plans_data = []
        for plan in response.meal_plans:
            plans_data.append(plan.to_dict())
        
        return {
            "success": True,
            "plans": plans_data,
            "total_count": response.total_count,
            "period": f"{start_date or '開始'} から {end_date or '終了'}"
        }
    else:
        return {
            "success": False,
            "error": response.error_message or "食事プラン検索に失敗しました"
        }