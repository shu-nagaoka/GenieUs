"""食事プラン管理API

コーディング規約準拠:
- Import文ファイル先頭配置
- 型アノテーション完備
- FastAPI Depends統合パターン
- 段階的エラーハンドリング
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.application.usecases.meal_plan_management_usecase import (
    CreateMealPlanRequest,
    MealPlanManagementUseCase,
    SearchMealPlansRequest,
    UpdateMealPlanRequest,
)
from src.presentation.api.dependencies import get_meal_plan_management_usecase

# === Pydantic Models ===

class NutritionInfoRequest(BaseModel):
    """栄養情報リクエストモデル"""

    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    fiber: float | None = None


class PlannedMealRequest(BaseModel):
    """個別食事プランリクエストモデル"""

    id: str | None = None
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    ingredients: list[str] = Field(default_factory=list)
    estimated_nutrition: NutritionInfoRequest | None = None
    difficulty: str = Field(default="easy", pattern="^(easy|medium|hard)$")
    prep_time_minutes: int = Field(default=10, ge=0, le=300)
    tags: list[str] = Field(default_factory=list)
    allergens: list[str] = Field(default_factory=list)
    recipe_url: str | None = None


class DayMealPlanRequest(BaseModel):
    """1日分食事プランリクエストモデル"""

    breakfast: PlannedMealRequest | None = None
    lunch: PlannedMealRequest | None = None
    dinner: PlannedMealRequest | None = None
    snack: PlannedMealRequest | None = None


class NutritionGoalsRequest(BaseModel):
    """栄養目標リクエストモデル"""

    daily_calories: float = Field(default=300.0, ge=0)
    daily_protein: float = Field(default=15.0, ge=0)
    daily_carbs: float = Field(default=45.0, ge=0)
    daily_fat: float = Field(default=8.0, ge=0)


class CreateMealPlanRequestModel(BaseModel):
    """食事プラン作成リクエストモデル"""

    child_id: str | None = None
    week_start: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    created_by: str = Field(default="user", pattern="^(user|genie)$")
    meals: dict = Field(default_factory=dict)
    nutrition_goals: NutritionGoalsRequest | None = None
    notes: str | None = None


class UpdateMealPlanRequestModel(BaseModel):
    """食事プラン更新リクエストモデル"""

    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    meals: dict | None = None
    nutrition_goals: NutritionGoalsRequest | None = None
    notes: str | None = None


class SearchMealPlansRequestModel(BaseModel):
    """食事プラン検索リクエストモデル"""

    search_query: str | None = Field(None, max_length=100)
    created_by: str | None = Field(None, pattern="^(user|genie)$")
    week_start: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")


# === Response Models ===

class NutritionInfoResponse(BaseModel):
    """栄養情報レスポンスモデル"""

    calories: float | None
    protein: float | None
    carbs: float | None
    fat: float | None
    fiber: float | None


class PlannedMealResponse(BaseModel):
    """個別食事プランレスポンスモデル"""

    id: str
    title: str
    description: str
    ingredients: list[str]
    estimated_nutrition: NutritionInfoResponse | None
    difficulty: str
    prep_time_minutes: int
    tags: list[str]
    allergens: list[str]
    recipe_url: str | None


class DayMealPlanResponse(BaseModel):
    """1日分食事プランレスポンスモデル"""

    breakfast: PlannedMealResponse | None
    lunch: PlannedMealResponse | None
    dinner: PlannedMealResponse | None
    snack: PlannedMealResponse | None


class NutritionGoalsResponse(BaseModel):
    """栄養目標レスポンスモデル"""

    daily_calories: float
    daily_protein: float
    daily_carbs: float
    daily_fat: float


class MealPlanResponse(BaseModel):
    """食事プランレスポンスモデル"""

    id: str
    user_id: str
    child_id: str | None
    week_start: str
    title: str
    description: str
    created_by: str
    meals: dict
    nutrition_goals: NutritionGoalsResponse | None
    notes: str | None
    created_at: str
    updated_at: str


class MealPlanListResponse(BaseModel):
    """食事プランリストレスポンスモデル"""

    meal_plans: list[MealPlanResponse]
    total_count: int


class MealPlanCreateResponse(BaseModel):
    """食事プラン作成レスポンスモデル"""

    success: bool
    plan_id: str | None
    meal_plan: MealPlanResponse | None
    message: str


# === Router ===

router = APIRouter()


@router.post("/meal-plans", response_model=MealPlanCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_plan(
    request: CreateMealPlanRequestModel,
    user_id: str = "test_user",  # TODO: 認証システムと統合
    usecase: MealPlanManagementUseCase = Depends(get_meal_plan_management_usecase),
) -> MealPlanCreateResponse:
    """食事プランを作成"""
    # リクエスト変換
    create_request = CreateMealPlanRequest(
        user_id=user_id,
        child_id=request.child_id,
        week_start=request.week_start,
        title=request.title,
        description=request.description,
        created_by=request.created_by,
        meals=request.meals,
        nutrition_goals=request.nutrition_goals.dict() if request.nutrition_goals else None,
        notes=request.notes,
    )

    # UseCase実行
    response = await usecase.create_meal_plan(create_request)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.error_message or "食事プランの作成に失敗しました",
        )

    # レスポンス変換
    meal_plan_data = None
    if response.meal_plan:
        meal_plan_dict = response.meal_plan.to_dict()
        meal_plan_data = MealPlanResponse(**meal_plan_dict)

    return MealPlanCreateResponse(
        success=True,
        plan_id=response.plan_id,
        meal_plan=meal_plan_data,
        message="食事プランを作成しました",
    )


@router.get("/meal-plans/{plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    plan_id: str,
    user_id: str = "test_user",  # TODO: 認証システムと統合
    usecase: MealPlanManagementUseCase = Depends(get_meal_plan_management_usecase),
) -> MealPlanResponse:
    """食事プランを取得"""
    response = await usecase.get_meal_plan(user_id, plan_id)

    if not response.success or not response.meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response.error_message or "食事プランが見つかりません",
        )

    meal_plan_dict = response.meal_plan.to_dict()
    return MealPlanResponse(**meal_plan_dict)


@router.put("/meal-plans/{plan_id}", response_model=MealPlanResponse)
async def update_meal_plan(
    plan_id: str,
    request: UpdateMealPlanRequestModel,
    user_id: str = "test_user",  # TODO: 認証システムと統合
    usecase: MealPlanManagementUseCase = Depends(get_meal_plan_management_usecase),
) -> MealPlanResponse:
    """食事プランを更新"""
    # リクエスト変換
    update_request = UpdateMealPlanRequest(
        user_id=user_id,
        plan_id=plan_id,
        title=request.title,
        description=request.description,
        meals=request.meals,
        nutrition_goals=request.nutrition_goals.dict() if request.nutrition_goals else None,
        notes=request.notes,
    )

    response = await usecase.update_meal_plan(update_request)

    if not response.success or not response.meal_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.error_message or "食事プランの更新に失敗しました",
        )

    meal_plan_dict = response.meal_plan.to_dict()
    return MealPlanResponse(**meal_plan_dict)


@router.delete("/meal-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_plan(
    plan_id: str,
    user_id: str = "test_user",  # TODO: 認証システムと統合
    usecase: MealPlanManagementUseCase = Depends(get_meal_plan_management_usecase),
):
    """食事プランを削除"""
    response = await usecase.delete_meal_plan(user_id, plan_id)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response.error_message or "食事プランが見つかりません",
        )


@router.get("/meal-plans", response_model=MealPlanListResponse)
async def list_meal_plans(
    user_id: str = "test_user",  # TODO: 認証システムと統合
    usecase: MealPlanManagementUseCase = Depends(get_meal_plan_management_usecase),
) -> MealPlanListResponse:
    """ユーザーの食事プラン一覧を取得"""
    response = await usecase.get_user_meal_plans(user_id)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.error_message or "食事プラン一覧の取得に失敗しました",
        )

    meal_plans_data = []
    for meal_plan in response.meal_plans:
        meal_plan_dict = meal_plan.to_dict()
        meal_plans_data.append(MealPlanResponse(**meal_plan_dict))

    return MealPlanListResponse(
        meal_plans=meal_plans_data,
        total_count=response.total_count,
    )


@router.post("/meal-plans/search", response_model=MealPlanListResponse)
async def search_meal_plans(
    request: SearchMealPlansRequestModel,
    user_id: str = "test_user",  # TODO: 認証システムと統合
    usecase: MealPlanManagementUseCase = Depends(get_meal_plan_management_usecase),
) -> MealPlanListResponse:
    """食事プランを検索"""
    # リクエスト変換
    search_request = SearchMealPlansRequest(
        user_id=user_id,
        search_query=request.search_query,
        created_by=request.created_by,
        week_start=request.week_start,
    )

    response = await usecase.search_meal_plans(search_request)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.error_message or "食事プランの検索に失敗しました",
        )

    meal_plans_data = []
    for meal_plan in response.meal_plans:
        meal_plan_dict = meal_plan.to_dict()
        meal_plans_data.append(MealPlanResponse(**meal_plan_dict))

    return MealPlanListResponse(
        meal_plans=meal_plans_data,
        total_count=response.total_count,
    )
