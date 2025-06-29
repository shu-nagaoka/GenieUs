/**
 * 食事プラン管理API
 * バックエンドAPI: /api/meal-plans
 */

import { API_BASE_URL } from '@/config/api'

// === Interfaces ===

export interface NutritionInfo {
  calories?: number
  protein?: number
  carbs?: number
  fat?: number
  fiber?: number
}

export interface PlannedMeal {
  id?: string
  title: string
  description: string
  ingredients: string[]
  estimated_nutrition?: NutritionInfo
  difficulty: 'easy' | 'medium' | 'hard'
  prep_time_minutes: number
  tags: string[]
  allergens?: string[]
  recipe_url?: string
}

export interface NutritionGoals {
  daily_calories: number
  daily_protein: number
  daily_carbs: number
  daily_fat: number
}

export interface MealPlan {
  id?: string
  user_id?: string
  child_id?: string
  week_start: string
  title: string
  description: string
  created_by: 'user' | 'genie'
  meals: {
    [day: string]: {
      breakfast?: PlannedMeal
      lunch?: PlannedMeal
      dinner?: PlannedMeal
      snack?: PlannedMeal
    }
  }
  nutrition_goals?: NutritionGoals
  notes?: string
  created_at?: string
  updated_at?: string
}

export interface CreateMealPlanRequest {
  child_id?: string
  week_start: string
  title: string
  description?: string
  created_by: 'user' | 'genie'
  meals: object
  nutrition_goals?: NutritionGoals
  notes?: string
}

export interface UpdateMealPlanRequest {
  title?: string
  description?: string
  meals?: object
  nutrition_goals?: NutritionGoals
  notes?: string
}

export interface SearchMealPlansRequest {
  search_query?: string
  created_by?: 'user' | 'genie'
  week_start?: string
}

// === API Response Types ===

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface MealPlanCreateResponse {
  success: boolean
  plan_id?: string
  meal_plan?: MealPlan
  message: string
}

export interface MealPlanListResponse {
  meal_plans: MealPlan[]
  total_count: number
}

// === API Functions ===

/**
 * 食事プラン作成
 */
export async function createMealPlan(
  request: CreateMealPlanRequest,
  user_id: string = 'frontend_user'
): Promise<ApiResponse<MealPlanCreateResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans?user_id=${user_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'プラン作成に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Create meal plan error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事プラン作成に失敗しました',
    }
  }
}

/**
 * 食事プラン取得
 */
export async function getMealPlan(
  plan_id: string,
  user_id: string = 'frontend_user'
): Promise<ApiResponse<MealPlan>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans/${plan_id}?user_id=${user_id}`)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事プランの取得に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Get meal plan error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事プランの取得に失敗しました',
    }
  }
}

/**
 * 食事プラン更新
 */
export async function updateMealPlan(
  plan_id: string,
  request: UpdateMealPlanRequest,
  user_id: string = 'frontend_user'
): Promise<ApiResponse<MealPlan>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans/${plan_id}?user_id=${user_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事プランの更新に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Update meal plan error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事プランの更新に失敗しました',
    }
  }
}

/**
 * 食事プラン削除
 */
export async function deleteMealPlan(
  plan_id: string,
  user_id: string = 'frontend_user'
): Promise<ApiResponse<void>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans/${plan_id}?user_id=${user_id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事プランの削除に失敗しました')
    }

    return { success: true, message: '食事プランを削除しました' }
  } catch (error) {
    console.error('Delete meal plan error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事プランの削除に失敗しました',
    }
  }
}

/**
 * ユーザーの食事プラン一覧取得
 */
export async function getMealPlans(
  user_id: string = 'frontend_user'
): Promise<ApiResponse<MealPlanListResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans?user_id=${user_id}`)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事プラン一覧の取得に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Get meal plans error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事プラン一覧の取得に失敗しました',
    }
  }
}

/**
 * 食事プラン検索
 */
export async function searchMealPlans(
  request: SearchMealPlansRequest,
  user_id: string = 'frontend_user'
): Promise<ApiResponse<MealPlanListResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/meal-plans/search?user_id=${user_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '食事プランの検索に失敗しました')
    }

    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    console.error('Search meal plans error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : '食事プランの検索に失敗しました',
    }
  }
}
