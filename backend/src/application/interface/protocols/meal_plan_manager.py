"""食事プラン管理用プロトコル

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- 技術的機能のみ（ビジネスロジック排除）
"""
from typing import Any, Protocol

from src.domain.entities import MealPlan


class MealPlanManagerProtocol(Protocol):
    """食事プラン管理の技術的プロトコル
    
    Agent中心アーキテクチャに準拠し、技術的操作のみを定義
    """

    async def save_meal_plan(self, user_id: str, plan_data: dict[str, Any]) -> str:
        """食事プランを保存
        
        Args:
            user_id: ユーザーID
            plan_data: プランデータ（技術的データ構造）
            
        Returns:
            保存されたプランID

        """
        ...

    async def get_meal_plan_by_id(self, user_id: str, plan_id: str) -> MealPlan | None:
        """IDで食事プランを取得
        
        Args:
            user_id: ユーザーID
            plan_id: プランID
            
        Returns:
            食事プランエンティティ（存在しない場合はNone）

        """
        ...

    async def get_meal_plans_by_user(self, user_id: str) -> list[MealPlan]:
        """ユーザーの全食事プランを取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            食事プランエンティティのリスト

        """
        ...

    async def get_meal_plans_by_week(self, user_id: str, week_start: str) -> list[MealPlan]:
        """指定週の食事プランを取得
        
        Args:
            user_id: ユーザーID
            week_start: 週開始日（YYYY-MM-DD）
            
        Returns:
            食事プランエンティティのリスト

        """
        ...

    async def update_meal_plan(self, user_id: str, plan_id: str, plan_data: dict[str, Any]) -> bool:
        """食事プランを更新
        
        Args:
            user_id: ユーザーID
            plan_id: プランID
            plan_data: 更新データ（技術的データ構造）
            
        Returns:
            更新成功フラグ

        """
        ...

    async def delete_meal_plan(self, user_id: str, plan_id: str) -> bool:
        """食事プランを削除
        
        Args:
            user_id: ユーザーID
            plan_id: プランID
            
        Returns:
            削除成功フラグ

        """
        ...

    async def search_meal_plans(
        self,
        user_id: str,
        search_query: str | None = None,
        created_by: str | None = None,
    ) -> list[MealPlan]:
        """食事プランを検索
        
        Args:
            user_id: ユーザーID
            search_query: 検索クエリ（タイトル・説明対象）
            created_by: 作成者フィルター（"user" or "genie"）
            
        Returns:
            検索結果の食事プランエンティティリスト

        """
        ...
